"""API do tradutor: uma execução produz código, layout e diagnósticos."""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import sys
import tempfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bs4 import BeautifulSoup

from translator.config import TranslationConfig
from translator.css_parser import CSSParser
from translator.diagnostics import Diagnostic, TranslationError
from translator.html_parser import HTMLParser
from translator.layout_engine import LayoutEngine, ViewportConfig
from translator.lvgl_generator import LVGLCodeGenerator


@dataclass
class TranslationResult:
    code: str
    header: str
    ast: dict
    styles: dict
    computed_layout: list
    diagnostics: list[Diagnostic]
    display: dict
    fonts: list[dict] = field(default_factory=list)

    def to_dict(self):
        return {
            "schema_version": 1,
            "design": {k: self.ast[k] for k in ("width", "height")},
            "display": self.display,
            "elements": self.ast["elements"],
            "styles": self.styles,
            "computed_layout": self.computed_layout,
            "fonts": self.fonts,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
        }


def atomic_write(path, content):
    atomic_write_many({path: content})


def atomic_write_many(contents):
    """Prepara todas as saídas e restaura as anteriores em falha de gravação.

    Cada substituição é atômica. A transação entre arquivos protege contra
    erros de E/S reportados, mas não promete atomicidade em quedas de energia.
    """
    targets = [Path(path) for path in contents]
    if len({path.resolve() for path in targets}) != len(targets):
        raise ValueError("Arquivos de saída devem ter caminhos distintos.")
    staged, backups, installed = {}, {}, []
    try:
        for path, content in zip(targets, contents.values()):
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(f"A saída deve ser um arquivo regular, sem link simbólico: {path}.")
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
            ) as stream:
                staged[path] = Path(stream.name)
                stream.write(content)
            if path.exists():
                staged[path].chmod(path.stat().st_mode & 0o777)
        for path in targets:
            if path.exists():
                with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
                    backup = Path(stream.name)
                try:
                    os.replace(path, backup)
                except OSError:
                    backup.unlink(missing_ok=True)
                    raise
                backups[path] = backup
            os.replace(staged[path], path)
            installed.append(path)
    except (OSError, ValueError) as original_error:
        restoration_errors = []
        for path in reversed(targets):
            try:
                if path in backups:
                    # Se a restauração falhar, preserva o backup para recuperação.
                    os.replace(backups[path], path)
                    del backups[path]
                elif path in installed:
                    path.unlink(missing_ok=True)
            except OSError:
                restoration_errors.append(
                    f"Não foi possível restaurar {path}; original salvo em {backups[path]}."
                    if path in backups
                    else f"Não foi possível remover a saída incompleta {path}."
                )
        if restoration_errors:
            raise OSError(" ".join(restoration_errors)) from original_error
        raise
    else:
        for backup in backups.values():
            backup.unlink(missing_ok=True)
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def extract_css(html):
    """Mantém linhas/colunas do HTML para os diagnósticos tinycss2."""
    soup = BeautifulSoup(html, "html.parser")
    offsets = [0, *[match.end() for match in re.finditer("\n", html)]]
    masked = ["\n" if c == "\n" else " " for c in html]
    for tag in soup.find_all("style"):
        start_tag = offsets[tag.sourceline - 1] + tag.sourcepos
        # '>' dentro de um atributo entre aspas não encerra a tag.
        opening = re.match(r"<style\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>", html[start_tag:], re.I)
        if opening is None:
            continue
        start = start_tag + opening.end()
        text = tag.string or ""
        masked[start : start + len(text)] = text
    return "".join(masked)


class UITranslator:
    def __init__(self, config=None):
        self.config = config or TranslationConfig()
        self.last_result = None

    def translate(self, html_text):
        self.last_result = None
        if not isinstance(html_text, str):
            raise TranslationError([Diagnostic("error", "html.source", "O conteúdo HTML deve ser texto.", 1, 1)])
        if "\0" in html_text:
            prefix = html_text.split("\0", 1)[0]
            raise TranslationError(
                [
                    Diagnostic(
                        "error",
                        "html.nul",
                        "O conteúdo HTML não pode conter NUL.",
                        prefix.count("\n") + 1,
                        len(prefix.rsplit("\n", 1)[-1]) + 1,
                    )
                ]
            )
        try:
            html_text.encode("utf-8")
        except UnicodeEncodeError as exc:
            prefix = html_text[: exc.start]
            raise TranslationError(
                [
                    Diagnostic(
                        "error",
                        "html.encoding",
                        "O conteúdo contém Unicode inválido.",
                        prefix.count("\n") + 1,
                        len(prefix.rsplit("\n", 1)[-1]) + 1,
                    )
                ]
            ) from exc
        diagnostics = []
        ast = HTMLParser.parse(html_text, diagnostics)
        if self.config.design_width is not None:
            ast["width"] = self.config.design_width
        if self.config.design_height is not None:
            ast["height"] = self.config.design_height
        css_locations = {}
        styles = CSSParser.parse_stylesheet(extract_css(html_text), diagnostics, locations=css_locations)
        ids = {element["id"] for element in HTMLParser.flatten_elements(ast["elements"])}
        for element_id in styles:
            if element_id not in ids:
                diagnostics.append(
                    Diagnostic(
                        "warning",
                        "css.unmatched_id",
                        f"Seletor #{element_id} não corresponde a um componente renderizável.",
                        *css_locations.get(element_id, (1, 1)),
                        element_id=element_id,
                    )
                )
        viewport = ViewportConfig(ast["width"], ast["height"], self.config.display_width, self.config.display_height)
        try:
            computed = LayoutEngine(viewport, self.config.font_catalog).compute_all_layouts(ast["elements"], styles)
            generator = LVGLCodeGenerator(
                self.config.display_width, self.config.display_height, self.config.font_catalog
            )
            code = generator.generate_complete_code(computed, ast)
        except ValueError as exc:
            diagnostics.append(
                Diagnostic(
                    "error",
                    "translation.value",
                    str(exc),
                    getattr(exc, "line", 1),
                    getattr(exc, "column", 1),
                    getattr(exc, "element_id", None),
                )
            )
            raise TranslationError(diagnostics) from exc
        for element in HTMLParser.flatten_elements(computed):
            if element["type"] != "label":
                continue
            symbol = element["computed"]["font"]
            missing = self.config.font_catalog.missing_characters(symbol, element.get("text", ""))
            if missing:
                diagnostics.append(
                    Diagnostic(
                        "warning",
                        "font.glyphs",
                        f"Caracteres ausentes da cobertura declarada de {symbol}: "
                        + " ".join(f"U+{ord(c):04X}" for c in missing)
                        + ". O texto UTF-8 foi preservado; use uma fonte com esses caracteres.",
                        element.get("line", 1),
                        element.get("column", 1),
                        element_id=element.get("id"),
                    )
                )
        if self.config.strict and diagnostics:
            diagnostics.append(
                Diagnostic("error", "translation.strict", "Modo estrito: corrija os avisos antes de gerar.", 1, 1)
            )
            raise TranslationError(diagnostics)
        result = TranslationResult(
            code,
            generator.generate_header(),
            ast,
            styles,
            computed,
            diagnostics,
            {"width": self.config.display_width, "height": self.config.display_height},
            sorted(
                (self.config.font_catalog.describe(symbol) for symbol in generator.used_fonts),
                key=lambda item: item["size"],
            ),
        )
        self.last_result = result
        return result

    def translate_html(self, html_text):
        return self.translate(html_text).code

    def translate_file(self, html_path, output_path):
        """Interface compatível: False em erros; arquivos existentes ficam intactos se a tradução falhar."""
        self.last_result = None
        try:
            source = Path(html_path)
            output = Path(output_path)
            targets = [output] if self.config.output_format == "json" else [output, output.with_suffix(".h")]
            if self.config.enable_debug_output:
                targets.append(output.with_suffix(".debug.json"))
            if source.resolve() in {p.resolve() for p in targets}:
                raise ValueError("A saída não pode substituir o arquivo de entrada.")
            if self.config.output_format == "c" and output.suffix != ".c":
                raise ValueError("Saída de código deve ter extensão .c.")
            result = self.translate(source.read_text(encoding="utf-8"))
            if self.config.output_format == "json":
                contents = {output: json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n"}
            else:
                contents = {output.with_suffix(".h"): result.header, output: result.code}
            if self.config.enable_debug_output:
                contents[output.with_suffix(".debug.json")] = (
                    json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n"
                )
            atomic_write_many(contents)
            for diagnostic in result.diagnostics:
                print(f"[{diagnostic.code}] {diagnostic.message}", file=sys.stderr)
            if self.config.verbose:
                print(f"Arquivo gerado: {output}")
            return True
        except (OSError, ValueError) as exc:
            print(f"Erro: {exc}", file=sys.stderr)
            return False


def main():
    from translator.cli import main as cli_main

    args = sys.argv[1:]
    if not args:
        base = Path(__file__).resolve().parent
        args = [str(base / "sample_ui.html"), "-o", str(base.parent / "output/ui_generated.c")]
    return cli_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
