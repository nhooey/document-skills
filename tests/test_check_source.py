"""Checks of the files the tests run on: every skill folder they see holds its `SKILL.md`.

`nix flake check` runs the tests as `checks.<system>.pytest` on a source narrowed to what the
tests may read, which includes each skill's `SKILL.md`. A narrower source would leave a test of
the skills nothing to read, so it would pass or fail on an empty list, not on the skills.

A skill-creator workspace, `skills/<skill>-workspace/`, is scratch that `.gitignore` keeps out of
the repository, not a skill.

Run them in the dev shell with `doc-skills test`.
"""

from __future__ import annotations

from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"

SKILL_DIRS = sorted(
    path for path in SKILLS.glob("*") if path.is_dir() and not path.name.endswith("-workspace")
)


def test_skill_dirs_exist() -> None:
    assert SKILL_DIRS, f"no skill folder under {SKILLS}"


def test_every_skill_dir_holds_skill_md() -> None:
    missing = [path.name for path in SKILL_DIRS if not (path / "SKILL.md").is_file()]
    assert not missing, f"skill folders under {SKILLS} without a SKILL.md: {missing}"
