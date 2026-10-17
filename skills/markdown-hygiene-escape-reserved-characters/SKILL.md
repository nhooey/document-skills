---
name: markdown-hygiene-escape-reserved-characters
description: |
  Escape the Markdown characters that would be read as formatting when you
  mean them literally: backslash, backtick, asterisk, underscore, braces,
  brackets, parentheses, angle brackets, hash, plus, minus, dot, bang, pipe
  and the ampersand of an HTML entity. Covers the full reserved set, which
  characters are special only in certain positions, a leading backslash
  versus a code span or fence, the table-cell and HTML-entity edge cases,
  and the failures they cause (a stray `_` italicizing a snake_case name, a
  leading `1.` becoming a list, `<thing>` vanishing as a tag). Use when
  writing or reviewing Markdown (READMEs, docs, skill files, PR and commit
  bodies, release notes, chat messages rendered as Markdown) whose literal
  text holds these symbols: filenames, identifiers, math, paths, version
  ranges, CLI flags, or prose the renderer is mangling.
tags: [markdown, writing]
---

# Escape reserved Markdown formatting characters

## How to load this skill

Passive reference. Loading it doesn't mean the document needs rewriting
now; it means that whenever you write Markdown holding literal symbols,
you escape the ones the renderer would misread, and only those.

Markdown reserves a small set of punctuation marks as formatting directives. When you want one to appear _literally_ — a `*` that means "asterisk", an underscore inside `my_variable`, a `<` that isn't an HTML tag — you have to tell the parser "this is text, not markup". Get it wrong and the renderer silently eats your characters or warps your prose: a `snake_case` name left outside a code span can turn _italic_ partway through, a line starting with `1.` becomes an ordered list, `<config>` vanishes as an unknown tag.

Two tools fix it: a **leading backslash** (`\*` → `*`) for an inline literal, or a **code span / fence** (`` `my_var` ``) when the whole run is code, where _nothing_ is interpreted. This skill covers which characters are reserved, when they're actually dangerous (many are only special in certain positions), and how to escape each cleanly.

## The reserved set

CommonMark lets a backslash escape exactly these ASCII punctuation characters. Any of them becomes a literal when preceded by `\`:

```
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

A backslash before a **non-punctuation** character is _not_ an escape — `\n` renders as a literal backslash-then-n, `\<space>` is just a backslash. Only the ASCII punctuation above is escapable; to show a literal backslash, write `\\`.

## Which characters actually need escaping — and when

Most are only special in specific positions, so blanket-escaping everything produces ugly, backslash-littered source. Escape by context:

- **Always risky inline (emphasis):**
  - `*` and `_` — emphasis markers. `*` is greedy anywhere; `_` is special only bordering whitespace/punctuation, so `snake_case_name` mid-word usually survives but `_leading` or `trailing_` italicizes. When unsure, escape or use a code span.
  - `` ` `` — backtick starts a code span. Escape `` \` `` inline, or to show backticks _inside_ code use a longer fence: ``` `` `x` `` ```.
- **Risky only at the start of a line / block:**
  - `#` — becomes a heading (`# `, `## `, …). Only at line start: `\# 1 priority` or `C#` mid-line is fine.
  - `-`, `+`, `*` followed by a space — bullet list. `- item` at line start lists; `5 - 3` does not.
  - `1.` / `1)` (digit + `.`/`)`) — ordered list. Escape the dot: `1\. First` keeps it prose.
  - `>` — blockquote at line start. `\> ` shows a literal. Mid-line `a > b` is safe.
  - `|` — table column separator; pipes in a cell need `\|`. Outside a table a bare `|` is literal.
  - `=` or `-` on the line _below_ text — setext heading underline. A line of only `---`/`===` becomes a heading or `<hr>`.
- **Risky as link/image syntax:**
  - `[` `]` — link/reference text. `\[draft\]` keeps literal brackets that would otherwise look like an undefined reference link.
  - `(` `)` — only special immediately after a `]` (the link URL). Standalone parens need no escape.
  - `!` — only special immediately before `[` (image syntax `![alt]`). `Wow!` is fine; `\![not an image]` is not.
- **Risky as HTML / entities:**
  - `<` — starts an HTML tag or autolink. `<config>` parses as a tag and vanishes; write `\<config\>` or `` `<config>` ``. `a < b` (with a space) is usually safe but escaping is safer.
  - `&` — starts an HTML entity. `AT&T` usually renders fine, but `&amp;` or `&copy;` decodes; write `\&` or `&amp;` to force a literal ampersand.
- **Extension-only:**
  - `~` — strikethrough (`~~x~~`) in GFM and some renderers. Literal tildes in `~/bin` are normally safe, but `~~` pairs strike.
  - `:` — emoji shortcodes (`:smile:`) on platforms that support them; rarely needs escaping in plain docs.

## Two ways to escape

1. **Backslash** for a single literal mark in prose: `50\% off`, `C\#`, `1\. not a list`. Precise and minimal — use it when only one or two characters are problematic.
2. **Code span / fence** when the whole run is code, an identifier, or a path — _nothing_ inside is interpreted, so you never escape individual characters:
   - Inline: `` `my_func(*args, **kwargs)` `` renders verbatim, underscores and asterisks intact.
   - Block: a triple-backtick (or `~~~`) fence for multi-line code; add a language tag for highlighting.
   - Almost always better for filenames, CLI invocations, regexes, and code identifiers — reach for it before hand-escaping a thicket of metacharacters.

## Edge cases that bite

- **Inside table cells**, escape `|` as `\|` even inside what looks like a code span — many parsers split the row on `|` _before_ tokenizing spans. A literal pipe in a cell is the classic broken table. The rest of table syntax is in `markdown-hygiene-lists-headings-tables`.
- **Code spans need no inner escapes** — but to include a literal backtick, widen the fence (two or more backticks as the delimiter, padded with spaces): ``` `` a ` b `` ```.
- **Backslash has no effect inside a code span or fence** — `` `a\*b` `` shows the backslash literally. Don't double-escape.
- **Autolinks and angle brackets** — `<https://example.com>` is a valid autolink, but `<arbitrary text>` is a dropped tag. Escape the brackets or fence the text.
- **Four leading spaces** makes an indented code block — not an escape problem but a related gotcha, since "my line rendered as code" is often mistaken for an escaping bug.
- **Don't over-escape.** Needless backslashes (`\?`, `\:` in ordinary prose) render as literal backslashes in some strict parsers and clutter the source in all. Escape the character actually being misparsed, not every symbol that _could_ be.

## Quick procedure

1. **Reproduce the mangling.** Render the Markdown and find what's eaten or transformed (vanished `<tag>`, unexpected italics, a spurious list).
2. **Identify the trigger character and its position.** Inline emphasis, line-start block syntax, link/image syntax, or HTML?
3. **Pick the tool.** One stray mark → backslash it. A whole code-ish run → wrap it in a code span or fence.
4. **Re-render and confirm** the literal text appears, and that you didn't break a span boundary or table column.
5. **Prefer code spans for code.** For an identifier, path, flag, or command, fencing is more robust and readable than a string of backslashes.

## Quick heuristic

> If the text _is_ code, fence it. If it's prose with one rogue mark, backslash that mark. Escape what the renderer actually misreads — not every symbol that might one day misbehave.

## When to apply

- Writing or reviewing Markdown whose literal text holds `*`, `_`, a
  backtick, `<`, `>`, `|`, `#`, `[` or another reserved character.
- A snake_case name renders in italics, a line turns into a list or a
  heading, or a `<word>` disappears from the rendered page.
- A table row splits into too many columns.
- Before sending Markdown that a terminal will render; see
  `markdown-hygiene-terminal-rendering` for what a terminal adds.

## Related skills

When one of these applies and it's in your skill listing, load it
without asking. If it isn't in your listing, tell the user which skill is
missing and ask whether to install it from the same collection this skill
came from; don't apply it from memory.

- `markdown-hygiene-lists-headings-tables`: Markdown syntax for lists, headings and tables, including pipes inside cells.
- `markdown-hygiene-terminal-rendering`: Markdown read in a terminal: box-drawing tables, glyph widths, separator lines and clickable links.
