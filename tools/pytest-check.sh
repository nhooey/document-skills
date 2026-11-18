# shellcheck shell=bash
# The build command of flake.nix's checks.pytest: the test Python is on
# PATH and $src is the source narrowed to the files the tests read.
set -o errexit -o nounset -o pipefail
cd "${src:?}"
python3 -I -B -m pytest tests
touch "${out:?}"
