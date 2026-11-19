# shellcheck shell=bash
# The build of the markdown-sentence-per-line package, run by the flake's
# runCommand. The derivation's attributes arrive as environment variables:
#   sentencePerLineScript  the skill's scripts/sentence_per_line.clj
#   babashka               the bb executable that runs it
#   parserPath             the PATH entry holding cmark-gfm
# shellcheck disable=SC2154 # $out and the attributes are set by Nix.

install -Dm644 "$sentencePerLineScript" \
  "$out/share/markdown-sentence-per-line/sentence_per_line.clj"
makeWrapper "$babashka" "$out/bin/markdown-sentence-per-line" \
  --add-flags "$out/share/markdown-sentence-per-line/sentence_per_line.clj" \
  --prefix PATH : "$parserPath"
