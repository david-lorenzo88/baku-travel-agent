#!/usr/bin/env python3
"""Copy an updated skill's payload from skills-src/ into an already-imported agent skill.

Usage: python tools/stage_skill.py <skill-name> [--agent agent]

Use this (not `add-skill --force`) to update a skill that is already in agent/behaviors/:
--force re-import mints new schema names for the anchor and sidecars, and the next
`pac copilot pull` then reverts the payload to the cloud copy. This tool copies only payload
files (SKILL.md, scripts/, references/, assets/) and never touches PAC's *.mcs.yml companions.

Run it AFTER the pre-push `pac copilot pull` (a pull overwrites local payload edits with the
cloud copy), then validate and push. New files without a companion sidecar are reported: import
those with the add-skill importer instead.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    skill = argv[1]
    agent = Path(argv[argv.index("--agent") + 1]) if "--agent" in argv else ROOT / "agent"
    src = ROOT / "skills-src" / skill
    dst = agent / "behaviors" / skill
    if not (src / "SKILL.md").is_file():
        print(f"error: {src}/SKILL.md not found", file=sys.stderr)
        return 2
    if not (dst / "skill.mcs.yml").is_file():
        print(f"error: {dst} is not an imported skill — import it with add-skill first", file=sys.stderr)
        return 2

    copied, missing_sidecar = [], []
    for f in sorted(p for p in src.rglob("*") if p.is_file()):
        rel = f.relative_to(src)
        if f.name.endswith(".mcs.yml") or "__pycache__" in rel.parts:
            continue
        target = dst / rel
        if not target.is_file() or target.read_bytes() != f.read_bytes():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
            copied.append(str(rel))
        if rel.name != "SKILL.md" and not (dst / (str(rel) + ".mcs.yml")).is_file():
            missing_sidecar.append(str(rel))

    stale = [
        str(p.relative_to(dst)) for p in dst.rglob("*")
        if p.is_file() and not p.name.endswith(".mcs.yml") and not (src / p.relative_to(dst)).is_file()
    ]
    print(f"{skill}: {len(copied)} file(s) updated" + (f": {', '.join(copied)}" if copied else ""))
    if missing_sidecar:
        print("new files with no sidecar (import needed): " + ", ".join(missing_sidecar))
    if stale:
        print("files in agent but not in source (remove in Copilot Studio if unwanted): " + ", ".join(stale))
    return 1 if missing_sidecar else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
