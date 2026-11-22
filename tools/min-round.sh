#!/usr/bin/env bash
# One minification round: cut list (with any files kept as they were) -> safe cuts -> source on AWS ->
# trimmed imports -> (re)start the unmerged build. Lake rebuilds only files whose text changed.
#   min-round.sh ROUND_LABEL
set -euo pipefail
cd ~/rh-sandbox
LABEL=$1; H=ubuntu@77.112.217.157; K=~/.ssh/rh-build
touch revert-files.txt extra-names.txt
python3 tools/reach.py ~/rh-check/src Main --v2 --v3 --cached --keep-names=$HOME/rh-sandbox/kept-after-swaps.txt --revert-files=$HOME/rh-sandbox/revert-files.txt --extra-names=$HOME/rh-sandbox/extra-names.txt 2>&1 | grep -E "exact" || true
python3 tools/finalize_cuts.py exact-cuts.json kept-after-swaps.txt decls-project.tsv exact-files.txt ~/rh-check/src cuts-final.json files-final.txt
python3 - <<'PY'
import json
rv = set(l.strip() for l in open('revert-files.txt') if l.strip())
for f in ('swaps.json', 'imports.json'):
    d = json.load(open(f)); json.dump({m: v for m, v in d.items() if m not in rv}, open(f.replace('.json', '-round.json'), 'w'))
c = json.load(open('cuts-final.json')); json.dump({m: ([] if m in rv else v) for m, v in c.items()}, open('cuts-round.json', 'w'))
PY
for f in files-final.txt cuts-round.json swaps-round.json imports-round.json; do scp -q -i $K $f $H:research/min/; done
ssh -i $K $H "set -e; cd ~/research/min; M=~/rh-build/min; O=~/rh-build/original
  tmux kill-session -t min 2>/dev/null || true
  rm -rf \$M/src-new; python3 prune.py \$O/src files-final.txt \$M/src-new-root cuts-round.json swaps-round.json imports-round.json | tail -1
  mv \$M/src-new-root/src \$M/src-new; rm -rf \$M/src-new-root
  python3 trim_imports.py \$M/src-new decls-mathlib.tsv decls-batteries.tsv decls-aesop.tsv decls-plausible.tsv decls-Qq.tsv 2>&1 | tail -1
  # replace changed files only, so Lake keeps what it already built
  rsync -a --checksum --delete \$M/src-new/ \$M/src/ ; rm -rf \$M/src-new
  n=\$(find \$M/src -name '*.lean' | wc -l); l=\$(find \$M/src -name '*.lean' -print0 | xargs -0 cat | wc -l)
  echo \"== \$(date -u +%H:%M:%S) $LABEL source: \$l lines, \$n files\" | tee -a ~/rh-build/build-min.log
  rm -f ~/run-min.log; tmux new -d -s min ~/build-min.sh"
