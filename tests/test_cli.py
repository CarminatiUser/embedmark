import json
import subprocess
import sys
from pathlib import Path

import pytest

from translator.cli import main
from translator.config import TranslationConfig
from translator.main import UITranslator
from translator.main import atomic_write_many


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "entrada com espaços.html"
    path.write_text('<screen><label id="x">Teste</label></screen><style>#x {width:50}</style>', encoding="utf-8")
    return path


def test_list_displays_needs_no_input(capsys):
    assert main(["--list-displays"]) == 0
    assert "st7789" in capsys.readouterr().out


def test_quiet_output_and_real_json_layout(source, tmp_path, capsys):
    output, data = tmp_path / "saída com espaço.c", tmp_path / "nested/result.json"
    assert main([str(source), "-o", str(output), "--quiet", "--export-json", str(data)]) == 0
    assert capsys.readouterr().out == ""
    assert output.with_suffix(".h").exists()
    result = json.loads(data.read_text())
    assert result["computed_layout"][0]["computed"]["width"] == 35
    assert result["schema_version"] == 1


def test_failed_translation_preserves_existing_outputs(source, tmp_path, capsys):
    output, header, data = tmp_path / "out.c", tmp_path / "out.h", tmp_path / "out.json"
    for p in [output, header, data]:
        p.write_text("preservar")
    source.write_text('<screen width="0"/>')
    assert (
        main([str(source), "-o", str(output), "--export-json", str(data), "--quiet", "--diagnostics-format", "json"])
        == 1
    )
    assert all(p.read_text() == "preservar" for p in [output, header, data])
    diagnostic = json.loads(capsys.readouterr().err)
    assert diagnostic[0]["code"] == "html.dimensions"


def test_path_collisions_rejected(source, tmp_path):
    output = tmp_path / "out.c"
    assert main([str(source), "-o", str(output), "--export-json", str(source)]) == 1
    assert not output.exists()
    assert main([str(source), "-o", str(output), "--export-json", str(output.with_suffix(".h"))]) == 1


def test_validate_does_not_write_code(source, tmp_path):
    output = tmp_path / "out.c"
    assert main([str(source), "-o", str(output), "--validate"]) == 0
    assert not output.exists()
    assert not output.with_suffix(".h").exists()


def test_legacy_file_api_json_and_error(source, tmp_path):
    t = UITranslator(TranslationConfig(output_format="json", verbose=False))
    output = tmp_path / "data.json"
    assert t.translate_file(source, output)
    assert json.loads(output.read_text())["computed_layout"]
    assert not t.translate_file(source, source)


def test_package_command_works_from_other_directory(source, tmp_path):
    completed = subprocess.run(
        [sys.executable, "-m", "translator", str(source), "--validate", "--quiet"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == ""


def test_legacy_script_entry_point(source, tmp_path):
    script = Path(__file__).resolve().parents[1] / "translator/cli.py"
    completed = subprocess.run(
        [sys.executable, str(script), str(source), "--validate", "--quiet"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def test_estimates_not_reported_as_performance(source, capsys):
    assert main([str(source), "--check-perf"]) == 1
    assert "medição" in capsys.readouterr().err


def test_debug_export_cannot_overwrite_input(tmp_path):
    source = tmp_path / "out.debug.json"
    source.write_text("<screen><label>x</label></screen>")
    original = source.read_text()
    translator = UITranslator(TranslationConfig(enable_debug_output=True))
    assert not translator.translate_file(source, tmp_path / "out.c")
    assert source.read_text() == original


def test_file_read_failure_clears_previous_result(source, tmp_path):
    translator = UITranslator()
    translator.translate_html(source.read_text())
    assert not translator.translate_file(tmp_path / "missing.html", tmp_path / "out.c")
    assert translator.last_result is None


@pytest.mark.parametrize("existing", [False, True])
def test_output_commit_failure_rolls_back_entire_set(source, tmp_path, monkeypatch, existing):
    import os

    output, header, data = tmp_path / "out.c", tmp_path / "out.h", tmp_path / "out.json"
    if existing:
        for path in (output, header, data):
            path.write_text("anterior: " + path.name)
    replace = os.replace
    failed = False

    def fail_once(src, dst):
        nonlocal failed
        if Path(dst) == output and not failed:
            failed = True
            raise OSError("Falha de disco simulada")
        return replace(src, dst)

    monkeypatch.setattr(os, "replace", fail_once)
    assert main([str(source), "-o", str(output), "--export-json", str(data)]) == 1
    for path in (output, header, data):
        assert path.read_text() == "anterior: " + path.name if existing else not path.exists()
    assert set(tmp_path.iterdir()) == ({source, output, header, data} if existing else {source})


def test_prepare_failure_preserves_header_and_code(source, tmp_path):
    output, header, data = tmp_path / "out.c", tmp_path / "out.h", tmp_path / "out.json"
    output.write_text("old C")
    header.write_text("old H")
    data.mkdir()
    assert main([str(source), "-o", str(output), "--export-json", str(data)]) == 1
    assert output.read_text() == "old C" and header.read_text() == "old H"


def test_atomic_output_rejects_symlinks_and_duplicate_destinations(tmp_path):
    original, link = tmp_path / "original.c", tmp_path / "link.c"
    original.write_text("intact")
    link.symlink_to(original)
    with pytest.raises(ValueError, match="link simbólico"):
        atomic_write_many({link: "changed"})
    assert original.read_text() == "intact" and link.is_symlink()
    with pytest.raises(ValueError, match="distintos"):
        atomic_write_many({original: "changed", link: "changed"})


def test_file_api_rolls_back_when_debug_output_is_directory(source, tmp_path):
    output, header, debug = tmp_path / "out.c", tmp_path / "out.h", tmp_path / "out.debug.json"
    output.write_text("old C")
    header.write_text("old H")
    debug.mkdir()
    translator = UITranslator(TranslationConfig(enable_debug_output=True))
    assert not translator.translate_file(source, output)
    assert output.read_text() == "old C" and header.read_text() == "old H"


def test_failed_restore_preserves_backup_and_attempts_other_restores(tmp_path, monkeypatch):
    import os

    output, header = tmp_path / "out.c", tmp_path / "out.h"
    output.write_text("old C")
    header.write_text("old H")
    replace = os.replace

    def locked_output(src, dst):
        if Path(dst) == output:
            raise OSError("Destino indisponível")
        return replace(src, dst)

    monkeypatch.setattr(os, "replace", locked_output)
    with pytest.raises(OSError, match="original salvo") as caught:
        atomic_write_many({header: "new H", output: "new C"})
    assert header.read_text() == "old H"
    backups = [path for path in tmp_path.iterdir() if path != header]
    assert len(backups) == 1 and backups[0].read_text() == "old C"
    assert str(backups[0]) in str(caught.value)
