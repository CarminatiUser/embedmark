"""Executa uma aplicação com LVGL real e display em memória, sem placa física."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shlex
import subprocess

import pytest

from translator.config import TranslationConfig
from translator.fonts import FontCatalog
from translator.main import UITranslator

ROOT = Path(__file__).resolve().parents[1]


def test_lifecycle_events_and_portuguese_fonts_with_real_lvgl(tmp_path):
    compiler, lvgl = os.environ.get("HOST_CC"), os.environ.get("LVGL_DIR")
    if not compiler or not lvgl:
        pytest.skip("Defina HOST_CC com compilador nativo e LVGL_DIR para executar o LVGL real.")
    lvgl = Path(lvgl)
    flags = [
        "-std=c99",
        "-DLV_CONF_SKIP",
        "-DLV_MEM_SIZE=1048576",
        "-DLV_USE_ASSERT_MEM_INTEGRITY=1",
        "-I",
        str(lvgl),
        "-I",
        str(tmp_path),
        "-I",
        str(ROOT / "examples/firmware"),
        *shlex.split(os.environ.get("HOST_CFLAGS", "")),
    ]
    config = TranslationConfig(font_catalog=FontCatalog.load(ROOT / "examples/fonts/fontes.json"), strict=True)
    result = UITranslator(config).translate((ROOT / "examples/05_interacao.html").read_text())
    (tmp_path / "ui_generated.c").write_text(result.code)
    (tmp_path / "ui_generated.h").write_text(result.header)

    # Confere cada glifo declarado contra as tabelas reais das três fontes.
    manifest = json.loads((ROOT / "examples/fonts/fontes.json").read_text())
    glyph_checks = ["static void verify_font_coverage(void) {", "lv_font_glyph_dsc_t glyph;"]
    for font in manifest["fonts"]:
        for low, high in font["ranges"]:
            glyph_checks.append(
                f"for (uint32_t cp = {low}; cp <= {high}; ++cp) "
                f"assert(lv_font_get_glyph_dsc(&{font['symbol']}, &glyph, cp, 0));"
            )
    glyph_checks.append("}")
    harness = (ROOT / "tests/runtime/lifecycle.c").read_text()
    harness = harness.replace("int main(void)", "\n".join(glyph_checks) + "\nint main(void)")
    harness = harness.replace("    lv_init();", "    lv_init();\n    verify_font_coverage();")
    (tmp_path / "lifecycle.c").write_text(harness)

    sources = [
        *sorted((lvgl / "src").rglob("*.c")),
        *sorted((ROOT / "examples/fonts").glob("*.c")),
        ROOT / "examples/firmware/ui_controller.c",
        tmp_path / "ui_generated.c",
        tmp_path / "lifecycle.c",
    ]
    assert len(sources) > 10, "Fontes LVGL não encontradas"

    def compile_one(item):
        index, source = item
        obj = tmp_path / f"object_{index}.o"
        command = [compiler, *flags, "-c", str(source), "-o", str(obj)]
        # Warnings do LVGL de terceiros não são tratados como erros do produto.
        if not source.is_relative_to(lvgl):
            command += ["-Wall", "-Wextra", "-Werror"]
        compiled = subprocess.run(command, capture_output=True, text=True)
        assert compiled.returncode == 0, f"{source}:\n{compiled.stderr}"
        return str(obj)

    with ThreadPoolExecutor(max_workers=4) as workers:
        objects = list(workers.map(compile_one, enumerate(sources)))
    executable = tmp_path / "lifecycle"
    linked = subprocess.run(
        [
            compiler,
            *shlex.split(os.environ.get("HOST_CFLAGS", "")),
            *shlex.split(os.environ.get("HOST_LDFLAGS", "")),
            *objects,
            "-lm",
            "-o",
            str(executable),
        ],
        capture_output=True,
        text=True,
    )
    assert linked.returncode == 0, linked.stderr
    executed = subprocess.run([str(executable)], capture_output=True, text=True, timeout=30)
    assert executed.returncode == 0, executed.stdout + executed.stderr
    assert "100 ciclos aprovados" in executed.stdout
