"""Tests for tools/validate_agent.py.

One passing fixture lives in tests/fixtures/agent-ok/. Each failing case copies it to a temp
folder and breaks exactly one rule, so every rule in the validator has a dedicated test.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "validate_agent.py"
OK_FIXTURE = ROOT / "tests" / "fixtures" / "agent-ok"


def run(agent_dir: Path):
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), str(agent_dir)], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout + proc.stderr


@pytest.fixture
def agent(tmp_path):
    dst = tmp_path / "agent"
    shutil.copytree(OK_FIXTURE, dst)
    return dst


def test_ok_fixture_passes():
    code, out = run(OK_FIXTURE)
    assert code == 0, out
    assert out.startswith("OK:")


def test_real_agent_passes():
    agent_dir = ROOT / "agent"
    if not agent_dir.is_dir():
        pytest.skip("agent/ not created yet")
    code, out = run(agent_dir)
    assert code == 0, out


def _replace(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new), encoding="utf-8")


def _expect_fail(agent_dir: Path, needle: str):
    code, out = run(agent_dir)
    assert code == 1, out
    assert needle in out, out


def test_invalid_yaml(agent):
    (agent / "behaviors/demo-skill/scripts/demo.py.mcs.yml").write_text("mcs.metadata: [unclosed\n")
    _expect_fail(agent, "invalid YAML")


def test_missing_component_name(agent):
    _replace(agent / "behaviors/demo-skill/skill.mcs.yml", "componentName: demo-skill", "description2: x")
    _expect_fail(agent, "componentName")


def test_component_name_yaml11_boolean(agent):
    _replace(agent / "behaviors/demo-skill/scripts/demo.py.mcs.yml", "componentName: ./scripts/demo.py", "componentName: on")
    _expect_fail(agent, "componentName must be a non-empty string")


def test_missing_kind(agent):
    _replace(agent / "behaviors/demo-skill/skill.mcs.yml", "kind: InlineAgentSkill\n", "")
    _expect_fail(agent, "missing 'kind'")


def test_sidecar_with_kind(agent):
    p = agent / "behaviors/demo-skill/scripts/demo.py.mcs.yml"
    p.write_text(p.read_text() + "kind: File\n")
    _expect_fail(agent, "must not define 'kind'")


def test_knowledge_sidecar_with_source(agent):
    p = agent / "capabilities/knowledge/files/notes_a1B2c3.mcs.yml"
    p.write_text(p.read_text() + "source:\n  kind: X\n")
    _expect_fail(agent, "must not define 'source'")


def test_template_not_cli(agent):
    _replace(agent / "settings.mcs.yml", "template: cliagent-1.0.0", "template: default-2.1.0")
    _expect_fail(agent, "template must start with 'cliagent-'")


def test_authoring_model(agent):
    _replace(agent / "settings.mcs.yml", "authoringModel: CliCopilot", "authoringModel: Classic")
    _expect_fail(agent, "authoringModel")


def test_empty_instructions(agent):
    _replace(agent / "settings.mcs.yml", '"Fixture instructions."', '""')
    _expect_fail(agent, "instructions are empty")


def test_topics_folder(agent):
    (agent / "topics").mkdir()
    _expect_fail(agent, "topics are not allowed")


def test_topic_kind(agent):
    (agent / "behaviors/greeting.mcs.yml").write_text(
        "mcs.metadata:\n  componentName: Greeting\nkind: AdaptiveDialog\n"
    )
    _expect_fail(agent, "topic component kind")


def test_skill_name_mismatch(agent):
    _replace(agent / "behaviors/demo-skill/SKILL.md", "name: demo-skill", "name: other-skill")
    _expect_fail(agent, "must equal folder")


def test_skill_name_format(agent):
    shutil.move(agent / "behaviors/demo-skill", agent / "behaviors/Demo_Skill")
    _replace(agent / "behaviors/Demo_Skill/SKILL.md", "name: demo-skill", "name: Demo_Skill")
    _expect_fail(agent, "lowercase letters, digits and single hyphens")


def test_skill_description_multiline(agent):
    _replace(
        agent / "behaviors/demo-skill/SKILL.md",
        "description: Demo skill used by the validator tests.",
        "description: |\n  line one\n  line two",
    )
    _expect_fail(agent, "single line")


def test_skill_description_too_long(agent):
    _replace(
        agent / "behaviors/demo-skill/SKILL.md",
        "description: Demo skill used by the validator tests.",
        "description: " + "x" * 1025,
    )
    _expect_fail(agent, "max 1024")


def test_skill_missing_frontmatter(agent):
    (agent / "behaviors/demo-skill/SKILL.md").write_text("No frontmatter here.\n")
    _expect_fail(agent, "missing or invalid YAML frontmatter")


def test_schema_name_too_long(agent):
    _replace(
        agent / "behaviors/demo-skill/skill.mcs.yml",
        "schemaName: catmgr_FixtureAgent.skill.demoskill_Ab1",
        "schemaName: catmgr_FixtureAgent.skill." + "a" * 80 + "_Ab1",
    )
    _expect_fail(agent, "max 100")


def test_knowledge_sidecar_derived_schema_too_long(agent):
    src = agent / "capabilities/knowledge/files/notes_a1B2c3.mcs.yml"
    shutil.move(src, src.with_name("n" * 80 + "_a1B2c3.mcs.yml"))
    _expect_fail(agent, "derived schema name")
