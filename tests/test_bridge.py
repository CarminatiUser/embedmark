"""Contrato usado pelo processo isolado da extensão VS Code."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from translator import __version__
from translator.bridge import process_request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '<screen width="172" height="320"><label id="x">Teste</label></screen>'


def request(**changes):
    return {"protocol": 1, "action": "generate", "source": SOURCE, **changes}


def run_bridge(raw, cwd):
    return subprocess.run(
        [sys.executable, "-m", "translator.bridge"],
        input=raw,
        cwd=cwd,
        capture_output=True,
        timeout=15,
    )


def test_generate_and_validate_share_result_without_writing(tmp_path):
    generated = run_bridge(json.dumps(request()).encode(), tmp_path)
    assert generated.returncode == 0, generated.stderr
    assert generated.stderr == b""
    data = json.loads(generated.stdout)
    assert data["protocol"] == 1 and data["ok"] and data["version"] == __version__ == "0.4.0"
    assert "screen_main_create" in data["code"] and "screen_main_destroy" in data["header"]
    validated = process_request(request(action="validate"))
    assert validated["result"] == data["result"]
    assert "code" not in validated and "header" not in validated
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "bad_request",
    [
        [],
        None,
        {},
        request(protocol=True),
        request(protocol=2),
        request(action="compile"),
        request(action=[]),
        request(source=17),
        request(config=[]),
        request(config=None),
        request(unexpected=True),
        request(config={"display_preset": []}),
        request(config={"design_width": False}),
        request(config={"strict": "false"}),
        request(config={"debug": True}),
        request(config={"font_manifest": 1}),
        request(config={"font_manifest": ""}),
    ],
)
def test_invalid_protocol_or_config_returns_structured_error(bad_request):
    data = process_request(bad_request)
    assert data["ok"] is False
    assert data["diagnostics"][0]["code"] == "bridge.request"
    assert "code" not in data and "header" not in data


@pytest.mark.parametrize(
    "raw",
    [
        b"not json",
        b"{} {}",
        b"\xff",
        b'{"protocol":NaN}',
        b'{"protocol":1,"protocol":1}',
    ],
)
def test_malformed_json_is_one_response_and_nonzero(raw, tmp_path):
    completed = run_bridge(raw, tmp_path)
    assert completed.returncode == 1
    assert completed.stderr == b""
    assert json.loads(completed.stdout)["diagnostics"][0]["code"] == "bridge.json"


def test_strict_default_has_editor_locations_and_can_be_disabled():
    source = SOURCE + "\n<style>\n#x { font-weight: bold; }\n</style>"
    strict = process_request(request(source=source))
    assert not strict["ok"]
    warning = next(d for d in strict["diagnostics"] if d["code"] == "css.unsupported")
    assert (warning["line"], warning["column"]) == (3, 6)
    assert "code" not in strict
    relaxed = process_request(request(source=source, config={"strict": False}))
    assert relaxed["ok"] and relaxed["diagnostics"]


def test_portuguese_font_manifest_exposes_only_used_font_sources():
    response = process_request(
        request(
            source='<screen width="172" height="320">\n  <label>Ação</label></screen>',
            config={"font_manifest": str(ROOT / "examples/fonts/fontes.json")},
        )
    )
    assert response["ok"] and not response["diagnostics"]
    assert len(response["fonts"]) == 1
    assert response["fonts"][0]["source"] == "tcc_font_pt_14.c"


def test_glyph_warning_points_to_label_and_invalid_unicode_is_structured():
    response = process_request(request(source="<screen>\n  <label>Ação</label></screen>"))
    warning = next(d for d in response["diagnostics"] if d["code"] == "font.glyphs")
    assert (warning["line"], warning["column"]) == (2, 3)
    response = process_request(request(source="<screen>\n<label>\ud800</label></screen>"))
    assert not response["ok"]
    assert response["diagnostics"][0]["code"] == "html.encoding"


def test_request_size_limit(tmp_path):
    completed = run_bridge(b" " * (8 * 1024 * 1024 + 1), tmp_path)
    assert completed.returncode == 1
    assert json.loads(completed.stdout)["diagnostics"][0]["code"] == "bridge.limit"


def test_nonfinite_font_metadata_is_a_structured_failure(tmp_path):
    data = json.loads((ROOT / "examples/fonts/fontes.json").read_text())
    data["fonts"][0]["metadata"] = float("nan")
    manifest = tmp_path / "fonts.json"
    manifest.write_text(json.dumps(data))
    completed = run_bridge(json.dumps(request(config={"font_manifest": str(manifest)})).encode(), tmp_path)
    assert completed.returncode == 1 and completed.stderr == b""
    assert json.loads(completed.stdout)["diagnostics"][0]["code"] == "bridge.request"
