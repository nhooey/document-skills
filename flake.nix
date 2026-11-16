{
  description = "document-skills: Agent skills for the mechanics of document formats (Markdown now; later PDF, DocX), as a Nix flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    flake-parts = {
      url = "github:hercules-ci/flake-parts";
      inputs.nixpkgs-lib.follows = "nixpkgs";
    };
    # Declared explicitly even though `agent-skill-flake` already pulls in
    # `treefmt-nix` transitively: this flake owns its formatter toolchain
    # rather than borrowing a dependency's. The consumer below `follows` this
    # input so the whole tree resolves to one version.
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # `agent-skill-flake` is the builder library, not a skill — it turns skill
    # directories into installable flakes and aggregates them, and exports the
    # `flakeModules.devshellSkills` flake-parts module that wires the dev shell
    # below (motd + install-skills startup + the ci/dev/maintenance command
    # trio + the reap-skills/update-skills-devshell pair). That module bundles
    # numtide/devshell, so this flake needs no `devshell` input of its own. It
    # carries zero skill inputs, so keeping it here does not drag the skill mesh
    # into the root lock; the dev-shell skill sources live only in the
    # `skills-devshell/` sub-flake's lock and are invoked at RUNTIME.
    agent-skill-flake = {
      url = "github:nhooey/agent-skill-flake";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        treefmt-nix.follows = "treefmt-nix";
      };
    };
  };

  outputs =
    {
      nixpkgs,
      flake-parts,
      agent-skill-flake,
      ...
    }@inputs:
    let
      # The skills this repo outputs: every skill under ./skills built into
      # per-skill packages plus the base install/preview apps. The dev-shell
      # skill set is NOT an output here — it lives in the `skills-devshell/`
      # sub-flake and is invoked at runtime by the dev shell below.
      base = agent-skill-flake.lib.mkAllSkillsFlake {
        inherit nixpkgs;
        source = import ./source.nix;
        skillsDir = ./skills;
        packagePrefix = "agent-skill-";
        # Ship the reference pages a SKILL.md links beside it (examples.md,
        # commands.md, ...); by default only SKILL.md, references/ and
        # scripts/ are installed. Lower-case names only, so a skill's
        # README.md stays in the repo for people instead of being installed.
        extraFiles = [ "[a-z]*.md" ];
        # Name the aggregate by owner+topic (agent-skills-nhooey-document-all)
        # rather than the owner-wide `agent-skills-nhooey-all`. The owner-wide
        # key would collide across all repos this owner publishes under
        # skillspkgs / nur-packages' last-write-wins `//` merge; the
        # owner+topic name is resolvable and unique, mirroring git-skills's
        # `agent-skills-nhooey-git-all`. The aggregate carries the home-manager
        # `isFlakeSkillsEnv` passthru itself, so `default` is directly
        # installable.
        name = "agent-skills-nhooey-document-all";
      };
    in
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import inputs.systems;
      imports = [
        # Bundles numtide/devshell + the whole dev-shell skills convention
        # (motd, install-skills startup, the ci/dev/maintenance command trio,
        # and the reap-skills/update-skills-devshell pair). Configured via the
        # `agent-skill-flake.devshellSkills` options block below. The dev-shell
        # skill set is defined in the runtime `skills-devshell/` sub-flake and
        # invoked at RUNTIME, never as a root input, so this repo keeps zero
        # skill inputs in its own lock.
        inputs.agent-skill-flake.flakeModules.devshellSkills
        inputs.treefmt-nix.flakeModule
      ];

      # Keep document-skills' custom banner; the module's generated motd is
      # overridden by passing `motd` here.
      agent-skill-flake.devshellSkills = {
        name = "document-skills";
        motd = ''
          {bold}{14}🚀 Entering document-skills dev shell{reset}
          Run {bold}menu{reset} to list available commands.
        '';
      };
      perSystem =
        {
          system,
          pkgs,
          lib,
          ...
        }:
        let
          # The Python the Python tests run on. Only maintainers run the
          # tests, so they may use libraries; the skills' own Python scripts
          # stay standard library, which tests/test_layout.py checks.
          testPython = pkgs.python3.withPackages (ps: [
            ps.pytest
            ps.pyyaml
          ]);

          # `doc-skills test` runs each language's tool on tests/, and
          # `doc-skills test SKILL...` on tests/SKILL..., from $PRJ_ROOT (set
          # by the dev shell), else the current directory. A named skill must
          # have a folder under tests/, and each language's tool runs only on
          # the named folders holding that language's tests; a named folder
          # holding none fails, as does a tool that runs no test. Each
          # language's tool runs with the same command here as in that
          # language's check below: pytest as `python3 -I -B -m pytest`, on
          # testPython.
          docSkills = pkgs.writeShellApplication {
            name = "doc-skills";
            runtimeInputs = [
              testPython
              pkgs.findutils
            ];
            text = builtins.readFile ./tools/doc-skills.sh;
          };

          # The sentence-per-line check from markdown-hygiene-lists-headings-tables,
          # run by Babashka with cmark-gfm, its Markdown parser, on its PATH. Other
          # repositories add it to their treefmt or checks, as that skill's SKILL.md
          # shows. tools/build_sentence_per_line.sh builds it from these
          # attributes.
          sentencePerLine = pkgs.runCommand "markdown-sentence-per-line" {
            nativeBuildInputs = [ pkgs.makeWrapper ];
            sentencePerLineScript = ./skills/markdown-hygiene-lists-headings-tables/scripts/sentence_per_line.clj;
            babashka = lib.getExe pkgs.babashka-unwrapped;
            parserPath = lib.makeBinPath [ pkgs.cmark-gfm ];
            meta.mainProgram = "markdown-sentence-per-line";
          } (builtins.readFile ./tools/build_sentence_per_line.sh);
        in
        {
          packages = base.packages.${system} // {
            markdown-sentence-per-line = sentencePerLine;
          };

          apps = base.apps.${system};

          # One check per language, each running that language's tool on its
          # tests under tests/, as the dev shell's command for it does.
          #
          # pytest: its source is pytest.ini, tests/, each skill's SKILL.md
          # and scripts/, and every file under skills/ that
          # tests/test_layout.py would reject: one named like a test, or one
          # inside a tests/ or test/ folder. An edit to a reference page
          # doesn't rerun it.
          checks.pytest =
            let
              skillDirs = lib.attrNames (
                lib.filterAttrs (_: type: type == "directory") (builtins.readDir ./skills)
              );
              namedLikeTest =
                name: lib.hasPrefix "test_" name || lib.hasInfix "_test." name || lib.hasSuffix ".bats" name;
              misplacedTests = lib.fileset.fromSource (
                lib.cleanSourceWith {
                  src = ./skills;
                  filter =
                    path: type:
                    type == "directory"
                    || namedLikeTest (baseNameOf path)
                    || lib.any (part: part == "tests" || part == "test") (
                      lib.splitString "/" (lib.removePrefix "${toString ./skills}/" (toString path))
                    );
                }
              );
              src = lib.fileset.toSource {
                root = ./.;
                fileset = lib.fileset.unions (
                  [
                    ./pytest.ini
                    ./tests
                    misplacedTests
                  ]
                  ++ lib.concatMap (name: [
                    (lib.fileset.maybeMissing (./skills + "/${name}/SKILL.md"))
                    (lib.fileset.maybeMissing (./skills + "/${name}/scripts"))
                  ]) skillDirs
                );
              };
            in
            pkgs.runCommand "pytest" {
              inherit src;
              nativeBuildInputs = [ testPython ];
            } (builtins.readFile ./tools/pytest-check.sh);

          # bb-test: `bb test`, the `test` task in bb.edn, on bb.edn and the
          # Clojure files under skills/ and tests/. The sentence-per-line
          # tests parse with cmark-gfm, and their end-to-end cases run the
          # packaged program.
          checks.bb-test = pkgs.runCommand "bb-test" {
            src = lib.fileset.toSource {
              root = ./.;
              fileset = lib.fileset.unions [
                ./bb.edn
                (lib.fileset.fileFilter (file: file.hasExt "clj") ./skills)
                (lib.fileset.fileFilter (file: file.hasExt "clj") ./tests)
              ];
            };
            nativeBuildInputs = [
              pkgs.babashka-unwrapped
              pkgs.cmark-gfm
            ];
            SENTENCE_PER_LINE = lib.getExe sentencePerLine;
          } (builtins.readFile ./tools/bb-test-check.sh);

          # The test Python, for pytest's own options (`python3 -m pytest -k
          # NAME tests`) beyond what `doc-skills test` takes, and cmark-gfm,
          # which the sentence-per-line script parses with when `bb test` or
          # `bb` runs it from the working tree.
          devshells.default.packages = [
            testPython
            pkgs.cmark-gfm
          ];

          # The repository's own commands, beside the module's check / fmt /
          # update-flake and skills commands in the dev shell's menu.
          devshells.default.commands = [
            {
              category = "dev";
              name = "doc-skills";
              package = docSkills;
              help = "Run the Python tests: doc-skills test [SKILL...]";
            }
            {
              category = "dev";
              name = "bb";
              package = pkgs.babashka-unwrapped;
              help = "Run the Babashka tests: bb test";
            }
            {
              category = "dev";
              name = "markdown-sentence-per-line";
              package = sentencePerLine;
              help = "Flag Markdown lines that end mid-sentence (markdown-sentence-per-line --help)";
            }
          ];

          # `nix fmt` runs nixfmt over `.nix` and prettier over `.md` / `.yaml`
          # / `.yml`; the module also surfaces a `checks.${system}.treefmt` so
          # `nix flake check` fails on any unformatted file. prettier's includes are pinned
          # to markdown and YAML so it leaves JSON and other file types alone —
          # add formatters here as other tracked file types arrive.
          treefmt = {
            projectRootFile = "flake.nix";
            programs.nixfmt.enable = true;
            programs.prettier.enable = true;
            settings.formatter.prettier.includes = [
              "*.md"
              "*.yaml"
              "*.yml"
            ];
          };
        };
    };
}
