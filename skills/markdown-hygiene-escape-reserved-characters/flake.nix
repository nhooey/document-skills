{
  description = "markdown-hygiene-escape-reserved-characters: Agent skill — escape the Markdown characters that would be read as formatting when you mean them literally, by backslash or code span";

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
      skillName = "markdown-hygiene-escape-reserved-characters";
      src = ./.;
    };
}
