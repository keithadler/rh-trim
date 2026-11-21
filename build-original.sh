#!/usr/bin/env bash
# Build the ORIGINAL claimed Lean proof of the Riemann Hypothesis, exactly as published (the
# byte-exact mirror Deicyde/riemann-hypothesis at a pinned commit), on a Linux machine.
# This is the script that built it on AWS on 2026-11-20/21. See docs/BUILD-ORIGINAL.md.
#
#   ./build-original.sh [WORK_DIR]        (default WORK_DIR: ~/rh-build)
#
# Run it on a THROWAWAY machine that holds nothing you care about: compiling Lean runs the proof's
# code. Rerunning it on the same disk resumes where it stopped (Lake skips what is built).
set -euo pipefail

WORK="${1:-$HOME/rh-build}"
O="$WORK/original"
LOG="$WORK/build-original.log"
PIN=8b83d5e7b319ebc7b3be6e59ce3411ba2b09d116
mkdir -p "$WORK"
say() { printf '== %s  %s\n' "$(date -u +%H:%M:%S)" "$*"; }

say "machine: $(nproc) CPUs, $(free -g | awk '/Mem:/{print $2}') GB RAM, $(df -h "$WORK" | awk 'NR==2{print $4}') free disk"

say "tools"
if ! command -v git >/dev/null || ! command -v bwrap >/dev/null || ! command -v zstd >/dev/null; then
  sudo apt-get update -qq && sudo apt-get install -y -qq git curl python3 bubblewrap zstd >/dev/null
fi
if ! command -v elan >/dev/null && [ ! -x "$HOME/.elan/bin/elan" ]; then
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$WORK/elan-init.sh"
  sh "$WORK/elan-init.sh" -y --default-toolchain none >/dev/null
fi
export PATH="$HOME/.elan/bin:$PATH"
# Ubuntu 24.04 blocks the user namespaces bubblewrap needs; this turns them back on (until reboot).
if [ -e /proc/sys/kernel/apparmor_restrict_unprivileged_userns ]; then
  sudo sysctl -q kernel.apparmor_restrict_unprivileged_userns=0 || true
fi

say "the proof, pinned to $PIN"
[ -d "$O/.git" ] || git clone --quiet https://github.com/Deicyde/riemann-hypothesis.git "$O"
git -C "$O" -c advice.detachedHead=false checkout --quiet "$PIN"
[ "$(git -C "$O" rev-parse HEAD)" = "$PIN" ] || { echo "wrong mirror commit" >&2; exit 1; }
cd "$O"

say "Lean 4.33.1 and Mathlib's official build cache (needs network)"
# Unpacking the cache on many cores opens thousands of files at once; the default limit is too low.
ulimit -n 1048576 2>/dev/null || ulimit -n 65536 2>/dev/null || true
lake --version
lake exe cache get

# Lake writes a .setup.json per module listing its whole import closure: about 4.6 MB each here,
# which filled a 200 GB disk after 20k modules. Lean reads it once when it starts on a module, so
# delete it after that; this does not make Lake rebuild anything.
( while true; do find "$O/.lake/build/ir" -name '*.setup.json' -mmin +2 -delete 2>/dev/null; sleep 60; done ) &
CLEANER=$!
trap 'kill $CLEANER 2>/dev/null' EXIT

if ! bwrap --unshare-net --ro-bind / / true 2>/dev/null; then
  echo "bubblewrap can't create a sandbox here. Don't build without one unless the machine is" >&2
  echo "throwaway; see docs/BUILD-ORIGINAL.md." >&2
  exit 1
fi
say "compiling, network cut off. Progress: tools/progress.sh $LOG (TOTAL=175187)"
start=$(date +%s)
set +e
bwrap --unshare-net --die-with-parent --ro-bind / / --bind "$O" "$O" --bind /tmp /tmp \
      --dev /dev --proc /proc --chdir "$O" -- \
  env LEAN_ABORT_ON_PANIC=1 lake build Main 2>&1 \
  | while IFS= read -r line; do printf '%s %s\n' "$(date -u +%H:%M:%S)" "$line"; done >> "$LOG"
status=${PIPESTATUS[0]}
set -e
secs=$(( $(date +%s) - start ))
say "RESULT exit status $status after $((secs/3600))h $((secs%3600/60))m"
printf '%s error lines, %s sorry warnings\n' "$(grep -c ' error: ' "$LOG" || true)" "$(grep -ci 'declaration uses .sorry' "$LOG" || true)"
tail -2 "$LOG"
echo
echo "Please report: https://github.com/keithadler/rh-trim/issues/new?template=build-report.yml"
