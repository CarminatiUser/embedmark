from copy import deepcopy
import json
from pathlib import Path

import pytest

from translator.cli import main
from translator.config import TranslationConfig
from translator.diagnostics import TranslationError
from translator.fonts import FontCatalog
from translator.main import UITranslator

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples/fonts/fontes.json"


def test_portuguese_catalog_and_config_roundtrip():
    catalog = FontCatalog.load(MANIFEST)
    config = TranslationConfig(font_catalog=catalog, strict=True)
    assert TranslationConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
    result = UITranslator(config).translate((ROOT / "examples/05_interacao.html").read_text())
    assert not result.diagnostics
    assert {font["symbol"] for font in result.fonts} == {"tcc_font_pt_14", "tcc_font_pt_20", "tcc_font_pt_24"}
    assert all(font["source"].endswith(".c") for font in result.to_dict()["fonts"])
    assert "LV_FONT_DECLARE(tcc_font_pt_14);" in result.code
    assert "#if !LV_FONT_MONTSERRAT_" not in result.code


def test_unknown_glyph_still_fails_strict_mode():
    config = TranslationConfig(font_catalog=FontCatalog.load(MANIFEST), strict=True)
    with pytest.raises(TranslationError) as error:
        UITranslator(config).translate("<screen><label>😊</label></screen>")
    assert any(d.code == "font.glyphs" for d in error.value.diagnostics)


def test_coverage_checked_for_the_selected_size():
    data = json.loads(MANIFEST.read_text())
    data["fonts"][0]["ranges"] = [[32, 126]]
    config = TranslationConfig(font_catalog=FontCatalog(data))
    result = UITranslator(config).translate('<screen width="172" height="320"><label>Ação</label></screen>')
    assert any(d.code == "font.glyphs" and "tcc_font_pt_14" in d.message for d in result.diagnostics)
    assert config.font_catalog.select(17)["size"] == 20


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d.update(schema_version=True),
        lambda d: d.update(fonts=[]),
        lambda d: d["fonts"][0].update(symbol="tcc_font_x);system(0)"),
        lambda d: d["fonts"][0].update(source="../escape.c"),
        lambda d: d["fonts"][0].update(size=True),
        lambda d: d["fonts"][0].update(ranges=[[100, 20]]),
        lambda d: d["fonts"][0].update(ranges=[[0xD800, 0xDFFF]]),
        lambda d: d["fonts"].append(deepcopy(d["fonts"][0])),
        lambda d: d["fonts"][0].update(metadata=float("nan")),
        lambda d: d["fonts"][0].update(metadata="\ud800"),
    ],
)
def test_invalid_catalog_rejected(change):
    data = json.loads(MANIFEST.read_text())
    change(data)
    with pytest.raises(ValueError):
        FontCatalog(data)


def test_cli_manifest_and_diagnostic_on_bad_file(tmp_path, capsys):
    source = ROOT / "examples/05_interacao.html"
    output = tmp_path / "ui_generated.c"
    assert main([str(source), "--font-manifest", str(MANIFEST), "--strict", "-o", str(output)]) == 0
    before = output.read_bytes()
    assert main([str(source), "--font-manifest", str(tmp_path / "missing.json"), "-o", str(output)]) == 1
    assert output.read_bytes() == before
    assert "catálogo de fontes" in capsys.readouterr().err
