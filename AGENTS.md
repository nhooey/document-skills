# document-skills

Agent skills for the mechanics of document formats (Markdown now, as
`markdown-hygiene-*`), packaged as a Nix flake with
[agent-skill-flake](https://github.com/nhooey/agent-skill-flake). Each skill
is a directory under `skills/` with a `SKILL.md` and its own `flake.nix`.

## Build and test

- `nix develop` enters the dev shell and installs the skills its agents
  use into `.agents/skills/`: skillspkgs' `skill-collections` combination,
  taken by the `skills-devshell/` sub-flake, with no additions. The
  combination's `markdown-hygiene-*` skills come from this repository's
  default branch on GitHub, not from the checkout's `skills/`.
- `menu` lists the dev shell's commands, each with a line of help.
- `fmt` (`nix fmt`) formats `*.nix` with nixfmt and `*.md`, `*.yaml` and
  `*.yml` with prettier.
- `check` (`nix flake check`) evaluates every output, runs the formatting
  check and runs the tests; it must pass before a change merges.
- Tests sit in a `tests/` directory beside the skill's `scripts/`, as stdlib
  `unittest` files, so they aren't installed with the skill.
- `doc-skills list` lists the skills and which of them have tests.
- `doc-skills test` runs every skill's tests; name skills after it to run
  only theirs. `doc-skills --help` lists its commands and options; its source
  is `tools/doc_skills.py`, with its tests in `tools/tests/`.
