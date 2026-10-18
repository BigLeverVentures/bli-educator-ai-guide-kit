#!/usr/bin/env python3
"""Import selected resources from a pinned public BLI educator release, offline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urljoin, urlsplit

from build import contained, encode, unsafe_symlink

REPOSITORY = "https://github.com/BigLeverVentures/bli-for-educators"
PEDAGOGY = ("educators/approach.md", "educators/authoring-kit.md", "educators/evaluation.md")
# Exact reviewed upstream notices, before link resolution. A new notice needs review.
REVIEWED_LICENSES = {
    # Same teaching-use terms, with the preserved original notice linked locally.
    "8048906349d9bd66944228dd0fa8cf85e8d62c04f7a8bd404cf47c2f599a946a": "teaching-use-1.0",
    "f9e44e9877575958b92cdf0bf3e5022dd0910662872a33cadd7159e302cc3450": "cc-by-4.0",
    "d91dd9ed55e41d986dc0e3449560fcb6745bd4af2ca2186db7f037b6f412b2f8": "teaching-use-1.0",
}


def resolve_links(body: str, source_url: str) -> str:
    """Keep prose intact; make Markdown and HTML relative source links absolute."""
    def url(value: str) -> str:
        if urlsplit(value).scheme or value.startswith("//"):
            return value
        return urljoin(source_url, value)
    body = re.sub(r'(\bhref=[\"\x27])([^\"\x27]+)([\"\x27])', lambda m: m[1] + url(m[2]) + m[3], body)
    return re.sub(r'(\]\()([^\s)]+)(\))', lambda m: m[1] + url(m[2]) + m[3], body)


def collect(source: Path, commit: str) -> dict[str, bytes]:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("commit must be the full public source SHA")
    inventory = json.loads(contained(source, "release-manifest.json").read_bytes())
    actual_commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if actual_commit != commit:
        raise ValueError("Supplied commit does not match the public checkout HEAD")
    pages = inventory["pages"]
    if not isinstance(pages, list) or not pages:
        raise ValueError("Public release has no resource inventory")
    selected = [page["path"] for page in pages] + list(PEDAGOGY) + ["LICENSE.md"]
    if len(selected) != len(set(selected)):
        raise ValueError("Duplicate public resource path")
    data = {}
    for name in ["release-manifest.json", *selected]:
        content = contained(source, name).read_bytes()
        committed = subprocess.check_output(["git", "-C", str(source), "show", f"{commit}:{name}"])
        if content != committed:
            raise ValueError(f"Public checkout differs from the pinned commit: {name}")
        if name == "release-manifest.json":
            continue
        if hashlib.sha256(content).hexdigest() != inventory["files"].get(name):
            raise ValueError(f"Public source hash mismatch: {name}")
        content.decode("utf-8")
        data[name] = content
    license_policy = REVIEWED_LICENSES.get(hashlib.sha256(data["LICENSE.md"]).hexdigest())
    if license_policy is None:
        raise ValueError("Unreviewed upstream license; review its complete text before importing")
    records = []
    sections = []
    for page in pages:
        name = page["path"]
        if not (name.startswith(("basics/", "exercises/", "paths/")) or name == "glossary.md"):
            raise ValueError(f"Resource outside reviewed curriculum scope: {name}")
        body = resolve_links(data[name].decode("utf-8"), f"{REPOSITORY}/blob/{commit}/{name}")
        resource_id = name.removesuffix(".md")
        records.append({"id": resource_id, "title": page["title"], "group": page["group"],
                        "url": "https://exercises.bigleverinstitute.org/" + page["browser_path"].removeprefix("site/"),
                        "source_heading": f"Resource: {resource_id}"})
        sections.append(f"# Resource: {resource_id}\n\nPublic source: {REPOSITORY}/blob/{commit}/{name}\n\n{body}")
    teaching = []
    for name in PEDAGOGY:
        teaching.append(f"# Source: {name}\n\n" + resolve_links(data[name].decode("utf-8"), f"{REPOSITORY}/blob/{commit}/{name}"))
    if license_policy == "teaching-use-1.0":
        permission = ("This distribution offers original educational text, prompts and templates under "
                      "Big Lever Educator Teaching-Use License 1.0: adapt and share for teaching; "
                      "no resale of covered materials. Ordinary paid teaching and learner-created work "
                      "remain allowed. Prior CC BY rights in unchanged material remain valid regardless "
                      "of which copy is used, including commercial reuse under that prior grant.")
    else:
        permission = ("This earlier snapshot was offered under CC BY 4.0, including commercial reuse "
                      "with attribution. Those rights remain valid regardless of which copy is used.")
    notice = ("# Curriculum source and reuse\n\nCopyright 2026 Big Lever Institute. " + permission +
              " See LICENSE.md in this curriculum folder.\n\n" +
              f"Adapted from {REPOSITORY}, revision {commit}. Packaging changes: selected public resource inventory; combined Markdown; relative source links resolved to pinned public URLs; catalog adds public lesson-site URLs. No underlying lesson prose was rewritten. This is a dated snapshot, not a live feed.\n")
    return {
        "catalog.json": encode({"snapshot_date": inventory["release_date"], "resources": records}),
        "lessons.md": (notice + "\n\n" + "\n\n---\n\n".join(sections)).encode("utf-8"),
        "pedagogy.md": (notice + "\n\n" + "\n\n---\n\n".join(teaching)).encode("utf-8"),
        "LICENSE.md": resolve_links(data["LICENSE.md"].decode("utf-8"), f"{REPOSITORY}/blob/{commit}/LICENSE.md").encode("utf-8"),
        "upstream.json": encode({"repository": REPOSITORY, "commit": commit, "release_date": inventory["release_date"],
            "source_files": {name: hashlib.sha256(content).hexdigest() for name, content in sorted(data.items())},
            "transformations": ["Combine selected public resources", "Resolve relative source links to pinned GitHub URLs", "Add public lesson-site catalog URLs"]}),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="A clean checkout of the public bli-for-educators release")
    parser.add_argument("destination", type=Path, help="Fresh directory outside the source checkout")
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    try:
        source = args.source.resolve()
        destination = args.destination.absolute()
        if any(unsafe_symlink(p) for p in (destination, *destination.parents)):
            raise ValueError("Destination may not use symlinks")
        resolved = destination.resolve()
        if destination.exists() or resolved == source or source in resolved.parents or resolved in source.parents:
            raise ValueError("Destination must be fresh and outside the source checkout")
        files = collect(source, args.commit)
        destination.mkdir(parents=True, exist_ok=False)
        for name, content in files.items():
            (destination / name).write_bytes(content)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Import failed: {error}\n")
    print(f"Imported reviewed public curriculum to {destination}; review the diff before adopting it.")


if __name__ == "__main__":
    main()
