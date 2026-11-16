# document-skills

Agent skills for the mechanics of document formats (Markdown now, as
`markdown-hygiene-*`), packaged as a Nix flake with
[agent-skill-flake](https://github.com/nhooey/agent-skill-flake). Each skill
is a directory under `skills/` with a `SKILL.md` and its own `flake.nix`.

## Build and test

- `nix develop` enters the dev shell and installs the project's skills into
  `.agents/skills/` from the `skills-devshell/` sub-flake.
- `nix fmt` formats `*.nix` with nixfmt and `*.md`, `*.yaml` and `*.yml`
  with prettier.
- `nix flake check` evaluates every output, runs the formatting check and
  runs the tests; it must pass before a change merges.
- Tests sit in a `tests/` directory beside the skill's `scripts/`, as stdlib
  `unittest` files, so they aren't installed with the skill. Run one skill's
  tests from its directory with `python3 -I -B -m unittest discover -s tests`.
