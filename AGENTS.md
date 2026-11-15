# document-skills

Agent skills for the mechanics of document formats (Markdown now, as
`markdown-hygiene-*`), packaged as a Nix flake with
[agent-skill-flake](https://github.com/nhooey/agent-skill-flake). Each skill
is a directory under `skills/` with a `SKILL.md` and its own `flake.nix`.

## Build and test

- `nix develop` enters the dev shell and installs the project's skills into
  `.agents/skills/` from the `skills-devshell/` sub-flake.
- `nix fmt` formats `*.nix` with nixfmt and `*.md` and `*.yaml` with prettier.
- `nix flake check` evaluates every output and runs the formatting check; it
  must pass before a change merges.
