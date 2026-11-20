#!/usr/bin/env bash
# Build the reduced RH proof on a Linux machine (tested design for Ubuntu 22.04/24.04; see
# docs/BUILD.md). Run from a clone of rh-trim, on a THROWAWAY machine that holds nothing you
# care about: compiling Lean runs the proof's code.
#
#   ./build-linux.sh [WORK_DIR]        (default WORK_DIR: ~/rh-build)
#
# Steps: install elan + Lean, rebuild the reduced fork (make-fork.sh), fetch Mathlib's cache,
# then compile with the network cut off (bubblewrap) and log everything with timestamps.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$HOME/rh-build}"
FORK="$WORK/reduced"
LOG="$WORK/build.log"
mkdir -p "$WORK"

say() { printf '\n== %s  %s\n' "$(date -u +%H:%M:%S)" "$*"; }

say "machine: $(nproc) CPUs, $(free -g | awk '/Mem:/{print $2}') GB RAM, $(df -h "$WORK" | awk 'NR==2{print $4}') free disk"

say "1/5  tools"
if ! command -v git >/dev/null || ! command -v curl >/dev/null || ! command -v python3 >/dev/null; then
  sudo apt-get update -qq && sudo apt-get install -y -qq git curl python3 bubblewrap >/dev/null
fi
command -v bwrap >/dev/null || sudo apt-get install -y -qq bubblewrap >/dev/null || true
if ! command -v elan >/dev/null; then
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$WORK/elan-init.sh"
  sh "$WORK/elan-init.sh" -y --default-toolchain none >/dev/null
fi
export PATH="$HOME/.elan/bin:$PATH"

say "2/5  rebuilding the reduced fork from the public mirror (text only, about 2 minutes)"
if [ ! -e "$FORK/src" ]; then
  "$HERE/make-fork.sh" "$FORK"
else
  echo "already there: $FORK"
fi

say "3/5  Lean 4.33.1 and Mathlib's official build cache (needs network)"
cd "$FORK"
lake --version
lake exe cache get

say "4/5  compiling, network cut off. Follow progress with: tools/progress.sh $LOG"
JOBS="${JOBS:-$(nproc)}"
BUILD=(lake build Main)
if command -v bwrap >/dev/null && bwrap --unshare-net --ro-bind / / true 2>/dev/null; then
  echo "sandbox: bubblewrap, no network, everything read-only except $FORK and /tmp"
  RUN=(bwrap --unshare-net --die-with-parent --ro-bind / / --bind "$FORK" "$FORK" --bind /tmp /tmp
       --dev /dev --proc /proc --chdir "$FORK" --)
else
  if [ "${ALLOW_NO_SANDBOX:-0}" != 1 ]; then
    echo "bubblewrap can't create a sandbox here (common inside containers such as RunPod pods)."
    echo "Only continue on a throwaway machine: rerun with ALLOW_NO_SANDBOX=1." >&2
    exit 1
  fi
  echo "WARNING: building WITHOUT a sandbox (ALLOW_NO_SANDBOX=1)"
  RUN=()
fi
start=$(date +%s)
set +e
"${RUN[@]}" env LEAN_ABORT_ON_PANIC=1 "${BUILD[@]}" 2>&1 | while IFS= read -r line; do
  printf '%s %s\n' "$(date -u +%H:%M:%S)" "$line"
done > "$LOG"
status=${PIPESTATUS[0]}
set -e
secs=$(( $(date +%s) - start ))

say "5/5  result"
printf 'exit status %s after %dh %02dm\n' "$status" $((secs/3600)) $((secs%3600/60))
grep -c ' error: ' "$LOG" | xargs printf '%s error lines\n'
bash "$HERE/tools/progress.sh" "$LOG"
if [ "$status" != 0 ]; then
  say "what the reduction cut but the proof needs (from the errors):"
  git clone --quiet https://github.com/Deicyde/riemann-hypothesis.git "$WORK/mirror" 2>/dev/null || true
  git -C "$WORK/mirror" checkout --quiet 8b83d5e7b319ebc7b3be6e59ce3411ba2b09d116
  python3 "$HERE/tools/missing.py" "$LOG" "$WORK/mirror/src" | tee "$WORK/missing.txt"
fi
echo
echo "Please report: https://github.com/keithadler/rh-trim/issues/new?template=build-report.yml"
echo "Attach $LOG (compressed) and, if it exists, $WORK/missing.txt"
