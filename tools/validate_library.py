"""Check the public reference package without contacting Resolve or GitHub."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"
SKIP_DIRS = {".git", "__pycache__", ".venv", ".pytest_cache"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def tracked_files() -> dict[str, dict[str, object]]:
    data = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.name == "MANIFEST.json":
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix == ".pyc":
            continue
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        data[rel] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return data


def validate_links() -> list[str]:
    problems = []
    for md in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in md.relative_to(ROOT).parts):
            continue
        body = md.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(body):
            target = raw.strip().split()[0].strip('<>')
            if target.startswith(("#", "http:", "https:", "mailto:", "data:")):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if target and not (md.parent / target).resolve().is_file():
                problems.append(f"{md.relative_to(ROOT)}: missing link {target}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()

    actual = tracked_files()
    if args.write_manifest:
        previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
        manifest = {
            "package": "Resolve_Agent_v1.9",
            "release_date": "2026-11-12",
            "tested_resolve": previous.get("tested_resolve", "21.2.0.5"),
            "entrypoint": "GUIDE.md",
            "files": actual,
        }
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Manifest written: {len(actual)} files")
        return 0

    problems = []
    if not MANIFEST.exists():
        problems.append("MANIFEST.json missing")
    else:
        expected = json.loads(MANIFEST.read_text(encoding="utf-8")).get("files", {})
        for path in sorted(set(expected) | set(actual)):
            if path not in expected:
                problems.append(f"Unlisted file: {path}")
            elif path not in actual:
                problems.append(f"Manifest refers to missing file: {path}")
            elif expected[path] != actual[path]:
                problems.append(f"Manifest size/hash mismatch: {path}")
    problems.extend(validate_links())
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        try:
            compile(path.read_bytes(), str(path), "exec")
        except Exception as exc:
            problems.append(f"Python syntax error {path.relative_to(ROOT)}: {exc}")
    if problems:
        print("Validation FAILED:\n" + "\n".join(f"- {item}" for item in problems))
        return 1
    print(f"Validation OK: {len(actual)} files, local Markdown links and Python syntax")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
