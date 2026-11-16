"""Tests for scripts/box_table.py: unit tests of its pure functions, then the command itself.

Run from the skill directory with `python3 -I -B -m unittest discover -s tests`;
`nix flake check` runs them as `checks.<system>.box-table`.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "box_table.py"
sys.path.insert(0, str(SCRIPT.parent))

import box_table  # noqa: E402

VS16 = "️"  # emoji presentation selector
ZWJ = "‍"  # zero-width joiner
COMBINING_ACUTE = "́"


class WidthTest(unittest.TestCase):
    def test_ascii_counts_one_column_per_character(self) -> None:
        self.assertEqual(box_table.width("abc"), 3)

    def test_empty_string_is_zero(self) -> None:
        self.assertEqual(box_table.width(""), 0)

    def test_wide_emoji_counts_two(self) -> None:
        self.assertEqual(box_table.width("✅"), 2)
        self.assertEqual(box_table.width("🏃"), 2)

    def test_east_asian_wide_and_fullwidth_count_two(self) -> None:
        self.assertEqual(box_table.width("漢字"), 4)
        self.assertEqual(box_table.width("Ａ"), 2)

    def test_combining_mark_counts_zero(self) -> None:
        self.assertEqual(box_table.width("e" + COMBINING_ACUTE), 1)

    def test_zero_width_joiner_counts_zero(self) -> None:
        self.assertEqual(box_table.width(ZWJ), 0)

    def test_presentation_selector_widens_a_narrow_character_to_two(self) -> None:
        self.assertEqual(box_table.width("❤"), 1)
        self.assertEqual(box_table.width("❤" + VS16), 2)

    def test_presentation_selector_leaves_a_wide_character_at_two(self) -> None:
        self.assertEqual(box_table.width("✅" + VS16), 2)

    def test_presentation_selector_on_its_own_counts_zero(self) -> None:
        self.assertEqual(box_table.width(VS16), 0)

    def test_presentation_selector_widens_only_the_character_before_it(self) -> None:
        self.assertEqual(box_table.width("a❤" + VS16 + "b"), 4)


class PadTest(unittest.TestCase):
    def test_left_aligned_pads_on_the_right(self) -> None:
        self.assertEqual(box_table.pad("ab", 4, right=False), "ab  ")

    def test_right_aligned_pads_on_the_left(self) -> None:
        self.assertEqual(box_table.pad("ab", 4, right=True), "  ab")

    def test_pads_by_display_width_not_length(self) -> None:
        self.assertEqual(box_table.pad("✅", 4, right=False), "✅  ")


class ParseTest(unittest.TestCase):
    def test_splits_rows_on_newlines_and_cells_on_tabs(self) -> None:
        self.assertEqual(
            box_table.parse("a\tb\nc\td\n"),
            (("a", "b"), ("c", "d")),
        )

    def test_skips_blank_and_whitespace_only_lines(self) -> None:
        self.assertEqual(
            box_table.parse("a\tb\n\n   \nc\td\n"),
            (("a", "b"), ("c", "d")),
        )

    def test_keeps_empty_cells(self) -> None:
        self.assertEqual(box_table.parse("a\tb\n\td\n"), (("a", "b"), ("", "d")))

    def test_empty_input_has_no_rows(self) -> None:
        self.assertEqual(box_table.parse(""), ())

    def test_short_row_names_its_row_and_both_cell_counts(self) -> None:
        with self.assertRaises(box_table.RowError) as caught:
            box_table.parse("a\tb\nc\td\ne\n")
        self.assertEqual(str(caught.exception), "row 3 has 1 cells, the header has 2")

    def test_long_row_is_rejected_too(self) -> None:
        with self.assertRaises(box_table.RowError) as caught:
            box_table.parse("a\tb\nc\td\te\n")
        self.assertEqual(str(caught.exception), "row 2 has 3 cells, the header has 2")


class RightColumnsTest(unittest.TestCase):
    def test_parses_comma_separated_indexes(self) -> None:
        self.assertEqual(box_table.right_columns("0,2"), frozenset({0, 2}))

    def test_empty_spec_is_no_columns(self) -> None:
        self.assertEqual(box_table.right_columns(""), frozenset())

    def test_ignores_empty_entries(self) -> None:
        self.assertEqual(box_table.right_columns("1,, ,3"), frozenset({1, 3}))

    def test_rejects_a_non_number(self) -> None:
        with self.assertRaises(ValueError):
            box_table.right_columns("x")


class DrawTest(unittest.TestCase):
    def test_draws_header_rule_body_and_borders(self) -> None:
        rows = (("Name", "N"), ("ab", "10"), ("c", "2"))
        self.assertEqual(
            box_table.draw(rows, frozenset()),
            "\n".join(
                (
                    "┌──────┬────┐",
                    "│ Name │ N  │",
                    "├──────┼────┤",
                    "│ ab   │ 10 │",
                    "│ c    │ 2  │",
                    "└──────┴────┘",
                )
            ),
        )

    def test_right_aligns_only_the_named_columns(self) -> None:
        rows = (("Name", "N"), ("ab", "10"), ("c", "2"))
        lines = box_table.draw(rows, frozenset({1})).splitlines()
        self.assertEqual(lines[3], "│ ab   │ 10 │")
        self.assertEqual(lines[4], "│ c    │  2 │")
        self.assertEqual(lines[1], "│ Name │  N │")

    def test_header_only_table_has_no_body_lines(self) -> None:
        self.assertEqual(
            box_table.draw((("a",),), frozenset()),
            "┌───┐\n│ a │\n├───┤\n└───┘",
        )

    def test_every_line_has_the_same_display_width_with_wide_cells(self) -> None:
        rows = (("Step", "State"), ("1", "✅"), ("2", "❤" + VS16), ("3", "漢字"))
        widths = {box_table.width(line) for line in box_table.draw(rows, frozenset()).splitlines()}
        self.assertEqual(widths, {16})


class ProbeTest(unittest.TestCase):
    def test_reports_code_points_and_counted_width(self) -> None:
        self.assertTrue(box_table.probe("🔗").endswith("\nU+1F517: counted 2 columns wide"))

    def test_lists_every_code_point_of_a_sequence(self) -> None:
        self.assertTrue(
            box_table.probe("❤" + VS16).endswith("\nU+2764 U+FE0F: counted 2 columns wide")
        )

    def test_glyph_row_and_ascii_row_are_drawn_the_same_width(self) -> None:
        lines = box_table.probe("🔗").splitlines()
        self.assertEqual(lines[3], "│ 🔗🔗🔗 │             6 │")
        self.assertEqual(lines[4], "│ xxxxxx │             6 │")


class RenderTest(unittest.TestCase):
    def test_draws_the_rows_with_status_zero(self) -> None:
        status, text = box_table.render("a\tb\n1\t22\n", "1")
        self.assertEqual(status, 0)
        self.assertEqual(text.splitlines()[3], "│ 1 │ 22 │")

    def test_no_rows_is_an_error(self) -> None:
        self.assertEqual(box_table.render("\n\n", ""), (1, "box_table.py: no rows on stdin"))

    def test_row_with_wrong_cell_count_is_an_error(self) -> None:
        self.assertEqual(
            box_table.render("a\tb\nc\n", ""),
            (1, "box_table.py: row 2 has 1 cells, the header has 2"),
        )

    def test_bad_right_spec_is_an_error(self) -> None:
        status, text = box_table.render("a\tb\n", "x")
        self.assertEqual(status, 1)
        self.assertTrue(text.startswith("box_table.py: invalid literal for int()"))


def run(args: list[str], stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


class CommandTest(unittest.TestCase):
    def test_skill_example_prints_the_table_on_stdout(self) -> None:
        result = run(["--right", "2"], "Step\tState\tCount\n1\t✅\t12\n2\t🏃\t3\n")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            result.stdout,
            "\n".join(
                (
                    "┌──────┬───────┬───────┐",
                    "│ Step │ State │ Count │",
                    "├──────┼───────┼───────┤",
                    "│ 1    │ ✅    │    12 │",
                    "│ 2    │ 🏃    │     3 │",
                    "└──────┴───────┴───────┘",
                    "",
                )
            ),
        )

    def test_error_goes_to_stderr_with_exit_status_one(self) -> None:
        result = run([], "a\tb\nc\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "box_table.py: row 2 has 1 cells, the header has 2\n")

    def test_probe_does_not_parse_stdin(self) -> None:
        result = run(["--probe", "🔗"], "not\ta\ttable\nx\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("U+1F517: counted 2 columns wide", result.stdout)


if __name__ == "__main__":
    unittest.main()
