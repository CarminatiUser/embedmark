"""Prepara o exemplo de integração sem sobrescrever um controlador modificado."""

import argparse
from pathlib import Path
import sys

from translator.config import TranslationConfig
from translator.fonts import FontCatalog
from translator.main import UITranslator, atomic_write_many

ROOT = Path(__file__).resolve().parents[1]


def prepare(destination):
    destination = Path(destination)
    assets = sorted((ROOT / "examples/firmware").iterdir()) + sorted((ROOT / "examples/fonts").iterdir())
    assets = [path for path in assets if path.is_file() and path.suffix in {".c", ".h", ".json", ".txt", ".cmake"}]
    html = ROOT / "examples/05_interacao.html"
    inputs = {path.resolve() for path in [html, *assets]}
    config = TranslationConfig(font_catalog=FontCatalog.load(ROOT / "examples/fonts/fontes.json"), strict=True)
    result = UITranslator(config).translate(html.read_text(encoding="utf-8"))
    contents = {path.name: path.read_text(encoding="utf-8") for path in assets}
    contents.update({"ui_generated.c": result.code, "ui_generated.h": result.header})
    for name, content in contents.items():
        target = destination / name
        if target.resolve() in inputs:
            raise ValueError("O diretório de saída não pode substituir arquivos dos exemplos.")
        if (
            name in {"ui_controller.c", "ui_controller.h"}
            and target.exists()
            and target.read_text(encoding="utf-8") != content
        ):
            raise ValueError(f"Controlador modificado preservado: {target}. Escolha outro diretório de saída.")
    atomic_write_many({destination / name: content for name, content in contents.items()})
    return destination


def main():
    parser = argparse.ArgumentParser(description="Prepara o exemplo de contador em português para integração.")
    parser.add_argument("--output", default="output/interacao")
    args = parser.parse_args()
    try:
        print(f"Exemplo preparado em {prepare(args.output)}")
    except (OSError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
