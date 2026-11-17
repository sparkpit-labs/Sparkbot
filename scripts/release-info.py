#!/usr/bin/env python3
"""Print the desktop release label and check every place that repeats it.

The public label (for example v0.0.01) lives in site/release.json. Installers
need a three-part version, so the same file carries it (0.0.1).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = (
    "windows-x64-setup.exe",
    "macos-arm64.dmg",
    "macos-x64.dmg",
    "linux-x64.AppImage",
    "linux-x64.deb",
)


def load() -> dict:
    return json.loads((ROOT / "site" / "release.json").read_text(encoding="utf-8"))


def problems(info: dict, ref: str | None) -> list[str]:
    label, version, repo = info["label"], info["version"], info["repository"]
    found: list[str] = []
    if not re.fullmatch(r"v\d+(\.\d+){2}", label):
        found.append(f"label {label!r} is not v<number>.<number>.<number>")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        found.append(f"version {version!r} is not three plain numbers")
    elif [int(p) for p in label[1:].split(".")] != [int(p) for p in version.split(".")]:
        found.append(f"label {label} and version {version} are different numbers")
    tauri = json.loads((ROOT / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8"))
    if tauri["version"] != version:
        found.append(f"src-tauri/tauri.conf.json has {tauri['version']}, expected {version}")
    cargo = (ROOT / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8")
    if f'version = "{version}"' not in cargo.split("[build-dependencies]")[0]:
        found.append(f"src-tauri/Cargo.toml package version is not {version}")
    if not (ROOT / "docs" / f"RELEASE_NOTES_{label}.md").is_file():
        found.append(f"docs/RELEASE_NOTES_{label}.md is missing")
    page = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    base = f"https://github.com/{repo}/releases/download/{label}/"
    for suffix in ASSETS:
        link = f"{base}Sparkbot-Roundtable-{label}-{suffix}"
        if link not in page:
            found.append(f"site/index.html does not link {link}")
    if f"{base}SHA256SUMS.txt" not in page:
        found.append("site/index.html does not link the checksum file")
    if ref and ref.startswith("refs/tags/") and ref != f"refs/tags/{label}":
        found.append(f"tag {ref.removeprefix('refs/tags/')} does not match label {label}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if any copy of the version disagrees")
    parser.add_argument("--ref", help="the Git ref being built, to compare a tag with the label")
    parser.add_argument("--github-output", help="append label and version to this GitHub Actions output file")
    args = parser.parse_args()
    info = load()
    print(f"label={info['label']}")
    print(f"version={info['version']}")
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as out:
            out.write(f"label={info['label']}\nversion={info['version']}\n")
    if args.check:
        found = problems(info, args.ref)
        for line in found:
            print(f"release-info: {line}", file=sys.stderr)
        return 1 if found else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
