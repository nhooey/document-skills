"""Checks of the repository's layout that hold for every skill.

An installed skill ships only what it runs, so no test sits under `skills/`, and its scripts
run on any Python 3, so they import only the standard library and each other.
"""

from __future__ import annotations

import ast
import sys
from fnmatch import fnmatch
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

TEST_FILES = ("test_*", "*_test.*", "*.bats")
TEST_DIRECTORIES = ("tests", "test")


def is_test_path(path: Path) -> bool:
    if path.is_dir():
        return path.name in TEST_DIRECTORIES
    return any(fnmatch(path.name, pattern) for pattern in TEST_FILES)


def absolute_imports(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
        return [node.module]
    return []


def imported_modules(source: str) -> frozenset[str]:
    """The top-level names of the absolute imports in `source`."""
    return frozenset(
        name.split(".")[0] for node in ast.walk(ast.parse(source)) for name in absolute_imports(node)
    )


def sibling_modules(directory: Path) -> frozenset[str]:
    """The modules a script in `directory` can import from beside it."""
    return frozenset(
        path.stem if path.suffix == ".py" else path.name
        for path in directory.iterdir()
        if path.suffix == ".py" or (path / "__init__.py").is_file()
    )


def test_no_test_sits_under_skills() -> None:
    misplaced = sorted(
        str(path.relative_to(ROOT)) for path in SKILLS.rglob("*") if is_test_path(path)
    )
    assert misplaced == [], "move these to tests/<skill>/"


SCRIPTS = sorted(SKILLS.glob("*/scripts/**/*.py"))


@pytest.mark.parametrize("script", SCRIPTS, ids=[str(s.relative_to(SKILLS)) for s in SCRIPTS])
def test_skill_scripts_import_only_the_standard_library(script: Path) -> None:
    allowed = sys.stdlib_module_names | sibling_modules(script.parent)
    assert sorted(imported_modules(script.read_text(encoding="utf-8")) - allowed) == []
