"""Verify VSIX contents and execute its bundled Python backend in isolation."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def verify(vsix, pythons):
    vsix = Path(vsix).resolve()
    record = {"artifact": vsix.name, "sha256": hashlib.sha256(vsix.read_bytes()).hexdigest(), "python_checks": []}
    with tempfile.TemporaryDirectory(prefix="embedmark-release-check-") as directory:
        work = Path(directory)
        with zipfile.ZipFile(vsix) as archive:
            names = archive.namelist()
            for name in names:
                parts = PurePosixPath(name)
                if parts.is_absolute() or ".." in parts.parts or "\\" in name:
                    raise ValueError(f"Unsafe VSIX path: {name}")
                if any(part in {"node_modules", ".venv", ".git", "__pycache__", ".env"} for part in parts.parts):
                    raise ValueError(f"Development/private file in VSIX: {name}")
            archive.extractall(work)
        extension = work / "extension"
        package = json.loads((extension / "package.json").read_text(encoding="utf-8"))
        bundled = extension / "bundled/python"
        manifest = json.loads((bundled / "BACKEND_MANIFEST.json").read_text(encoding="utf-8"))
        if package["version"] != manifest["translator"]:
            raise ValueError("Extension/backend version mismatch")
        wheel = vsix.parent / f"embedmark-{package['version']}-py3-none-any.whl"
        if wheel.exists():
            with zipfile.ZipFile(wheel) as python_package:
                core_files = [name for name in python_package.namelist() if name.startswith("translator/")]
                for name in core_files:
                    if (bundled / name).read_bytes() != python_package.read(name):
                        raise ValueError(f"VSIX backend differs from Python wheel: {name}")
            record["wheel_core_files_matched"] = len(core_files)
            record["wheel_sha256"] = hashlib.sha256(wheel.read_bytes()).hexdigest()
        for name, digest in manifest["files"].items():
            if hashlib.sha256((bundled / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f"Bundled file checksum mismatch: {name}")
        if not (extension / package["main"]).is_file():
            raise ValueError("Extension entry point is missing")
        if not (extension / package["icon"]).read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Extension icon is not a PNG")
        for name in [
            "readme.md",
            "changelog.md",
            "LICENSE.txt",
            "resources/LANGUAGE_GUIDE.md",
            "resources/FONTES.md",
            "resources/API_FIRMWARE.md",
            "bundled/python/THIRD_PARTY_NOTICES.md",
        ]:
            if not (extension / name).is_file():
                raise ValueError(f"Missing packaged asset: {name}")
        cases = [
            (p, {})
            for p in [
                ROOT / "examples/01_minima.html",
                ROOT / "examples/02_espacamento.html",
                ROOT / "examples/03_hierarquia.html",
                ROOT / "translator/sample_ui.html",
                ROOT / "translator/advanced_example.html",
            ]
        ]
        cases.append(
            (ROOT / "examples/05_interacao.html", {"font_manifest": str(extension / "resources/fonts/fontes.json")})
        )
        for python in pythons:
            version = subprocess.check_output([python, "--version"], text=True).strip()
            for source, config in cases:
                request = {
                    "protocol": 1,
                    "action": "generate",
                    "source": source.read_text(encoding="utf-8"),
                    "config": config,
                }
                process = subprocess.run(
                    [python, "-I", "-S", str(extension / "bundled/launcher.py")],
                    input=json.dumps(request),
                    capture_output=True,
                    text=True,
                    cwd=work,
                    timeout=30,
                )
                response = json.loads(process.stdout)
                if (
                    process.returncode != 0
                    or not response.get("ok")
                    or not response.get("code")
                    or not response.get("header")
                ):
                    raise ValueError(f"Packaged backend failed on {version}/{source.name}: {response}")
                if response["version"] != package["version"]:
                    raise ValueError("Running backend returned unexpected version")
            invalid = {
                "protocol": 1,
                "action": "generate",
                "source": (ROOT / "examples/04_erros.html").read_text(encoding="utf-8"),
            }
            process = subprocess.run(
                [python, "-I", "-S", str(extension / "bundled/launcher.py")],
                input=json.dumps(invalid),
                capture_output=True,
                text=True,
                cwd=work,
                timeout=30,
            )
            response = json.loads(process.stdout)
            if process.returncode == 0 or response.get("ok") or not response.get("diagnostics"):
                raise ValueError("Invalid input was not rejected by the packaged backend")
            record["python_checks"].append(
                {"python": version, "valid_examples": len(cases), "invalid_example": "rejected"}
            )
        record.update(
            {
                "version": package["version"],
                "publisher": package["publisher"],
                "bundled_files_verified": len(manifest["files"]),
                "vsix_files": len(names),
                "status": "passed",
            }
        )
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vsix")
    parser.add_argument("--python", action="append", required=True, help="Repeat to test more interpreters")
    parser.add_argument("--report")
    args = parser.parse_args()
    record = verify(args.vsix, args.python)
    text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
