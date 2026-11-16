{
  description = "markdown-hygiene-terminal-rendering: Agent skill — Markdown read in a terminal: tables fitted to its width, glyph width checks, the U+2800 separator line, hard line breaks, clickable links and commands for the reader to run";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    agent-skill-flake.url = "github:nhooey/agent-skill-flake";
    agent-skill-flake.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    { nixpkgs, agent-skill-flake, ... }:
    agent-skill-flake.lib.mkSkillFlake {
      inherit nixpkgs;
      source = import ../../source.nix;
      skillName = "markdown-hygiene-terminal-rendering";
      src = ./.;
    };
}
