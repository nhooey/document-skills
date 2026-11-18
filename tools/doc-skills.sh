# shellcheck shell=bash
# doc-skills: the body of the dev shell's `doc-skills` command, which
# flake.nix wraps with writeShellApplication, putting the test Python and
# findutils on PATH.
set -o errexit -o nounset -o pipefail
usage="usage: doc-skills test [SKILL...]  (pytest tests, or pytest tests/SKILL...)"
case "${1:-}" in
  test) shift ;;
  -h | --help)
    echo "$usage"
    exit 0
    ;;
  *)
    echo "$usage" >&2
    exit 2
    ;;
esac
cd "${PRJ_ROOT:-.}"
# Whether folder $1 holds a file named like any of the patterns after it.
holds() {
  local folder=$1 names=()
  shift
  for pattern in "$@"; do names+=(-o -name "$pattern"); done
  [ -n "$(find "$folder" -type f \( "${names[@]:1}" \) -print -quit)" ]
}
python_paths=()
for skill in "$@"; do
  folder="tests/$skill"
  if [[ $skill == */* || $skill == .* || ! -d $folder ]]; then
    echo "doc-skills: no tests/ folder for a skill named '$skill'" >&2
    exit 2
  fi
  found=0
  if holds "$folder" 'test_*.py' '*_test.py'; then
    python_paths+=("$folder")
    found=1
  fi
  if [ "$found" -eq 0 ]; then
    echo "doc-skills: $folder holds no tests" >&2
    exit 1
  fi
done
status=0
if [ "$#" -eq 0 ]; then
  python3 -I -B -m pytest tests || status=1
elif [ "${#python_paths[@]}" -gt 0 ]; then
  python3 -I -B -m pytest "${python_paths[@]}" || status=1
fi
exit "$status"
