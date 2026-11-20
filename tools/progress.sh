#!/usr/bin/env bash
# Progress and rate of a build-linux.sh build, from its timestamped log.
#   tools/progress.sh ~/rh-build/build.log
# Prints files built, the rate over the last 10 minutes, and a rough time left.
set -euo pipefail
LOG="$1"
TOTAL=137020        # proof files in the reduced version (plus Mathlib's, which come from cache)
awk -v total="$TOTAL" '
  function secs(t,  a) { split(t, a, ":"); return a[1]*3600 + a[2]*60 + a[3] }
  / (✔|⚠) \[/ && $0 !~ /Mathlib|Batteries|Aesop|Qq|Plausible|ProofWidgets|ImportGraph|LeanSearchClient/ {
    n++; t = secs($1); if (first == "") first = t; times[n] = t
  }
  / error: / { e++ }
  END {
    if (n == 0) { print "no proof files built yet"; exit }
    last = times[n]; if (last < first) last += 86400
    k = n; while (k > 1 && (last - times[k-1] + 86400) % 86400 <= 600) k--
    win = (last - times[k] + 86400) % 86400; rate = (win > 0) ? (n - k) / win * 60 : 0
    printf "%d proof files built, %d error lines\n", n, e
    if (rate > 0) {
      left = (total - n) / rate
      printf "rate: %.0f files/min over the last %d min; about %dh %02dm left at that rate\n", rate, win/60, left/60, left%60
    }
  }' "$LOG"
