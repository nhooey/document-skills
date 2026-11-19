---
name: markdown-hygiene-escape-reserved-characters
description: Escape the Markdown characters that would be read as formatting when you mean them literally, with a backslash for a stray mark in prose or a code span or fence for a run of code, and escape only those. Covers the backslash-escapable set (every ASCII punctuation mark), which characters are special only in certain positions (line start, after `]`, before `[`), the table-cell and HTML-entity edge cases, and the failures they cause (a `_word_` turning italic, a leading `1.` becoming a list, `<thing>` vanishing as a tag). Use when writing or reviewing Markdown (READMEs, docs, skill files, PR and commit bodies, GitHub issues, messages to other projects, release notes, chat messages rendered as Markdown) whose literal text holds these symbols, such as filenames, identifiers, math, paths, version ranges and CLI flags, or when a renderer is mangling prose.
tags: [markdown, writing]
---

# Escape reserved Markdown formatting characters

_Escape a punctuation mark only where the renderer would read it as formatting: a backslash for one mark in prose, a code span or fence for a whole run of code._

Left unescaped, a reserved mark silently changes the page: `_leading and trailing_` turns italic, a line starting with `1.` becomes an ordered list, `<config>` vanishes as an unknown HTML tag. There are two fixes:

- **A leading backslash** (`\*` renders as `*`) for one literal mark in prose.
- **A code span or fence** (`` `my_var` ``) when the whole run is code, since nothing inside one is interpreted.

## The escapable set

CommonMark lets a backslash escape any ASCII punctuation character, and nothing else:

```text
\   backslash              `   backtick
*   asterisk               _   underscore
{ } curly braces           [ ] square brackets
( ) parentheses            #   hash
+   plus                   - . minus / hyphen, dot
!   bang (exclamation)     |   pipe
<   less-than / angle      >   greater-than
"   double quote           '   single quote
~   tilde                  =   equals
:   colon                  ;   semicolon
,   comma                  @   at
$ % ^ & ?  and the rest of ASCII punctuation
```

A backslash before any other character is not an escape: `\n` renders as a backslash and an `n`. To show a literal backslash, write `\\`. A backslash at the end of a line is a hard line break, not a literal.

## Which characters need escaping, and where

Most marks are special only in certain positions, so escape by context rather than everywhere:

- **Inline emphasis and code:**
  - `*` marks emphasis anywhere, inside a word included.
  - `_` marks emphasis only at a word's edge: `snake_case_name` survives in CommonMark and GFM, but `_leading` or `trailing_` italicizes, and older renderers italicize mid-word too. When unsure, escape it or use a code span.
  - `` ` `` opens a code span. Escape it as `` \` ``, or, to show backticks inside code, use a longer delimiter: ``` `` `x` `` ```.
- **At the start of a line:**
  - `#` followed by a space is a heading. Escape it there (`\# 1 priority`); `C#` mid-line is fine.
  - `-`, `+` or `*` followed by a space is a bullet item. `- item` at a line's start lists; `5 - 3` does not.
  - A digit and `.` or `)` is an ordered item. Escape the dot: `1\. First` stays prose.
  - `>` is a blockquote. `\>` shows a literal; mid-line `a > b` is safe.
  - A line of only `---` or `===` under a paragraph line underlines it as a heading, and a line of only `---`, `***` or `___` elsewhere is a horizontal rule.
- **Link and image syntax:**
  - `[` and `]` hold link text. `\[draft\]` keeps literal brackets that a reference definition elsewhere could turn into a link.
  - `(` and `)` are special only right after a `]`, as the link's URL. Standalone parentheses need no escape.
  - `!` is special only right before `[`, as an image (`![alt](src)`). `Wow!` is fine.
- **HTML and entities:**
  - `<` followed by a letter, `/`, `!` or `?` can open an HTML tag or an autolink: `<config>` parses as a tag and vanishes. Write `\<config\>` or `` `<config>` ``. `a < b`, with a space after the `<`, is safe.
  - `&` followed by a name and `;` is an entity: `&copy;` renders as ©. Write `\&copy;` or `&amp;copy;` to show it literally. `AT&T` is fine.
- **Tables:** `|` separates columns. Escape a pipe in a cell as `\|`; outside a table a bare `|` is literal.
- **Extensions:**
  - `~` marks strikethrough in GFM, wrapped in one tilde or two: `~one~` and `~~two~~` both strike. A lone tilde, as in `~/bin`, is safe.
  - `:` opens an emoji shortcode (`:smile:`) on platforms that support them; it rarely needs escaping in plain docs.

## Backslash or code span

1. **Backslash** for one or two literal marks in prose: `50\% off`, `C\#`, `1\. not a list`.
2. **Code span or fence** when the run is code, an identifier, a path, a flag, a command or a regex. Nothing inside is interpreted, so no character needs escaping:
   - Inline: `` `my_func(*args, **kwargs)` `` renders verbatim, underscores and asterisks intact.
   - Block: a fence of three backticks (or `~~~`) for multi-line code, with a language tag for highlighting.

## Edge cases

- **A pipe in a table cell** needs `\|` even inside a code span, since GFM splits the row on `|` before it reads spans; the backslash is dropped in the rendered cell. The rest of table syntax is in `markdown-hygiene-lists-headings-tables`.
- **A backslash does nothing inside a code span or fence:** `` `a\*b` `` shows the backslash. Don't double-escape.
- **A backtick inside a code span** needs a longer delimiter, two or more backticks padded with spaces: ``` `` a ` b `` ```.
- **Autolinks:** `<https://example.com>` is a link, but `<arbitrary text>` is a dropped tag. Escape the brackets or put the text in a code span.
- **Four leading spaces** make an indented code block. This is not an escaping problem, but "my line rendered as code" is often mistaken for one.
- **Don't over-escape.** A needless backslash (`\?`, `\:` in prose) clutters the source, and renderers that aren't CommonMark may print it. Escape the mark actually being misread.

## Procedure

1. **Reproduce the mangling.** Render the Markdown and find what is eaten or changed: a vanished `<tag>`, unexpected italics, a spurious list.
2. **Find the trigger and its position:** inline emphasis, line-start block syntax, link or image syntax, HTML, or a table.
3. **Pick the fix:** a backslash for one stray mark, a code span or fence for a run of code.
4. **Re-render and check** that the literal text appears and that no span boundary or table column broke.

## When to apply

- Writing or reviewing Markdown whose literal text holds `*`, `_`, a backtick, `<`, `>`, `|`, `#`, `[` or another reserved character.
- A name renders in italics, a line turns into a list or a heading, or a `<word>` disappears from the rendered page.
- A table row splits into too many columns.
- Writing Markdown that a terminal will show; `markdown-hygiene-terminal-rendering` covers what a terminal adds.

## Related skills

When one of these applies and it's in your skill listing, load it
without asking. If it isn't in your listing, tell the user which skill is
missing and ask whether to install it from the same collection this skill
came from; don't apply it from memory.

- `markdown-hygiene-lists-headings-tables`: Markdown syntax for lists, headings and tables, including pipes inside cells.
- `markdown-hygiene-terminal-rendering`: Markdown read in a terminal: tables fitted to its width, glyph widths, separator lines and clickable links.
