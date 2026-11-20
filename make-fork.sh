#!/usr/bin/env bash
# Rebuild the trimmed RH fork from the public mirror, then check it is byte-identical to ours.
#
#   ./make-fork.sh [DEST]          (default DEST: ./rh-trim-fork)
#
# Needs git and python3 (3.9 or newer). Takes about 2 minutes plus the clone (about 1.7 GB).
# Reads and writes text only: nothing from the proof is compiled or run.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$(mkdir -p "${1:-rh-trim-fork}" && cd "${1:-rh-trim-fork}" && pwd)"
MIRROR="${RH_TRIM_MIRROR:-https://github.com/Deicyde/riemann-hypothesis.git}"
PIN=8b83d5e7b319ebc7b3be6e59ce3411ba2b09d116
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

if [ -e "$DEST/src" ]; then
  echo "error: $DEST/src already exists; pass an empty folder" >&2
  exit 1
fi

echo "1/6  cloning the mirror at ${PIN:0:9}"
git clone --quiet "$MIRROR" "$WORK/mirror"
git -C "$WORK/mirror" -c advice.detachedHead=false checkout --quiet "$PIN"
[ "$(git -C "$WORK/mirror" rev-parse HEAD)" = "$PIN" ] || { echo "error: wrong mirror commit" >&2; exit 1; }

echo "2/6  unpacking the trace results"
gunzip -c "$HERE/data/kept-files.txt.gz" > "$WORK/kept-files.txt"
gunzip -c "$HERE/data/cuts.json.gz" > "$WORK/cuts.json"

echo "3/6  writing the trimmed source"
python3 "$HERE/tools/prune.py" "$WORK/mirror/src" "$WORK/kept-files.txt" "$DEST" "$WORK/cuts.json"

echo "4/6  removing dangling attributes, checking imports"
python3 "$HERE/tools/check_fork.py" "$DEST/src" "$WORK/mirror/src"
python3 "$HERE/tools/trim_main.py" "$DEST/src"

echo "5/6  adding the key-chain docstrings"
python3 "$HERE/tools/add_docs.py" "$DEST/src"
for f in lakefile.toml lake-manifest.json lean-toolchain comparator.json export-targets.txt .gitignore; do
  cp "$WORK/mirror/$f" "$DEST/"
done

echo "6/6  checking the result against the published fingerprint"
got="$(python3 "$HERE/tools/tree_hash.py" "$DEST/src")"
want="$(cat "$HERE/data/expected-tree.txt")"
if [ "$got" = "$want" ]; then
  echo "OK: $DEST/src matches ($want)"
else
  echo "MISMATCH: got $got, expected $want" >&2
  exit 1
fi
echo
echo "Next: see docs/CHECKING.md. Build only inside a sandbox; compiling Lean runs code."
