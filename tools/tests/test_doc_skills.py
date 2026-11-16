"""Tests for tools/doc_skills.py: its argument parsing, its pure functions, then the command.

Run from the `tools/` directory with `python3 -I -B -m unittest discover -s tests`;
`nix flake check` runs them as `checks.<system>.doc-skills`.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "doc_skills.py"
sys.path.insert(0, str(SCRIPT.parent))

import doc_skills  # noqa: E402

PASSING = "import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n"
FAILING = "import unittest\n\nclass T(unittest.TestCase):\n    def test_no(self):\n        self.fail()\n"


def make_repo(base: Path, skills: dict[str, str | None]) -> Path:
    """A repository under `base` with one skill per entry; the value is its test file, or None."""
    for name, test in skills.items():
        skill = base / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"# {name}\n")
        if test is not None:
            (skill / "tests").mkdir()
            (skill / "tests" / "test_it.py").write_text(test)
    return base


class ParserTest(unittest.TestCase):
    def test_a_command_is_required(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            doc_skills.parser().parse_args([])
        self.assertEqual(raised.exception.code, 2)

    def test_unknown_command_is_a_usage_error(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            doc_skills.parser().parse_args(["build"])
        self.assertEqual(raised.exception.code, 2)

    def test_list_takes_no_names(self) -> None:
        ns = doc_skills.parser().parse_args(["list"])
        self.assertEqual(ns.command, "list")
        self.assertIsNone(ns.root)

    def test_test_defaults_to_no_names_and_quiet(self) -> None:
        ns = doc_skills.parser().parse_args(["test"])
        self.assertEqual((ns.command, ns.names, ns.verbose), ("test", [], False))

    def test_test_takes_names_and_verbose(self) -> None:
        ns = doc_skills.parser().parse_args(["test", "a", "b", "-v"])
        self.assertEqual((ns.names, ns.verbose), (["a", "b"], True))

    def test_root_comes_before_the_command(self) -> None:
        ns = doc_skills.parser().parse_args(["--root", "/r", "list"])
        self.assertEqual(ns.root, Path("/r"))

    def test_help_lists_the_command_tokens(self) -> None:
        text = doc_skills.parser().format_help()
        self.assertIn("list", text)
        self.assertIn("test", text)
        self.assertIn("--root", text)


class FindSkillsTest(unittest.TestCase):
    def test_finds_skills_sorted_and_notes_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), {"b": PASSING, "a": None})
            found = doc_skills.find_skills(root)
        self.assertEqual([(s.name, s.has_tests) for s in found], [("a", False), ("b", True)])

    def test_skips_a_directory_without_skill_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), {"a": None})
            (root / "skills" / "a-workspace").mkdir()
            found = doc_skills.find_skills(root)
        self.assertEqual([s.name for s in found], ["a"])

    def test_no_skills_directory_is_no_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(doc_skills.find_skills(Path(tmp)), ())


class SelectTest(unittest.TestCase):
    SKILLS = (
        doc_skills.Skill("a", Path("a"), False),
        doc_skills.Skill("b", Path("b"), True),
        doc_skills.Skill("c", Path("c"), True),
    )

    def test_no_names_selects_every_skill_with_tests(self) -> None:
        self.assertEqual([s.name for s in doc_skills.select(self.SKILLS, [])], ["b", "c"])

    def test_names_select_in_the_order_given(self) -> None:
        chosen = doc_skills.select(self.SKILLS, ["c", "a"])
        self.assertEqual([s.name for s in chosen], ["c", "a"])

    def test_unknown_names_raise_naming_them(self) -> None:
        with self.assertRaisesRegex(doc_skills.UnknownSkill, "x, y"):
            doc_skills.select(self.SKILLS, ["a", "x", "y"])


class PureTest(unittest.TestCase):
    def test_unittest_command(self) -> None:
        self.assertEqual(
            doc_skills.unittest_command("py", False),
            ["py", "-I", "-B", "-m", "unittest", "discover", "-s", "tests"],
        )
        self.assertEqual(doc_skills.unittest_command("py", True)[-1], "-v")

    def test_list_lines_pad_names(self) -> None:
        skills = (doc_skills.Skill("a", Path("a"), True), doc_skills.Skill("ccc", Path("c"), False))
        self.assertEqual(doc_skills.list_lines(skills), ["a    tests", "ccc  -"])


class CommandTest(unittest.TestCase):
    def run_tool(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", "-B", str(SCRIPT), "--root", str(root), *args],
            capture_output=True,
            text=True,
        )

    def test_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_tool(make_repo(Path(tmp), {"a": PASSING, "b": None}), "list")
        self.assertEqual((result.returncode, result.stdout), (0, "a  tests\nb  -\n"))

    def test_passing_suites_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_tool(make_repo(Path(tmp), {"a": PASSING, "b": None}), "test")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_failing_suite_exits_one_and_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_tool(make_repo(Path(tmp), {"a": PASSING, "b": FAILING}), "test")
        self.assertEqual(result.returncode, 1)
        self.assertIn("failed: b", result.stderr)

    def test_an_unknown_skill_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_tool(make_repo(Path(tmp), {"a": PASSING}), "test", "nope")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown skill: nope", result.stderr)


if __name__ == "__main__":
    unittest.main()
