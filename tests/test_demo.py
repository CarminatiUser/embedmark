from pathlib import Path
import subprocess
import sys


def test_prepared_demo_preserves_modified_application_code(tmp_path):
    script = Path(__file__).resolve().parents[1] / "tools/prepare_demo.py"
    destination = tmp_path / "demo com espaço"
    command = [sys.executable, str(script), "--output", str(destination)]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    expected = {
        "ui_generated.c",
        "ui_generated.h",
        "ui_controller.c",
        "ui_controller.h",
        "tcc_font_pt_14.c",
        "tcc_font_pt_20.c",
        "tcc_font_pt_24.c",
        "OFL.txt",
        "fontes.json",
        "tcc_ui_sources.cmake",
    }
    assert {path.name for path in destination.iterdir()} == expected
    controller = destination / "ui_controller.c"
    controller.write_text(controller.read_text() + "\n/* Alteração do usuário. */\n")
    before = {path.name: path.read_bytes() for path in destination.iterdir()}
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert "Controlador modificado preservado" in result.stderr
    assert {path.name: path.read_bytes() for path in destination.iterdir()} == before
