"""Checks of every skill's "Your preferences" section: its command line reads both preferences files.

An installed skill's folder is often a symlink into the Nix store, `~/.claude/skills/<skill> ->
/nix/store/…/<skill>`, with the user's `<skill>.preferences.md` beside the link. Claude Code puts
the link's path in place of `${CLAUDE_SKILL_DIR}`, so the line must find the user's file through
that path as written, not through the folder the link points to.

Run them in the dev shell with `doc-skills test`; `nix flake check` runs them as
`checks.<system>.pytest`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parents[1] / "skills"

SECTIONS = sorted(
    path
    for path in SKILLS.glob("*/SKILL.md")
    if "## Your preferences" in path.read_text(encoding="utf-8").splitlines()
)


def command_line(path: Path) -> str:
    """The command in the section's opening line: an exclamation mark and one code span."""
    lines = path.read_text(encoding="utf-8").splitlines()
    after = lines[lines.index("## Your preferences") + 1 :]
    line = next((line for line in after if line.strip()), "")
    assert line.startswith("!`") and line.endswith("`") and line.count("`") == 2, (
        f"{path}'s preferences section opens with {line!r}, not a `!` command line"
    )
    return line[2:-1]


def run(line: str, skill_dir: Path, project: Path) -> str:
    """The line's output, after Claude Code's textual substitution of the two variables."""
    script = line.replace("${CLAUDE_SKILL_DIR}", str(skill_dir)).replace(
        "${CLAUDE_PROJECT_DIR}", str(project)
    )
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True).stdout


def test_sections_exist() -> None:
    assert SECTIONS, f"no SKILL.md under {SKILLS} has a `## Your preferences` section"


@pytest.mark.parametrize("path", SECTIONS, ids=lambda path: path.parent.name)
def test_the_line_reads_both_files_through_a_symlinked_skill_folder(
    path: Path, tmp_path: Path
) -> None:
    skill = path.parent.name
    store = tmp_path / "nix" / "store" / "hash-skill" / "share" / "claude-skills" / skill
    store.mkdir(parents=True)
    skills = tmp_path / "home dir" / ".claude" / "skills"
    skills.mkdir(parents=True)
    (skills / skill).symlink_to(store, target_is_directory=True)
    (skills / f"{skill}.preferences.md").write_text("- User: yes\n", encoding="utf-8")
    project = tmp_path / "the project"
    (project / ".agents" / "skills").mkdir(parents=True)
    (project / ".agents" / "skills" / f"{skill}.preferences.md").write_text(
        "- Project: yes\n", encoding="utf-8"
    )

    assert run(command_line(path), skills / skill, project) == "- User: yes\n- Project: yes\n"


@pytest.mark.parametrize("path", SECTIONS, ids=lambda path: path.parent.name)
def test_the_line_prints_nothing_when_neither_file_exists(path: Path, tmp_path: Path) -> None:
    skill_dir = tmp_path / "home dir" / ".claude" / "skills" / path.parent.name
    skill_dir.mkdir(parents=True)
    assert run(command_line(path), skill_dir, tmp_path / "the project") == ""
