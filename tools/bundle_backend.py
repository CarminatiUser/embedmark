"""Bundle the translator and hash-locked pure Python dependencies for VS Code."""

import argparse
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def locked_dependencies(lock):
    dependencies = {}
    for line in lock.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        match = re.fullmatch(r"([\w-]+)==([\w.]+) --hash=sha256:([a-f0-9]{64})", line)
        if not match:
            raise ValueError(f"Unsupported dependency lock line: {line}")
        name, version, digest = match.groups()
        dependencies[name.replace("-", "_").lower()] = (version, digest)
    if not dependencies:
        raise ValueError("Empty dependency lock")
    return dependencies


def verified_wheels(cache, dependencies):
    selected = {}
    for wheel in sorted(cache.glob("*.whl")):
        with zipfile.ZipFile(wheel) as archive:
            metadata_names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(metadata_names) != 1:
                continue
            metadata = BytesParser().parsebytes(archive.read(metadata_names[0]))
        name = metadata["Name"].replace("-", "_").lower()
        if name not in dependencies or metadata["Version"] != dependencies[name][0]:
            continue
        digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
        if digest != dependencies[name][1]:
            raise ValueError(f"Dependency checksum mismatch: {wheel.name}")
        if not wheel.name.endswith("none-any.whl"):
            raise ValueError(f"Only pure Python wheels may be bundled: {wheel.name}")
        selected[name] = (wheel, digest)
    missing = set(dependencies) - set(selected)
    if missing:
        raise ValueError("Missing verified wheels: " + ", ".join(sorted(missing)))
    return selected


def unpack_wheel(wheel, destination):
    with zipfile.ZipFile(wheel) as archive:
        for entry in archive.infolist():
            name = PurePosixPath(entry.filename)
            if name.is_absolute() or ".." in name.parts or "\\" in entry.filename:
                raise ValueError(f"Unsafe wheel entry: {entry.filename}")
            if any(part.endswith(".data") for part in name.parts):
                raise ValueError(f"Wheel requires unsupported installation mapping: {entry.filename}")
            target = destination.joinpath(*name.parts)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                if target.exists():
                    raise ValueError(f"Bundled dependency file collision: {entry.filename}")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(entry))


def bundle(root=ROOT, *, download=True):
    lock = root / "requirements-runtime.lock"
    cache = root / "build/wheels"
    cache.mkdir(parents=True, exist_ok=True)
    dependencies = locked_dependencies(lock)
    if download:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "download",
                "--disable-pip-version-check",
                "--no-deps",
                "--only-binary=:all:",
                "--require-hashes",
                "-r",
                str(lock),
                "-d",
                str(cache),
            ],
            check=True,
        )
    selected = verified_wheels(cache, dependencies)
    bundled = root / "extension/bundled"
    bundled.mkdir(parents=True, exist_ok=True)
    destination = bundled / "python"
    if destination.is_symlink():
        raise ValueError("Bundled Python directory cannot be a symbolic link")
    version_source = (root / "translator/__init__.py").read_text(encoding="utf-8")
    version = re.search(r'__version__ = "([^"]+)"', version_source).group(1)
    manifest = {"translator": version, "protocol": 1, "dependencies": [], "files": {}}
    with tempfile.TemporaryDirectory(prefix="embedmark-bundle-", dir=bundled) as staging_name:
        staging = Path(staging_name)
        for name, (wheel, digest) in selected.items():
            unpack_wheel(wheel, staging)
            with zipfile.ZipFile(wheel) as archive:
                license_paths = [
                    item
                    for item in archive.namelist()
                    if not item.endswith("/") and ("license" in item.lower() or "copying" in item.lower())
                ]
            manifest["dependencies"].append(
                {
                    "name": name,
                    "version": dependencies[name][0],
                    "wheel": wheel.name,
                    "sha256": digest,
                    "license_files": license_paths,
                }
            )
        shutil.copytree(
            root / "translator", staging / "translator", ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
        )
        shutil.copyfile(root / "LICENSE", staging / "TRANSLATOR_LICENSE.txt")
        notices = [
            "# Third-party notices",
            "",
            "Original upstream license files are included without modification.",
            "",
        ]
        for dependency in manifest["dependencies"]:
            notices.append(f"- {dependency['name']} {dependency['version']}")
            notices.extend(f"  - [{name}]({name})" for name in dependency["license_files"])
        notices.extend(["", "Bitmap fonts and their OFL license are included separately in resources/fonts.", ""])
        (staging / "THIRD_PARTY_NOTICES.md").write_text("\n".join(notices), encoding="utf-8")
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                manifest["files"][path.relative_to(staging).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        (staging / "BACKEND_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        previous = bundled / ".python-previous"
        if previous.exists():
            raise ValueError(f"Previous bundle needs recovery: {previous}")
        if destination.exists():
            destination.rename(previous)
        try:
            staging.rename(destination)
        except OSError:
            if previous.exists():
                previous.rename(destination)
            raise
        if previous.exists():
            shutil.rmtree(previous)
    print(f"Bundled translator {version} with {len(selected)} verified dependencies: {destination}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Use already downloaded hash-verified wheels")
    args = parser.parse_args()
    try:
        bundle(download=not args.offline)
    except (OSError, ValueError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"Bundle failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
