"""Checks of every skill's SKILL.md frontmatter: its name and the description a skill listing shows.

The Agent Skills specification caps `description` at 1,024 characters. A skill listing shows
only each skill's description, cuts a long one short and drops descriptions when it overflows,
so a trigger-first skill's description leads with when to load the skill and stays short.

Run them in the dev shell with `doc-skills test`; `nix flake check` runs them as
`checks.<system>.pytest`.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

SKILLS = Path(__file__).resolve().parents[1] / "skills"

DESCRIPTION_LIMIT = 1024

# Skills whose description leads with when to load them and stays within TRIGGER_FIRST_LIMIT.
TRIGGER_FIRST = ("markdown-hygiene-terminal-rendering",)
TRIGGER_FIRST_PREFIX = "Load before "
TRIGGER_FIRST_LIMIT = 500

SKILL_NAMES = sorted(path.name for path in SKILLS.iterdir() if path.is_dir())


def parse_frontmatter(text: str) -> dict:
    """The YAML mapping between a SKILL.md's opening `---` line and the next `---` line."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md does not open with a `---` line")
    if "---" not in lines[1:]:
        raise ValueError("SKILL.md's frontmatter has no closing `---` line")
    meta = yaml.safe_load("\n".join(lines[1 : lines.index("---", 1)]))
    if not isinstance(meta, dict):
        raise ValueError(f"SKILL.md's frontmatter is a {type(meta).__name__}, not a mapping")
    return meta


def frontmatter(skill: str) -> dict:
    """The skill's parsed SKILL.md frontmatter."""
    skill_md = SKILLS / skill / "SKILL.md"
    assert skill_md.is_file(), f"skills/{skill} has no SKILL.md"
    return parse_frontmatter(skill_md.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("text", "meta"),
    [
        pytest.param(
            "---\nname: a\ndescription: b c\n---\n\n# A\n",
            {"name": "a", "description": "b c"},
            id="good document",
        ),
        pytest.param(
            "---\nname: a\n---\n\n# A\n\n---\n\nB\n",
            {"name": "a"},
            id="a --- line in the body is not the frontmatter's end",
        ),
    ],
)
def test_parse_frontmatter_reads_between_the_markers(text: str, meta: dict) -> None:
    assert parse_frontmatter(text) == meta


@pytest.mark.parametrize(
    ("text", "message"),
    [
        pytest.param("name: a\n---\n", "does not open with", id="no opening ---"),
        pytest.param("---\nname: a\n\n# A\n", "no closing", id="no closing ---"),
        pytest.param("---\n- a\n- b\n---\n", "is a list, not a mapping", id="a list"),
        pytest.param("---\n---\n", "is a NoneType, not a mapping", id="empty frontmatter"),
    ],
)
def test_parse_frontmatter_rejects(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_frontmatter(text)


def test_skills_exist() -> None:
    assert SKILL_NAMES, f"no skill folder under {SKILLS}"


@pytest.mark.parametrize("skill", SKILL_NAMES)
def test_frontmatter_names_the_skill_and_describes_it(skill: str) -> None:
    meta = frontmatter(skill)
    assert meta.get("name") == skill, f"name is {meta.get('name')!r}, not the folder's name"
    description = meta.get("description")
    assert isinstance(description, str), f"description is {description!r}, not a string"
    assert description.strip(), "description is empty"
    assert len(description) <= DESCRIPTION_LIMIT


@pytest.mark.parametrize("skill", TRIGGER_FIRST)
def test_trigger_first_description_leads_with_when_to_load(skill: str) -> None:
    description = frontmatter(skill)["description"]
    assert description.startswith(TRIGGER_FIRST_PREFIX), description[:80]
    assert len(description) <= TRIGGER_FIRST_LIMIT
