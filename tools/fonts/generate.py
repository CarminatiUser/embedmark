"""Reproduz as fontes do exemplo; requer npm ci em tools/fonts."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = ROOT / "examples/fonts"
SIZES = (14, 20, 24)
EXTRA = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇºª°•"


def generate():
    converter = HERE / "node_modules/lv_font_conv/lv_font_conv.js"
    if not converter.is_file():
        raise SystemExit("Execute npm ci --prefix tools/fonts antes de gerar as fontes.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    entries = []
    ranges = [[32, 126], *[[code, code] for code in sorted(set(map(ord, EXTRA)))]]
    for size in SIZES:
        symbol = f"embedmark_sans_pt_{size}"
        destination = OUTPUT / f"{symbol}.c"
        subprocess.run(
            [
                "node",
                str(converter),
                "--font",
                "Montserrat-Medium.ttf",
                "--range",
                "0x20-0x7e",
                "--symbols",
                EXTRA,
                "--size",
                str(size),
                "--format",
                "lvgl",
                "--bpp",
                "4",
                "--no-compress",
                "--no-prefilter",
                "--lv-include",
                "lvgl.h",
                "-o",
                str(destination),
            ],
            cwd=HERE,
            check=True,
        )
        source = destination.read_text().replace(str(destination), f"{symbol}.c")
        destination.write_text(
            "/* EmbedMark Sans PT: derivada de Montserrat Medium 7.200.\n"
            " * Copyright 2011 The Montserrat Project Authors.\n"
            " * SIL Open Font License 1.1; veja OFL.txt distribuído junto. */\n" + source
        )
        entries.append({"size": size, "symbol": symbol, "source": destination.name, "ranges": ranges})
    (OUTPUT / "fontes.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "EmbedMark Sans PT",
                "fonts": entries,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    shutil.copyfile(HERE / "OFL.txt", OUTPUT / "OFL.txt")
    print("Fontes geradas. SHA-256 do TTF:", hashlib.sha256((HERE / "Montserrat-Medium.ttf").read_bytes()).hexdigest())


if __name__ == "__main__":
    generate()
