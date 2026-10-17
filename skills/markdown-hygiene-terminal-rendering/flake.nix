{
  description = "markdown-hygiene-terminal-rendering: Agent skill — Markdown read in a terminal: box-drawing tables padded for emoji width, glyph width checks, the U+2800 separator line, hard line breaks and clickable links";

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
