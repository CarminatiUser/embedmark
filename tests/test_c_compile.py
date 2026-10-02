"""Compila contra headers reais do LVGL, sem um mock de suas APIs."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest

from translator.config import LVGL_COORD_MAX
from translator.config import TranslationConfig
from translator.fonts import FontCatalog
from translator.layout_engine import FontMapper
from translator.main import UITranslator

ROOT = Path(__file__).resolve().parents[1]


def compile_c(code, tmp_path, *, fonts=True):
    lvgl = os.environ.get("LVGL_DIR")
    compiler = os.environ.get("CC") or shutil.which("clang") or shutil.which("cc")
    if not lvgl or not compiler:
        pytest.skip("Defina LVGL_DIR com LVGL 8.3.x e disponibilize um compilador C.")
    source = tmp_path / "generated.c"
    source.write_text(code)
    flags = [f"-DLV_FONT_MONTSERRAT_{n}=1" for n in FontMapper.FONT_MAP] if fonts else []
    return subprocess.run(
        [
            compiler,
            "-std=c99",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-DLV_CONF_SKIP",
            *flags,
            "-I",
            lvgl,
            "-c",
            str(source),
            "-o",
            str(tmp_path / "generated.o"),
        ],
        text=True,
        capture_output=True,
    )


@pytest.mark.parametrize(
    "name",
    [
        "translator/sample_ui.html",
        "translator/advanced_example.html",
        "examples/01_minima.html",
        "examples/02_espacamento.html",
        "examples/03_hierarquia.html",
    ],
)
def test_examples_compile_with_real_lvgl(name, tmp_path):
    result = UITranslator().translate((ROOT / name).read_text())
    completed = compile_c(result.code, tmp_path)
    assert completed.returncode == 0, completed.stderr


def test_adversarial_names_text_and_anonymous_nodes_compile(tmp_path):
    html = '<screen><div><label id="1bad">aspas &quot; ação</label><button id="scr">go</button></div>'
    html += '<label id="a-b">x</label><label id="a_b">y</label><label id="for">z</label></screen>'
    completed = compile_c(UITranslator().translate_html(html), tmp_path)
    assert completed.returncode == 0, completed.stderr


def test_coordinate_limit_matches_default_lvgl(tmp_path):
    code = f"""#include "lvgl.h"
#if LV_COORD_MAX != {LVGL_COORD_MAX}
#error "Limite de coordenadas divergente do LVGL"
#endif
"""
    completed = compile_c(code, tmp_path)
    assert completed.returncode == 0, completed.stderr


@pytest.mark.parametrize("html", ["<screen/>", '<screen id="raiz"/>', "<screen><label>Sem ID</label></screen>"])
def test_registry_without_component_ids_compiles(html, tmp_path):
    result = compile_c(UITranslator().translate(html).code, tmp_path)
    assert result.returncode == 0, result.stderr


def test_interactive_example_with_custom_fonts_compiles(tmp_path):
    config = TranslationConfig(font_catalog=FontCatalog.load(ROOT / "examples/fonts/fontes.json"), strict=True)
    code = UITranslator(config).translate((ROOT / "examples/05_interacao.html").read_text()).code
    result = compile_c(code, tmp_path, fonts=False)
    assert result.returncode == 0, result.stderr


def test_missing_font_produces_actionable_build_error(tmp_path):
    html = '<screen width="172" height="320"><label id="x">x</label></screen><style>#x {font-size:48}</style>'
    completed = compile_c(UITranslator().translate_html(html), tmp_path, fonts=False)
    assert completed.returncode != 0
    assert "Habilite LV_FONT_MONTSERRAT_48" in completed.stderr


def test_c99_trigraphs_in_user_text_cannot_change_generated_code(tmp_path):
    html = '<screen><label id="??/">??/ ??= ??( ??) ??! ??&lt; ??&gt; ??-</label></screen>'
    code = UITranslator().translate_html(html)
    assert "??" not in code
    assert r"\?\?/" in code
    completed = compile_c(code, tmp_path)
    assert completed.returncode == 0, completed.stderr
