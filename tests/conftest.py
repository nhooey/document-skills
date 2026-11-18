"""Setup shared by every test under `tests/`.

A skill's tests sit in `tests/<skill>/` and import the skill's scripts by module name: before
pytest imports a test module there, `skills/<skill>/scripts/` goes first on `sys.path`.

The folder stays on `sys.path` for the rest of the run, and Python imports a module name once,
so two skills whose scripts share a module name would share whichever was imported first; give
skill scripts names unique across the repository.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
SKILLS = TESTS.parent / "skills"


def skill_of(path: Path) -> str | None:
    """The skill a test file under `tests/<skill>/` belongs to, or None for a repository test."""
    parts = path.resolve().relative_to(TESTS).parts
    return parts[0] if len(parts) > 1 else None


def pytest_collectstart(collector: pytest.Collector) -> None:
    if not isinstance(collector, pytest.Module):
        return
    skill = skill_of(collector.path)
    scripts = str(SKILLS / skill / "scripts") if skill else None
    if scripts and Path(scripts).is_dir() and scripts not in sys.path:
        sys.path.insert(0, scripts)
