#!/usr/bin/env python3
"""Validate a Copilot Studio CLI agent workspace before `pac copilot push`.

Usage: python tools/validate_agent.py <agent-dir>

Exits 0 when the workspace passes, 1 when problems are found (all listed), 2 on usage errors.
Uses yaml.safe_load (YAML 1.1), which is how the Copilot Studio tooling reads these files, so
scalars such as `on`, `yes` or `2026-11-13` are caught when they should be strings.
Never reads `.mcs/` (CLI-managed state).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

SCHEMA_NAME_LIMIT = 100
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
AGENT_SCHEMA_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
TOPIC_KIND_RE = re.compile(r"(Topic|AdaptiveDialog)", re.IGNORECASE)


def load_yaml(path: Path, problems: list[str]):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        problems.append(f"{path}: invalid YAML ({exc.__class__.__name__}: {exc})")
        return None


def parse_frontmatter(text: str):
    """Return the frontmatter mapping of a Markdown document, or None."""
    if not text.startswith("---"):
        return None
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return None
    body = parts[0][3:]
    try:
        data = yaml.safe_load(body)
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def check_skill_frontmatter(fm, folder: str, where: str, problems: list[str]) -> None:
    if fm is None:
        problems.append(f"{where}: missing or invalid YAML frontmatter")
        return
    name = fm.get("name")
    desc = fm.get("description")
    if not isinstance(name, str) or not name:
        problems.append(f"{where}: frontmatter 'name' must be a non-empty string")
    else:
        if name != folder:
            problems.append(f"{where}: frontmatter name '{name}' must equal folder '{folder}'")
        if len(name) > 64 or not SKILL_NAME_RE.match(name):
            problems.append(
                f"{where}: name '{name}' must be ≤ 64 chars of lowercase letters, digits and single hyphens"
            )
    if not isinstance(desc, str) or not desc.strip():
        problems.append(f"{where}: frontmatter 'description' must be a non-empty string")
    else:
        if "\n" in desc.strip():
            problems.append(f"{where}: description must be a single line")
        if len(desc) > 1024:
            problems.append(f"{where}: description is {len(desc)} chars (max 1024)")


def validate(agent_dir: Path) -> tuple[list[str], int]:
    problems: list[str] = []
    checked = 0

    settings_path = agent_dir / "settings.mcs.yml"
    agent_schema = ""
    if not settings_path.is_file():
        problems.append(f"{settings_path}: missing")
    else:
        settings = load_yaml(settings_path, problems)
        checked += 1
        if isinstance(settings, dict):
            template = settings.get("template")
            if not (isinstance(template, str) and template.lower().startswith("cliagent-")):
                problems.append(f"{settings_path}: template must start with 'cliagent-' (got {template!r})")
            cfg = settings.get("configuration") or {}
            if not isinstance(cfg, dict) or cfg.get("authoringModel") != "CliCopilot":
                problems.append(f"{settings_path}: configuration.authoringModel must be 'CliCopilot'")
            agent_schema = settings.get("schemaName") or ""
            if not (isinstance(agent_schema, str) and AGENT_SCHEMA_RE.match(agent_schema)):
                problems.append(f"{settings_path}: schemaName {agent_schema!r} is not a valid prefix")
                agent_schema = ""
            elif len(agent_schema) > SCHEMA_NAME_LIMIT:
                problems.append(f"{settings_path}: schemaName longer than {SCHEMA_NAME_LIMIT} chars")
            segments = (((cfg.get("agentSettings") or {}).get("instructions") or {}).get("segments")) or []
            if not any(isinstance(s, dict) and str(s.get("value", "")).strip() for s in segments):
                problems.append(f"{settings_path}: instructions are empty")
        elif settings is not None:
            problems.append(f"{settings_path}: top level must be a mapping")

    for path in sorted(agent_dir.rglob("*")):
        rel = path.relative_to(agent_dir)
        if rel.parts and rel.parts[0] == ".mcs":
            continue
        if path.is_dir() and path.name.lower() == "topics":
            problems.append(f"{path}: topics are not allowed in a CLI agent")
            continue
        if not path.is_file() or not path.name.endswith(".mcs.yml") or path == settings_path:
            continue

        checked += 1
        data = load_yaml(path, problems)
        if data is None:
            continue
        if not isinstance(data, dict):
            problems.append(f"{path}: top level must be a mapping")
            continue

        meta = data.get("mcs.metadata")
        if not isinstance(meta, dict):
            problems.append(f"{path}: missing mcs.metadata")
            continue
        comp = meta.get("componentName")
        if not isinstance(comp, str) or not comp.strip():
            problems.append(f"{path}: mcs.metadata.componentName must be a non-empty string (got {comp!r})")
        if "description" in meta and not isinstance(meta.get("description"), str):
            problems.append(f"{path}: mcs.metadata.description must be a string")
        schema = meta.get("schemaName")
        if isinstance(schema, str) and len(schema) > SCHEMA_NAME_LIMIT:
            problems.append(f"{path}: schemaName is {len(schema)} chars (max {SCHEMA_NAME_LIMIT})")
        for key in ("bundle", "manifestSchemaName"):
            val = meta.get(key)
            if isinstance(val, str) and len(val) > SCHEMA_NAME_LIMIT:
                problems.append(f"{path}: {key} is {len(val)} chars (max {SCHEMA_NAME_LIMIT})")

        parts = rel.parts
        is_skill_payload_sidecar = False
        is_knowledge_sidecar = len(parts) >= 3 and parts[0] == "capabilities" and parts[1] == "knowledge" and parts[2] == "files"
        if parts and parts[0] == "behaviors" and len(parts) >= 3:
            folder = parts[1]
            anchor_names = {"skill.mcs.yml", f"{folder}.mcs.yml"}
            is_skill_payload_sidecar = not (len(parts) == 3 and parts[2] in anchor_names)

        kind = data.get("kind")
        if is_skill_payload_sidecar or is_knowledge_sidecar:
            if "kind" in data:
                problems.append(f"{path}: metadata-only sidecar must not define 'kind'")
            if is_knowledge_sidecar and "source" in data:
                problems.append(f"{path}: uploaded-knowledge sidecar must not define 'source'")
            if is_knowledge_sidecar and agent_schema:
                derived = f"{agent_schema}.file.{path.name[: -len('.mcs.yml')]}"
                if len(derived) > SCHEMA_NAME_LIMIT:
                    problems.append(f"{path}: derived schema name '{derived}' exceeds {SCHEMA_NAME_LIMIT} chars")
        else:
            if not isinstance(kind, str) or not kind:
                problems.append(f"{path}: missing 'kind'")
            elif TOPIC_KIND_RE.search(kind):
                problems.append(f"{path}: topic component kind '{kind}' is not allowed in a CLI agent")

        # Inline skill: frontmatter lives inside `content:`
        if parts and parts[0] == "behaviors" and kind == "InlineAgentSkill" and "content" in data:
            fm = parse_frontmatter(str(data.get("content") or ""))
            check_skill_frontmatter(fm, parts[1], f"{path} (content)", problems)

    behaviors = agent_dir / "behaviors"
    if behaviors.is_dir():
        for skill_dir in sorted(p for p in behaviors.iterdir() if p.is_dir()):
            manifest = skill_dir / "SKILL.md"
            if manifest.is_file():
                checked += 1
                try:
                    text = manifest.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    problems.append(f"{manifest}: must be UTF-8")
                    continue
                if text.startswith("﻿"):
                    problems.append(f"{manifest}: must not start with a byte-order mark")
                check_skill_frontmatter(parse_frontmatter(text.lstrip("﻿")), skill_dir.name, str(manifest), problems)

    return problems, checked


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    agent_dir = Path(argv[1])
    if not agent_dir.is_dir():
        print(f"error: {agent_dir} is not a directory", file=sys.stderr)
        return 2
    problems, checked = validate(agent_dir)
    if problems:
        print(f"FAIL: {len(problems)} problem(s) in {checked} file(s) checked")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"OK: {checked} file(s) checked, no problems")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
