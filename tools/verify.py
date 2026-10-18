#!/usr/bin/env python3
"""Compare every committed generated artifact with a fresh source-derived build."""
from pathlib import Path
import argparse
import sys

from build import ROOT, artifacts


def verify(root: Path = ROOT, profile_relative: str = "profiles/big-lever.json") -> None:
    expected = artifacts(root, profile_relative)
    actual: dict[str, bytes] = {}
    for directory in ("packages", "builder", ".claude-plugin"):
        if (root / directory).is_symlink():
            raise ValueError(f"Generated directory must not be a symlink: {directory}")
        for path in (root / directory).rglob("*"):
            if path.is_symlink():
                raise ValueError(f"Generated symlink: {path.relative_to(root)}")
            if path.is_file():
                actual[path.relative_to(root).as_posix()] = path.read_bytes()
    manifest = root / "release-manifest.json"
    if manifest.is_symlink():
        raise ValueError("Generated manifest must not be a symlink")
    actual["release-manifest.json"] = manifest.read_bytes()
    if expected != actual:
        different = sorted(name for name in expected.keys() | actual.keys() if expected.get(name) != actual.get(name))
        raise ValueError("Generated files differ from source: " + ", ".join(different))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="profiles/big-lever.json", help="Profile used for the committed generated distribution")
    args = parser.parse_args()
    try:
        verify(profile_relative=args.profile)
    except (OSError, ValueError) as error:
        sys.exit(f"Verification failed: {error}")
    print("Generated packages, authoring files and manifest match source exactly.")
