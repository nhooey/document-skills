# document-skills

Agent skills for the mechanics of document formats, packaged as a Nix flake.

Each format has its own skills and its own prefix: Markdown now, as
`markdown-hygiene-`, and later PDF, DocX and others, each under a prefix of
its own. These skills cover how a format works: its syntax, escaping and
how it renders where it's read. What to say and how to structure it, in any
format, is the job of the `writing-hygiene-` skills in writing-skills; a
skill here names the writing skill it pairs with.

Each skill is a self-contained directory under [`skills/`](skills/) with a
`SKILL.md` that an agent loads on demand. Skills are built by
[`agent-skill-flake`](https://github.com/nhooey/agent-skill-flake).

## Skills

| Skill                                                                                                        | What it does                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| [`markdown-hygiene-escape-reserved-characters`](skills/markdown-hygiene-escape-reserved-characters/SKILL.md) | Escape the characters Markdown would read as formatting, by backslash or code span, and only those.                               |
| [`markdown-hygiene-lists-headings-tables`](skills/markdown-hygiene-lists-headings-tables/SKILL.md)           | One sentence per line and its check, list nesting, ATX heading levels, table pipes, `<br/>` and ✅/❌ cells, `<details>` folding. |
| [`markdown-hygiene-terminal-rendering`](skills/markdown-hygiene-terminal-rendering/SKILL.md)                 | Markdown read in a terminal: tables fitted to its width, glyph width checks, U+2800 separator lines, links, commands to run.      |

## Install

```bash
# Preview what installing every skill would change, without writing anything
nix run github:nhooey/document-skills#preview

# Install all skills into the agent's skill directory
nix run github:nhooey/document-skills#install
```

Package outputs:

- `agent-skills-nhooey-document-all` — the aggregate of every skill (also `default`)
- `agent-skill-nhooey-markdown-hygiene-escape-reserved-characters`
- `agent-skill-nhooey-markdown-hygiene-lists-headings-tables`
- `agent-skill-nhooey-markdown-hygiene-terminal-rendering`
- `markdown-sentence-per-line` — the sentence-per-line check from `markdown-hygiene-lists-headings-tables`, for a repository's treefmt or checks

## Development

```bash
nix develop      # enter the dev shell; run `menu` to list commands
fmt              # nixfmt over *.nix, prettier over *.md / *.yaml / *.yml
doc-skills test  # pytest tests: every test; name skills to run only theirs
bb test          # the Babashka tests, tests/*/*_test.clj
check            # nix flake check: the treefmt check and all the tests
```
