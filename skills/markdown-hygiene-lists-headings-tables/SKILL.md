---
name: markdown-hygiene-lists-headings-tables
description: >-
  Load when writing or reviewing any Markdown (a README, docs, a skill, a plan, a GitHub issue, comment or PR description, a commit message or a message to another project) or when a list, heading or table renders wrongly. Syntax only: one sentence per line in repository files, list nesting, heading levels, table pipes and collapsed sections. Whether to use a list, headings or a table is in the `writing-hygiene-*` skills.
tags: [markdown, writing]
---

# Markdown syntax for line breaks, lists, headings and tables

_Write each sentence on a line of its own, and once the content is a list, an outline or a table, write its syntax so the renderer builds that structure and not a different one._

Once you have decided that content is a list, an outline of headings or a
table, the remaining work is syntax: a renderer that reads the wrong indent,
a skipped heading level or a stray pipe silently produces a different
structure from the one you wrote. This skill is that syntax. Whether to use
a list, a heading or a table, and how to convert prose faithfully, is in
`writing-hygiene-prose-to-lists`, `writing-hygiene-headings-as-outline` and
`writing-hygiene-tables-for-comparison`.

## Line breaks in prose

### One sentence per line in Markdown files

Start each sentence on a line of its own, and never break a line inside one.
A newline inside a paragraph renders as a space, so the page reads the same.
A diff, `git blame` or review comment then lands on the one sentence it's about, and editing a sentence never reflows the ones after it.

- **Too long for one line:** split it into 2 sentences.
- **List items:** each sentence after the first goes on a continuation line at the item's text column.
- **Prettier:** keep `proseWrap` at its default, `"preserve"`. `"always"` refills paragraphs.

### Text posted to GitHub

GitHub renders every newline as a line break in the text posted to it: comments, issues, pull request descriptions and review comments.
There, join each paragraph into one line and part paragraphs with a blank line, so a sentence-per-line paragraph doesn't show as a column of short lines.
Lists, tables and code blocks keep their own lines.
Files in a repository render by the ordinary Markdown rules above, so the rule for files stands.

### Commit messages

A commit message is read raw, by `git log` in a terminal, so its body stays wrapped at 72 columns, as `git-hygiene-commit-message-format` says.
A tool that copies a commit body into a pull request description joins each paragraph's lines first, as `github-hygiene-pull-request-mirrors-commit` does, since GitHub would otherwise show every wrap.

### Checking a file

`scripts/sentence_per_line.clj` flags each paragraph line, in a list item or block quote too, that is followed by another line of the same paragraph and ends without `.`, `!`, `?` or `…`, before any closing emphasis, code, bracket or quote marks.
It parses the Markdown, so code blocks, tables, headings, HTML blocks, front matter, the last line of a paragraph, a line followed by a list item and a hard break are never flagged.
A colon or semicolon doesn't end a sentence, and an abbreviation such as "e.g." at a line's end passes as one.
It prints `FILE:LINE:` for each flagged line and exits 1 when there is one, 0 when there is none and 2 on an error; it changes no file.

The flake packages it with its parser, `cmark-gfm`:

```bash
nix run github:nhooey/document-skills#markdown-sentence-per-line -- README.md docs/*.md
```

To run it in a repository's `nix fmt` and `nix flake check`, add the `document-skills` flake as an input and the program as a treefmt-nix formatter.
A formatter that exits non-zero fails `nix fmt` and the treefmt check alike, with the flagged lines in the output:

```nix
treefmt.settings.formatter.markdown-sentence-per-line = {
  command = lib.getExe inputs.document-skills.packages.${system}.markdown-sentence-per-line;
  includes = [ "*.md" ];
  # excludes = [ "docs/not-yet-converted.md" ];
};
```

Without treefmt, run it from a check:

```nix
checks.markdown-sentence-per-line = pkgs.runCommand "markdown-sentence-per-line" { } ''
  cd ${./.}
  find . -name '*.md' -exec ${lib.getExe inputs.document-skills.packages.${system}.markdown-sentence-per-line} {} +
  touch $out
'';
```

### Converting a hard-wrapped file

1. **Pick a file no open change touches.** Converting rewrites most of its prose lines, so it conflicts with any open pull request that edits the file.
2. **Leave the rest alone:** code blocks, tables, headings, front matter, HTML and hard line breaks.
3. **Join each paragraph's lines into one**, in list items and block quotes too, keeping the item's indent and the quote's `>`.
4. **Break after each sentence**, starting the next sentence on a new line at the same indent.
   Read each break: an abbreviation such as "e.g." or "i.e.", a decimal number or a version number doesn't end a sentence.
5. **Confirm that only line breaks changed:** `git diff --word-diff` shows no changed words.
6. **Run the check** on the file.
7. **Commit the conversion alone**, apart from any change of wording, so a reviewer can skim it and the commit can go in `.git-blame-ignore-revs`.

## Lists

- **One marker per list.** Use `-` for bullets throughout a document; a
  change of marker (`-` to `*`, or `1.` to `1)`) starts a new list in
  CommonMark, which can add a gap or restart the numbering.
- **Ordered lists for sequences and priorities.** Write `1.`, `2.`, `3.`.
  A renderer numbers from the first item's number and ignores the rest, so
  the later numbers matter only to someone reading the source: number in
  order rather than writing `1.` on every line.
- **Nest by the parent's text column.** A child item is indented to where
  the parent's text starts: 2 spaces under `- `, 3 under `1. `, 4 under
  `10. `. Fewer spaces and the child becomes a sibling; 4 or more beyond
  the parent's text and it becomes an indented code block.
- **Continuation lines and paragraphs inside an item** use the same indent
  as the item's text. An unindented line ends the item.
- **Blank lines around a list.** Put a blank line before the first item and
  after the last. Without the one before, an ordered list starting at any
  number but 1 is folded into the paragraph above in CommonMark, and so is
  any list in older renderers; without the one after, a following
  unindented line can join the last item.
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
- **Alignment** goes in the delimiter row: `:---` left,
  `:---:` centre, `---:` right; a plain `---` leaves it to the renderer,
  which usually left-aligns. Right-align numbers so their digits line up.
- **The same number of cells in every row** as in the header. A row with
  fewer gets empty cells; a row with more loses the extra ones.
- **A blank line above and below the table.** Directly under a paragraph
  line some renderers read the table as more paragraph, and in GFM a line
  of text directly under the last row becomes one more row.
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

## Collapsed sections

A collapsed section is HTML that Markdown passes through: `<details>` around the block, and inside it a `<summary>` holding the one line shown while the block is closed.
Markdown doesn't read inside an HTML block, and a blank line is what ends one, so the blank lines decide what renders.
Whether a block should be collapsed at all is in `writing-hygiene-progressive-disclosure`.

```markdown
<details>
<summary>Already current (4)</summary>

- auth
- docs
- mail
- web

</details>

The next paragraph.
```

- **A blank line after `</summary>`.**
  Without it the content is still part of the HTML block, and a list, a table or a code fence inside shows as its raw text.
- **A blank line after `</details>`.**
  Without it the next line joins the HTML block, and its Markdown isn't rendered.
- **The tags at the indent of the text around them:** column 0, or the item's text column inside a list item.
- **HTML in the summary, not Markdown.**
  The summary line is inside the HTML block, so `**bold**` and backticks show as typed: write `<b>` and `<code>`.
- **`<details open>`** draws the section open, for the reader to close.

### Where a collapsed section folds

It folds where the Markdown becomes HTML in a browser and the renderer lets these 2 tags through.
Anywhere else the content shows in full, usually with the tags as text around it.

| Where the Markdown is read                                                            | A `<details>` block                                                    |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| GitHub: an issue, a pull request, a comment, a release, a wiki, a rendered `.md` file | folds                                                                  |
| A terminal, raw or through a renderer                                                 | doesn't fold, as `markdown-hygiene-terminal-rendering` says            |
| A commit message                                                                      | doesn't fold: `git log` and GitHub's commit page show it as plain text |

Leave the tags out where they don't fold.

## Common mistakes

| Mistake                                        | Fix                                       |
| ---------------------------------------------- | ----------------------------------------- |
| A file's paragraph wrapped mid-sentence        | One sentence per line                     |
| Sentence-per-line paragraph posted to GitHub   | Join the paragraph into one line          |
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
| Markdown inside `<details>` shows as raw text  | Add a blank line after `</summary>`       |
| `<details>` in text read in a terminal         | Leave it out and put the detail last      |

## When to apply

- Writing or reviewing any Markdown, to break its prose lines between sentences, or to join them in text posted to GitHub.
- Converting a hard-wrapped Markdown file, or adding the sentence-per-line check to a repository.
- Writing or reviewing any Markdown list, heading or table.
- A list, heading or table renders differently from its source: flattened
  nesting, a merged paragraph, a missing anchor, a split or shifted row.
- Right after a writing skill has chosen to turn prose into a list, an
  outline or a table, to write it out.
- Writing a `<details>` block, or fixing one whose content shows as raw text.

## Related skills

When one of these applies and it's in your skill listing, load it
without asking. If it isn't in your listing, tell the user which skill is
missing and ask whether to install it from the same collection this skill
came from; don't apply it from memory.

- `writing-hygiene-prose-to-lists`: when prose is really a list, when to leave it alone, and how to convert it faithfully.
- `writing-hygiene-headings-as-outline`: when a document needs headings and how to make them read as its outline.
- `writing-hygiene-tables-for-comparison`: when content is an item-by-property grid, and which properties earn columns.
- `writing-hygiene-progressive-disclosure`: which parts of a document are collapsed, and what a collapsed section's label says.
- `markdown-hygiene-escape-reserved-characters`: escaping characters, such as a pipe in a cell, that Markdown would read as formatting.
- `markdown-hygiene-terminal-rendering`: tables, separators and links in Markdown that is read in a terminal.
- `git-hygiene-commit-message-format`: the commit message body, wrapped at 72 columns rather than one sentence per line.
- `github-hygiene-pull-request-mirrors-commit`: copying a commit body into a pull request description, with its paragraphs joined for GitHub.
