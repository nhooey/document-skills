---
name: markdown-hygiene-lists-headings-tables
description: |
  The Markdown syntax for lists, headings and tables, so the structure you
  chose renders as you meant it. Lists: one marker per list, nesting by the
  parent's text column, ordered lists for sequences, a lead-in colon, blank
  lines around the list, hard line breaks inside an item. Headings: ATX
  `#` syntax, one H1, no skipped levels, no closing period, a real heading
  rather than a bold line so it gets an anchor and a table-of-contents
  entry. Tables: header and delimiter rows, pipes and alignment colons,
  `\|` in cells, an explicit `—` or `N/A` for an empty cell, `<br/>` for a
  second line in a cell, ✅/❌ for genuinely binary cells, and a first
  column that links each item's name. Use whenever writing or reviewing
  Markdown that holds a list, a heading or a table. Deciding whether the
  content should be a list, a heading tree or a table is a writing
  question, covered by the writing-hygiene skills named inside.
tags: [markdown, writing]
---

# Markdown syntax for lists, headings and tables

Once you have decided that content is a list, an outline of headings or a
table, the remaining work is syntax: a renderer that reads the wrong indent,
a skipped heading level or a stray pipe silently produces a different
structure from the one you wrote. This skill is that syntax. Whether to use
a list, a heading or a table, and how to convert prose faithfully, is in
`writing-hygiene-prose-to-lists`, `writing-hygiene-headings-as-outline` and
`writing-hygiene-tables-for-comparison`.

## How to load this skill

Passive reference. Load it alongside the writing skill that chose the
structure, or on its own when reviewing Markdown whose lists, headings or
tables render wrong.

## Lists

- **One marker per list.** Use `-` for bullets throughout a document; a
  change of marker (`-` to `*`) starts a new list in CommonMark, which can
  add a gap or reset numbering.
- **Ordered lists for sequences and priorities.** Write `1.`, `2.`, `3.`.
  A list whose first number is not 1 starts at that number, and a renderer
  may renumber the rest, so number in order rather than relying on `1.` for
  every line.
- **Nest by the parent's text column.** A child item is indented to where
  the parent's text starts: 2 spaces under `- `, 3 under `1. `, 4 under
  `10. `. Fewer spaces and the child becomes a sibling; 4 or more beyond
  the parent's text and it becomes an indented code block.
- **Continuation lines and paragraphs inside an item** use the same indent
  as the item's text. An unindented line ends the item.
- **Blank lines around a list.** Put a blank line before the first item and
  after the last. Without the one before, some renderers (and every
  renderer, after a paragraph line ending in text) fold the first item into
  the paragraph above.
- **Tight and loose lists.** Blank lines between items make the whole list
  "loose", rendering each item as a paragraph with extra space. Keep items
  together unless they hold several paragraphs.
- **The lead-in line.** End the line before a list with a colon when it
  introduces the list; leave the colon off when the items complete its
  sentence.
- **Bold label, then text.** A list of labelled items reads as
  `- **Label:** text` or `- **Label** — text`; pick one form per list.

### Hard line breaks

A single newline inside a paragraph or list item is a soft break: it renders
as a space. To break the line without starting a new paragraph, end it with
**2 trailing spaces** or a backslash (`\`). Two spaces are invisible in the
source, and editors and formatters may strip them, so check that the file
keeps them. Use a hard break where line structure matters, such as a header
line followed by an underline, an address, or a label line above its
value.

## Headings

- **ATX syntax.** Write `#` to `######`, a space, then the text:
  `## Installation`. No space (`##Installation`) is not a heading in
  CommonMark. Leave the closing `#`s off.
- **One H1, the title.** Major sections are `##`, their sub-sections `###`.
  A second H1 flattens the outline.
- **Don't skip levels.** Go `##` to `###`, never `##` to `####`: a skipped
  level breaks the outline and table-of-contents generators.
- **Shallow nesting.** Past `####` the hierarchy is usually too fine to be
  useful.
- **No trailing period.** A heading is a label, not a sentence.
- **A blank line before and after** each heading, so it never merges with
  the paragraph next to it.
- **A real heading, not bold text.** A standalone `**Setup**` line looks
  like a heading but gets no anchor, no table-of-contents entry and no
  place in the outline. Promote it to `###`.
- **Anchors come from the text.** GitHub and most renderers derive a
  heading's anchor from its words (`## Install the CLI` is
  `#install-the-cli`). Renaming a heading breaks links to it, so search for
  the old anchor when you rename one.
- **Avoid setext headings** (text underlined with `===` or `---`). A line
  of `---` under a paragraph turns it into a heading by accident; ATX is
  unambiguous.

## Tables

### Structure

```markdown
| Database | Data model | Consistency |        Cost |
| -------- | ---------- | ----------- | ----------: |
| Postgres | Relational | ACID        |        Free |
| DynamoDB | Key-value  | Eventual    | Per-request |
```

- **A header row, then a delimiter row** with at least 3 dashes per column.
  Without the delimiter row it is not a table.
- **Leading and trailing pipes** on every row. They are optional in GFM but
  make the row boundaries unmistakable.
- **Alignment** goes in the delimiter row: `:---` left (the default),
  `:---:` centre, `---:` right. Right-align numbers so their digits line up.
- **The same number of cells in every row** as in the header. A row with
  fewer gets empty cells; a row with more loses the extra ones.
- **A blank line before the table.** Directly under a paragraph line some
  renderers read it as more paragraph.
- **Padding the source** so the pipes line up is optional for the renderer
  and kind to the next person reading the raw file; a formatter such as
  prettier does it for you. A table read raw, in a terminal, is a different
  case, covered in `markdown-hygiene-terminal-rendering`.

### Cells

- **One line of Markdown per cell.** A cell can't hold a list, a block
  quote or a code block; inline formatting (code spans, emphasis, links)
  works.
- **Escape a literal pipe** as `\|`, even inside a code span: many parsers
  split the row on `|` before reading spans.
- **An empty cell is never blank.** Write `—` or `N/A`, so "no", "unknown"
  and "same as above" can't be confused.
- **A second line in a cell** is `<br/>`, the one HTML tag GFM tables
  render reliably. Use it for a qualifier under the cell's main value:
  `✅<br/>Only on the Pro plan`. Never inline the qualifier after a dash
  (`✅ — only on Pro`): the symbol stops leading the cell.
- **Binary cells are ✅ and ❌.** A yes/no, supported/unsupported or
  included/excluded column holds ✅ or ❌, which the eye reads by shape and
  colour before reading any word; `Yes` and `No` must be read cell by cell.
  Only a column where every cell is genuinely yes or no gets them: a
  categorical value (a license, a switch type) or a number (a price, a
  weight) stays plain text.
- **The first column names the item, as a link.** Each row's first cell is
  the item's name, linked to its most relevant page: the official site or
  canonical docs, falling back to the source repository, a Wikipedia
  article or a product page. Not plain or bold text, and not a name linked
  only in the surrounding prose.

```markdown
| Keyboard                                     | Wireless                 | Hot-swappable switches |
| -------------------------------------------- | ------------------------ | ---------------------- |
| [Glove80](https://www.moergo.com/)           | ✅<br/>Bluetooth via ZMK | ✅                     |
| [Moonlander](https://www.zsa.io/moonlander/) | ❌<br/>USB-C only        | ✅                     |
| [HHKB Hybrid](https://hhkeyboard.us/)        | ✅<br/>Up to 4 devices   | ❌<br/>Topre, soldered |
```

- **Clip each cell** to a word, a number, a symbol or a short phrase. A note
  that won't fit goes in a sentence or footnote under the table.
- **Same units and form down a column** (`$10/mo` in every row, not
  `ten dollars a month` in one), so the column reads as one axis.
- **A property shared by every row** goes in a line under the table
  (`**Shared by all three:** Linux, macOS and Windows apps.`) rather than a
  column of identical cells. Which properties earn columns at all is in
  `writing-hygiene-tables-for-comparison`.

## Common mistakes

| Mistake                                        | Fix                                       |
| ---------------------------------------------- | ----------------------------------------- |
| Child bullet indented 1 space, renders flat    | Indent to the parent's text column        |
| Child indented 4+ spaces past it, renders code | Indent to the parent's text column        |
| List glued to the paragraph above              | Add a blank line before the first item    |
| Line break inside an item vanishes             | End the line with 2 spaces or `\`         |
| `##Heading` with no space                      | `## Heading`                              |
| `##` followed by `####`                        | Use `###`; don't skip levels              |
| `**Setup**` on its own line as a section title | `### Setup`                               |
| Table with no delimiter row                    | Add a row of `---` cells under the header |
| A literal pipe in a cell splits the row        | Put a backslash before the pipe           |
| Blank cell                                     | `—` or `N/A`                              |
| `Yes` / `No` cells                             | ✅ / ❌                                   |
| `✅ — only on Pro`                             | `✅<br/>Only on Pro`                      |
| ✅ in a categorical or numeric column          | Plain text                                |
| Plain or bold item names in the first column   | Link each name to its canonical page      |

## When to apply

- Writing or reviewing any Markdown list, heading or table.
- A list, heading or table renders differently from its source: flattened
  nesting, a merged paragraph, a missing anchor, a split or shifted row.
- Right after a writing skill has chosen to turn prose into a list, an
  outline or a table, to write it out.

## Related skills

When one of these applies and it's in your skill listing, load it
without asking. If it isn't in your listing, tell the user which skill is
missing and ask whether to install it from the same collection this skill
came from; don't apply it from memory.

- `writing-hygiene-prose-to-lists`: when prose is really a list, when to leave it alone, and how to convert it faithfully.
- `writing-hygiene-headings-as-outline`: when a document needs headings and how to make them read as its outline.
- `writing-hygiene-tables-for-comparison`: when content is an item-by-property grid, and which properties earn columns.
- `markdown-hygiene-escape-reserved-characters`: escaping characters, such as a pipe in a cell, that Markdown would read as formatting.
- `markdown-hygiene-terminal-rendering`: tables, separators and links in Markdown that is read in a terminal.
