import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

spec = importlib.util.spec_from_file_location("bundle_backend", Path(__file__).parents[1] / "bundle_backend.py")
bundler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundler)


def fixture_root(root):
    (root / "translator").mkdir()
    (root / "translator/__init__.py").write_text('__version__ = "0.4.2"\n')
    (root / "LICENSE").write_text("All rights reserved.\n")
    cache = root / "build/wheels"
    cache.mkdir(parents=True)
    wheel = cache / "sample-1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("sample/__init__.py", "VALUE = 1\n")
        archive.writestr("sample-1.0.dist-info/METADATA", "Name: sample\nVersion: 1.0\n")
        archive.writestr("sample-1.0.dist-info/LICENSE", "Sample license\n")
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
    (root / "requirements-runtime.lock").write_text(f"sample==1.0 --hash=sha256:{digest}\n")
    return wheel


def test_offline_bundle_contains_sources_licenses_and_checksums(tmp_path):
    fixture_root(tmp_path)
    manifest = bundler.bundle(tmp_path, download=False)
    output = tmp_path / "extension/bundled/python"
    assert (output / "sample-1.0.dist-info/LICENSE").read_text() == "Sample license\n"
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == digest
    assert json.loads((output / "BACKEND_MANIFEST.json").read_text()) == manifest


def test_replacement_removes_obsolete_files(tmp_path):
    fixture_root(tmp_path)
    bundler.bundle(tmp_path, download=False)
    output = tmp_path / "extension/bundled/python"
    (output / "obsolete.py").write_text("stale")
    bundler.bundle(tmp_path, download=False)
    assert not (output / "obsolete.py").exists()
    assert not (output.parent / ".python-previous").exists()


def test_checksum_failure_preserves_last_bundle(tmp_path):
    wheel = fixture_root(tmp_path)
    bundler.bundle(tmp_path, download=False)
    output = tmp_path / "extension/bundled/python/sample/__init__.py"
    with zipfile.ZipFile(wheel, "a") as archive:
        archive.writestr("injected.py", "unsafe")
    with pytest.raises(ValueError, match="checksum mismatch"):
        bundler.bundle(tmp_path, download=False)
    assert output.read_text() == "VALUE = 1\n"


@pytest.mark.parametrize("name", ["../escape.py", "/escape.py", "bad\\escape.py"])
def test_wheel_paths_cannot_escape_destination(tmp_path, name):
    wheel = tmp_path / "bad.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(name, "unsafe")
    with pytest.raises(ValueError, match="Unsafe wheel entry"):
        bundler.unpack_wheel(wheel, tmp_path / "output")
    assert not (tmp_path / "escape.py").exists()


def test_recovery_directory_blocks_replacement(tmp_path):
    fixture_root(tmp_path)
    bundler.bundle(tmp_path, download=False)
    previous = tmp_path / "extension/bundled/.python-previous"
    previous.mkdir()
    (previous / "keep").write_text("recovery")
    with pytest.raises(ValueError, match="needs recovery"):
        bundler.bundle(tmp_path, download=False)
    assert (previous / "keep").read_text() == "recovery"
