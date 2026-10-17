{
  description = "markdown-hygiene-lists-headings-tables: Agent skill — Markdown syntax for lists, headings and tables: nesting indents, hard line breaks, ATX levels, pipes and alignment, <br/> in cells, ✅/❌ cells, linked first column";

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
      skillName = "markdown-hygiene-lists-headings-tables";
      src = ./.;
    };
}
