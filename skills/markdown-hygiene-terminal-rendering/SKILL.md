---
name: markdown-hygiene-terminal-rendering
description: |
  Write Markdown that reads correctly in a terminal, where it is shown raw
  or only partly rendered on a grid of fixed-width columns. Write tables
  as plain Markdown tables with padded source columns, never in a code
  block, and let the terminal renderer draw them. Check a new glyph's
  rendered width before putting it in an underline or a table
  (`scripts/box_table.py --probe`). Part multi-line list items with a
  separator line holding the list's indent and U+2800, because blank and
  whitespace lines collapse.
  End a header line with a hard line break (2 trailing spaces) before an
  underline. Write every URL as a Markdown link, never bare, and never
  inside a code block. Use whenever writing Markdown that a
  person will read in a terminal: a coding agent's replies, CLI output,
  commit and tag messages read with `git log`, READMEs read with `cat` or
  `less`, and notes in a terminal pager.
tags: [markdown, terminal, writing]
---

# Markdown in a terminal

A terminal draws text on a grid of fixed-width columns. Markdown sent to it
is either printed raw or passed through a renderer that handles some syntax
(emphasis, links, lists, tables) and not the rest. Either way, some of what
a browser would lay out for you is now your job: the gaps between items,
where a line breaks, the width of each glyph, and which text can be
clicked. The rules below make
the source read well raw and render well in the terminal renderers in
common use.

## How to load this skill

Passive reference. Load it whenever the reader will see your Markdown in a
terminal; it applies on top of ordinary Markdown syntax, so load
`markdown-hygiene-lists-headings-tables` and
`markdown-hygiene-escape-reserved-characters` beside it.

## Tables: plain Markdown tables

A terminal renderer that handles GitHub-flavored Markdown tables, as a
coding agent's terminal interface does, draws the borders, makes the
header row bold and wraps long cells to the window. Write a plain Markdown
table and let it:

```markdown
| Step | State | Count |
| ---- | ----- | ----: |
| 1    | ✅    |    12 |
| 2    | 🏃    |     3 |
```

- **The syntax:** a header row, a delimiter row and the body rows, as
  `markdown-hygiene-lists-headings-tables` says.
- **Right-align numbers** with `---:` in the delimiter row, so their digits
  line up.
- **Pad the source columns** to their widest cell, so the table also reads
  where it is shown raw.
- **Links in a cell** are fine: the renderer makes them clickable there as
  anywhere else. Keep the label short, since a label that wraps across
  lines of a cell can stop being clickable.
- **Short cells.** A cell of a few words keeps each row on a line or two;
  move longer text to a note under the table.
- **Not inside a code block.** A table in a fenced block is printed as
  raw `|` and `---`.

## Glyph widths: check before you use one

A terminal decides each glyph's width itself, and terminals disagree,
especially about emoji, symbols with an "ambiguous" East Asian width, and
emoji sequences. A glyph drawn at a width other than the one counted for it
pushes an underline past its header, shifts a padded source column, and can
put a rendered table's borders out of line, since the renderer counts
widths its own way.

- **Count terminal columns, not characters:** an emoji or a CJK character
  is 2 columns, a combining mark or zero-width joiner 0, and a character
  followed by U+FE0F (the emoji presentation selector, as in `⚠️`) 2.
- **Check each new glyph** in the terminals your readers use before putting
  it in a table or an underline. `scripts/box_table.py --probe GLYPH` draws
  a small table with the glyph in one row and ASCII in the others, and
  prints the width the script counts: if the right-hand borders don't line
  up on screen, that terminal draws the glyph at a different width.

  ```bash
  python3 -I scripts/box_table.py --probe '🔗'
  ```

- **Prefer single-code-point emoji** whose East Asian width is W (most
  emoji from U+1F300 up, ✅, ❌, ⏳). Avoid in tables:
  - zero-width-joiner sequences (👩‍💻), flags (🇨🇦) and skin-tone variants,
    which some terminals draw as 2 columns and others as 4 to 6;
  - symbols of ambiguous width (①, `→` in some fonts, Greek and Cyrillic in
    CJK locales), which are 1 column in most terminals and 2 in others;
  - a symbol that needs U+FE0F to become an emoji (`⚠️`, `❤️`), which some
    terminals draw at 1 column regardless.
- **Keep a short list of checked glyphs** per document or tool and use only
  those; a new one is checked first.
- **A 1-column glyph alone on its line is safe**, since no alignment depends
  on it; the separator character below is one.

## Separator lines between multi-line list items

Items that each run to several lines (an item with a note, sub-items or
options under it) run together in a terminal unless something parts them.
The usual Markdown answer, a blank line, doesn't survive:

- **An empty line** between items is folded away by terminal renderers,
  which treat the list as loose or simply drop it: no gap.
- **A line of spaces** renders a gap or none, depending on its width and
  the renderer.
- **A no-break space (U+00A0)** typed on that line often reaches the
  terminal as a plain space, so it fails the same way.

What works is a line that is not whitespace but draws as nothing: the
list's indent, then **U+2800 BRAILLE PATTERN BLANK** (`⠀`), and nothing
else.

- **The indent** is the column the items' text starts at: 3 spaces under
  `1. `, 2 under `- `. At any other indent the line ends the list or
  attaches to the wrong item.
- **Directly under the item's last line**, with no blank line above or
  below it. A blank line beside it renders a double gap.
- **Only where an item is multi-line.** A run of one-line items stays
  together, with no separator, and the first item follows the list's lead-in
  or header with none.
- **It renders one gap** after a simple item, after a loose item with blank
  lines inside it, and after an item ending in a nested list alike.

```text
1. **First decision:** the summary line.
   A note under the summary.
   ⠀
2. **Second decision:** the summary line.
   - an option
   - another option
   ⠀
3. **A one-line item.**
4. **Another one-line item.**
```

U+2800 is invisible in most editors too, so check a draft by searching for
the character (`grep -n $'\u2800'` in bash or zsh) rather than by eye.

## Header lines and hard line breaks

A single newline is a soft break, which a renderer joins into one line with
a space. A header line followed by a decorative underline, a label line
followed by its value, or any two lines that must stay two lines, needs a
**hard line break: 2 trailing spaces** at the end of the first line (a
trailing backslash also works in CommonMark but shows as a literal `\` when
printed raw).

```text
**Waiting:**··
▔▔▔▔▔▔▔▔▔▔▔▔
```

(`··` stands for the 2 trailing spaces.) An underline drawn with a glyph
such as `▔` U+2594 or `━` U+2501 takes one glyph per column of the header
line, counting each emoji in the header as 2, so it ends exactly under the
header's last character. Check that your editor or formatter keeps trailing
spaces in the files where you rely on them.

## Links

- **Every URL is a Markdown link** with a label that says what it opens:
  `[the trial projection](http://127.0.0.1:8765/projection)`. Most
  terminals and terminal renderers make it clickable and show only the
  label. A local served page needs this as much as a web page.
- **Never a bare URL.** A long one wraps across lines and stops being
  clickable, and the reader can't tell what it opens until they open it.
- **Never inside a code block**, where it is printed as text and can't be
  clicked. A Markdown table's cell can hold a link (see Tables above).

- **Text the reader copies** (a command, a prompt, a config snippet) stays
  in its code block, URL included: there the point is copying the exact
  text, not clicking.

## When to apply

- Writing Markdown that a person reads in a terminal: a coding agent's
  replies, CLI output, commit and tag messages, a README read with `cat`,
  `less` or `glow`.
- Putting a table, an emoji, a decorative underline or a link into such
  text.
- A list's items run together, a table's borders don't line up, or a link
  can't be clicked in the terminal.

## Related skills

When one of these applies and it's in your skill listing, load it
without asking. If it isn't in your listing, tell the user which skill is
missing and ask whether to install it from the same collection this skill
came from; don't apply it from memory.

- `markdown-hygiene-lists-headings-tables`: the Markdown syntax for lists, headings and tables these rules build on.
- `markdown-hygiene-escape-reserved-characters`: escaping characters that Markdown would read as formatting.
- `coding-agent-kanban-turn-responses`: an agent's turn responses, which apply these rules to their lists, tables and links.
