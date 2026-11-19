# shellcheck shell=bash
# The build command of flake.nix's checks.bb-test: bb and cmark-gfm are on
# PATH, $src is the source narrowed to bb.edn and the Clojure files, and
# $SENTENCE_PER_LINE is the packaged program the end-to-end tests run.
set -o errexit -o nounset -o pipefail
cd "${src:?}"
bb test
touch "${out:?}"
