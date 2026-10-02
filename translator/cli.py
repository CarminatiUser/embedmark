"""Interface de terminal e contrato de diagnósticos para integrações."""

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translator import __version__
from translator.config import TranslationConfig, DisplayPresets
from translator.diagnostics import Diagnostic, TranslationError
from translator.fonts import FontCatalog
from translator.html_parser import HTMLParser
from translator.main import UITranslator, atomic_write_many


def report(diagnostics, mode):
    if mode == "json":
        print(json.dumps([d.to_dict() for d in diagnostics], ensure_ascii=False), file=sys.stderr)
    else:
        for d in diagnostics:
            location = f"{d.line}:{d.column or 1}: " if d.line is not None else ""
            print(f"{location}{d.severity} [{d.code}]: {d.message}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Traduz interfaces HTML/CSS simplificadas para LVGL 8.3.")
    parser.add_argument("input", nargs="?", help="Arquivo HTML de entrada")
    parser.add_argument("-o", "--output", default="output/ui_generated.c", help="Arquivo C de saída")
    parser.add_argument("-d", "--display", choices=DisplayPresets.DISPLAYS, default="st7789")
    parser.add_argument("--orientation", choices=["portrait", "landscape"], default="portrait")
    parser.add_argument("-w", "--width", type=int, help="Sobrescreve largura de projeto do HTML")
    parser.add_argument("-H", "--height", type=int, help="Sobrescreve altura de projeto do HTML")
    parser.add_argument("--display-width", type=int, help="Largura do display custom antes da orientação")
    parser.add_argument("--display-height", type=int, help="Altura do display custom antes da orientação")
    parser.add_argument("--font-manifest", help="Catálogo JSON de fontes C externas e cobertura Unicode")
    parser.add_argument("-q", "--quiet", action="store_true", help="Oculta mensagens de sucesso; mantém diagnósticos")
    parser.add_argument("--analyze", action="store_true", help="Conta objetos, estilos e bytes do texto gerado")
    parser.add_argument("--check-perf", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--export-json", help="Exporta árvore, estilos, layout e diagnósticos")
    parser.add_argument("--validate", action="store_true", help="Valida sem gravar código")
    parser.add_argument("--strict", action="store_true", help="Considera avisos como falha")
    parser.add_argument("--diagnostics-format", choices=["text", "json"], default="text")
    parser.add_argument("--list-displays", action="store_true")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    if args.list_displays:
        for name, description in DisplayPresets.list_displays().items():
            print(f"{name}: {description}")
        return 0
    if not args.input:
        parser.error("Informe o arquivo de entrada ou --list-displays.")
    try:
        if args.check_perf:
            raise ValueError("--check-perf foi retirado: desempenho exige medição no firmware.")
        config = TranslationConfig(
            design_width=args.width,
            design_height=args.height,
            display_preset=args.display,
            orientation=args.orientation,
            verbose=not args.quiet,
            display_width=args.display_width,
            display_height=args.display_height,
            strict=args.strict,
            font_catalog=FontCatalog.load(args.font_manifest) if args.font_manifest else None,
        )
        source, output = Path(args.input), Path(args.output)
        targets = [] if args.validate else [output, output.with_suffix(".h")]
        if args.export_json:
            targets.append(Path(args.export_json))
        resolved = [p.resolve() for p in targets]
        if source.resolve() in resolved or len(resolved) != len(set(resolved)):
            raise ValueError("Entrada, saída C, header e JSON devem ter caminhos distintos.")
        if not args.validate and output.suffix != ".c":
            raise ValueError("O arquivo de saída deve ter extensão .c.")
        result = UITranslator(config).translate(source.read_text(encoding="utf-8"))
        contents = {}
        if not args.validate:
            contents[output.with_suffix(".h")] = result.header
            contents[output] = result.code
        if args.export_json:
            contents[Path(args.export_json)] = json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n"
        atomic_write_many(contents)
        if result.diagnostics or args.diagnostics_format == "json":
            report(result.diagnostics, args.diagnostics_format)
        if not args.quiet:
            print("Validação concluída." if args.validate else f"Gerados: {output} e {output.with_suffix('.h')}")
            if args.analyze:
                print(
                    f"Objetos: {1 + len(HTMLParser.flatten_elements(result.computed_layout))}; "
                    f"estilos: {result.code.count('static lv_style_t')}; "
                    f"texto C: {len(result.code.encode('utf-8'))} bytes (não representa memória do firmware)."
                )
        return 0
    except TranslationError as exc:
        report(exc.diagnostics, args.diagnostics_format)
        return 1
    except (OSError, ValueError) as exc:
        report([Diagnostic("error", "cli.failure", str(exc))], args.diagnostics_format)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
