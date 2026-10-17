#!/usr/bin/env python3
"""Draw tab-separated rows from stdin as a table of box-drawing lines.

Why it exists: a Markdown table's `|` and `---` show as a grid of loose dashes in a terminal that
prints Markdown raw or only half renders it, so a table read in a terminal is drawn in a `text`
block with `┌ ┬ ┐ ├ ┼ ┤ └ ┴ ┘ ─ │`, which join with no gaps. Padding its columns by hand goes wrong
on an emoji, which a terminal draws 2 columns wide.

Takes: rows on stdin, cells separated by a tab, the first row the header, blank lines skipped.
Every row must have as many cells as the header, or the script exits 1 naming the row. A column
is padded to its widest cell, where a character of East Asian width W or F counts 2 columns, a
combining mark or format character (a zero-width joiner, a variation selector) 0, and a
character followed by U+FE0F, the emoji presentation selector, 2. `--right N,M` right-aligns
those 0-based columns, for numbers.

    printf 'Run\\tState\\n1\\t✅\\n' | python3 -I scripts/box_table.py --right 0

`--probe GLYPH` draws a table with GLYPH in one row and ASCII in the others, and prints the
width this script counts for it: if the right-hand borders of the drawn table don't line up in
your terminal, the terminal draws GLYPH at a different width, and it doesn't belong in a table.

    python3 -I scripts/box_table.py --probe '🔗'

Standard library only.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata

EMOJI_PRESENTATION = "️"


class RowError(Exception):
    """A row whose cell count differs from the header's."""


def char_width(char: str) -> int:
    if unicodedata.combining(char) or unicodedata.category(char) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(char) in "WF" else 1


def width(text: str) -> int:
    total = 0
    previous = 0
    for char in text:
        if char == EMOJI_PRESENTATION and previous == 1:
            total += 1
            previous = 2
            continue
        previous = char_width(char)
        total += previous
    return total


def pad(text: str, size: int, right: bool) -> str:
    gap = " " * (size - width(text))
    return gap + text if right else text + gap


def parse(text: str) -> tuple[tuple[str, ...], ...]:
    rows = tuple(tuple(line.split("\t")) for line in text.splitlines() if line.strip())
    bad = next(((i, r) for i, r in enumerate(rows) if len(r) != len(rows[0])), None)
    if bad:
        raise RowError(f"row {bad[0] + 1} has {len(bad[1])} cells, the header has {len(rows[0])}")
    return rows


def rule(sizes: tuple[int, ...], left: str, middle: str, right: str) -> str:
    return left + middle.join("─" * (s + 2) for s in sizes) + right


def draw(rows: tuple[tuple[str, ...], ...], right_columns: frozenset[int]) -> str:
    sizes = tuple(max(width(r[i]) for r in rows) for i in range(len(rows[0])))

    def line(row: tuple[str, ...]) -> str:
        cells = (pad(c, sizes[i], i in right_columns) for i, c in enumerate(row))
        return "│ " + " │ ".join(cells) + " │"

    return "\n".join(
        (
            rule(sizes, "┌", "┬", "┐"),
            line(rows[0]),
            rule(sizes, "├", "┼", "┤"),
            *(line(r) for r in rows[1:]),
            rule(sizes, "└", "┴", "┘"),
        )
    )


def probe(glyph: str) -> str:
    counted = width(glyph)
    rows = (
        ("Glyph", "Counted width"),
        (glyph * 3, str(counted * 3)),
        ("x" * (counted * 3), str(counted * 3)),
    )
    points = " ".join(f"U+{ord(c):04X}" for c in glyph)
    return f"{draw(rows, frozenset({1}))}\n{points}: counted {counted} columns wide"


def right_columns(spec: str) -> frozenset[int]:
    return frozenset(int(n) for n in spec.split(",") if n.strip())


def main(argv: list[str]) -> tuple[int, str]:
    args = argparse.ArgumentParser(prog="box_table.py", description=__doc__.split("\n")[0])
    args.add_argument("--right", default="", metavar="N,M", help="0-based columns to right-align")
    args.add_argument("--probe", metavar="GLYPH", help="draw a test table to check GLYPH's width")
    ns = args.parse_args(argv)
    if ns.probe:
        return 0, probe(ns.probe)
    try:
        rows = parse(sys.stdin.read())
        result = (
            (0, draw(rows, right_columns(ns.right)))
            if rows
            else (1, "box_table.py: no rows on stdin")
        )
    except (RowError, ValueError) as error:
        result = (1, f"box_table.py: {error}")
    return result


if __name__ == "__main__":
    status, text = main(sys.argv[1:])
    print(text, file=sys.stdout if status == 0 else sys.stderr)
    sys.exit(status)
