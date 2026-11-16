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
        # skill set (the git/GitHub pack plus skillspkgs' `authoring`
        # combination) is defined in the runtime `skills-devshell/` sub-flake
        # and invoked at RUNTIME, never as a root input, so this repo keeps zero
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
          # tools/doc_skills.py, installed as `doc-skills` with its shebang
          # pointed at the dev shell's Python.
          docSkills =
            pkgs.runCommand "doc-skills"
              {
                buildInputs = [ pkgs.python3 ];
                meta.mainProgram = "doc-skills";
              }
              ''
                install -Dm755 ${./tools/doc_skills.py} $out/bin/doc-skills
                patchShebangs $out/bin
              '';
        in
        {
          packages = base.packages.${system};

          apps = base.apps.${system};

          # Every skill's unittest suite, run through the dev shell's own
          # `doc-skills test`. Its source is only each skill's SKILL.md,
          # scripts/ and tests/, so an edit to a reference page doesn't rerun
          # them.
          checks.skill-tests =
            let
              skillDirs = lib.attrNames (
                lib.filterAttrs (_: type: type == "directory") (builtins.readDir ./skills)
              );
              src = lib.fileset.toSource {
                root = ./.;
                fileset = lib.fileset.unions (
                  lib.concatMap (name: [
                    (lib.fileset.maybeMissing (./skills + "/${name}/SKILL.md"))
                    (lib.fileset.maybeMissing (./skills + "/${name}/scripts"))
                    (lib.fileset.maybeMissing (./skills + "/${name}/tests"))
                  ]) skillDirs
                );
              };
            in
            pkgs.runCommand "skill-tests" { } ''
              ${lib.getExe docSkills} --root ${src} test
              touch $out
            '';

          # Tests of doc-skills itself: its argument parsing, its pure
          # functions and the command.
          checks.doc-skills = pkgs.runCommand "doc-skills-tests" { nativeBuildInputs = [ pkgs.python3 ]; } ''
            cd ${./tools}
            python3 -I -B -m unittest discover -s tests
            touch $out
          '';

          # The repository's own command, beside the module's check / fmt /
          # update-flake and skills commands in the dev shell's menu.
          devshells.default.commands = [
            {
              category = "dev";
              name = "doc-skills";
              package = docSkills;
              help = "List the skills and run their tests (doc-skills --help)";
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
