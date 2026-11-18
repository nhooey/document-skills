# document-skills

Agent skills for the mechanics of document formats (Markdown now, as
`markdown-hygiene-*`), packaged as a Nix flake with
[agent-skill-flake](https://github.com/nhooey/agent-skill-flake). Each skill
is a directory under `skills/` with a `SKILL.md` and its own `flake.nix`.

## Build and test

- `nix develop` enters the dev shell and installs the skills its agents
  use, listed in the `skills-devshell/` sub-flake, into `.agents/skills/`.
  The skills under `skills/` are not among them.
- `menu` lists the dev shell's commands, each with a line of help.
- `fmt` (`nix fmt`) formats `*.nix` with nixfmt and `*.md`, `*.yaml` and
  `*.yml` with prettier.
- `check` (`nix flake check`) evaluates every output, runs the formatting
  check and runs the tests; it must pass before a change merges.
- An installed skill ships only what it runs: its `SKILL.md`, its reference
  pages and `scripts/`. A skill's Python scripts import only the standard
  library and each other, and no two skills' scripts share a module name.
- Every `SKILL.md` opens with frontmatter whose `name` is the skill's folder
  and whose `description` is at most 1,024 characters. A skill listed under
  `trigger-first` in `skill-checks.toml` has a description that opens on
  `trigger-first-prefix` and stays within 500 characters.
- agent-skill-flake's `skill-layout` and `skill-description` checks enforce
  these rules, including that no test sits under `skills/`, and read their
  settings from `skill-checks.toml`.
- Tests live outside the skills, under `tests/`, each language's run by that
  language's own tool:
  - A skill's tests go in `tests/<skill>/`, in the skill's language.
  - Tests of every skill or of the repository go directly in `tests/`.
  - Python tests run with pytest, the one library they may import.
    `tests/conftest.py` puts `skills/<skill>/scripts/` on `sys.path` for the
    tests in `tests/<skill>/`, so they import a script by its module name.
    `pytest.ini` holds pytest's options.
  - Babashka tests are `clojure.test` files named `*_test.clj`, run by
    `bb test`, the `test` task in `bb.edn`, with Babashka's own
    `clojure.test`. `bb.edn` puts each Babashka skill's `scripts/` and its
    `tests/<skill>/` on the task's classpath, and the task requires each
    test namespace, so a test requires its script by namespace.
  - A new language gets a check of its own in `flake.nix` and a command in
    the dev shell, both running its tool on its tests under `tests/`.
- `doc-skills test` runs pytest on `tests/`, and `doc-skills test SKILL...`
  on `tests/SKILL...`, only those skills' tests, not the repository tests.
  For pytest's own options, run `python3 -m pytest` in the dev shell.
- `bb test` runs the Babashka tests.
- `nix flake check` runs one check per language with the same command:
  `checks.<system>.pytest` runs `pytest tests` and `checks.<system>.bb-test`
  runs `bb test`.
