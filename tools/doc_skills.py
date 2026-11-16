#!/usr/bin/env python3
"""Work on this repository's skills: list them and run their tests.

A skill is a directory under `skills/` with a `SKILL.md`; its tests, if it has any, are stdlib
`unittest` files in a `tests/` directory beside its `scripts/`.

    doc-skills list                     # every skill, and whether it has tests
    doc-skills test                     # run every skill's tests
    doc-skills test NAME... --verbose   # run the named skills' tests, one line per test

The repository root is `--root`, else `$PRJ_ROOT` (set by the dev shell), else the current
directory. Exits 0 when every suite passes, 1 when one fails, and 2 on a usage error or an
unknown skill name.

Standard library only.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    has_tests: bool


class UnknownSkill(Exception):
    """A skill name given on the command line that isn't a skill under `skills/`."""


def find_skills(root: Path) -> tuple[Skill, ...]:
    """The skills under `root/skills`, sorted by name."""
    base = root / "skills"
    if not base.is_dir():
        return ()
    return tuple(
        Skill(path.name, path, (path / "tests").is_dir())
        for path in sorted(base.iterdir())
        if (path / "SKILL.md").is_file()
    )


def select(skills: tuple[Skill, ...], names: list[str]) -> tuple[Skill, ...]:
    """The named skills in the order given, or every skill with tests when no name is given."""
    if not names:
        return tuple(s for s in skills if s.has_tests)
    by_name = {s.name: s for s in skills}
    unknown = [n for n in names if n not in by_name]
    if unknown:
        raise UnknownSkill(", ".join(unknown))
    return tuple(by_name[n] for n in names)


def unittest_command(python: str, verbose: bool) -> list[str]:
    """The command that runs a skill's tests from its directory."""
    return [python, "-I", "-B", "-m", "unittest", "discover", "-s", "tests"] + (
        ["-v"] if verbose else []
    )


def list_lines(skills: tuple[Skill, ...]) -> list[str]:
    size = max((len(s.name) for s in skills), default=0)
    return [f"{s.name:<{size}}  {'tests' if s.has_tests else '-'}" for s in skills]


def default_root() -> Path:
    return Path(os.environ.get("PRJ_ROOT") or Path.cwd())


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(prog="doc-skills", description=__doc__.split("\n")[0])
    top.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (default: $PRJ_ROOT, else the current directory)",
    )
    commands = top.add_subparsers(dest="command", required=True, metavar="COMMAND")
    commands.add_parser("list", help="list every skill and whether it has tests")
    test = commands.add_parser("test", help="run skills' unittest suites")
    test.add_argument("names", nargs="*", metavar="NAME", help="skills to test (default: all)")
    test.add_argument("-v", "--verbose", action="store_true", help="print one line per test")
    return top


def run_tests(skills: tuple[Skill, ...], verbose: bool) -> int:
    failed = []
    for skill in skills:
        if not skill.has_tests:
            print(f"== {skill.name}: no tests", file=sys.stderr)
            continue
        print(f"== {skill.name}", file=sys.stderr, flush=True)
        result = subprocess.run(unittest_command(sys.executable, verbose), cwd=skill.path)
        if result.returncode != 0:
            failed.append(skill.name)
    if failed:
        print(f"failed: {', '.join(failed)}", file=sys.stderr)
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ns = parser().parse_args(argv)
    skills = find_skills(ns.root or default_root())
    if ns.command == "list":
        print("\n".join(list_lines(skills)))
        return 0
    try:
        chosen = select(skills, ns.names)
    except UnknownSkill as error:
        print(f"doc-skills: unknown skill: {error}", file=sys.stderr)
        return 2
    return run_tests(chosen, ns.verbose)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
