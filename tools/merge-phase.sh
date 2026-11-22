#!/usr/bin/env bash
# Step 2: merge the clean unmerged source into bundles and build; a bundle that fails has its files taken
# back out of bundling, and the build resumes. Stops on a clean merged build.
cd ~/rh-sandbox
H=ubuntu@77.112.217.157; K=~/.ssh/rh-build
ssh -i $K $H 'M=~/rh-build/min; [ -d $M/src-clean ] || cp -r $M/src $M/src-clean; : > ~/research/min/nomerge.txt'
n=0
while [ $n -lt 20 ]; do
  n=$((n+1))
  ssh -i $K $H "set -e; cd ~/research/min; M=~/rh-build/min
    tmux kill-session -t min 2>/dev/null || true
    rm -rf \$M/src-m \$M/src-m.bundles.tsv
    python3 merge_files.py \$M/src-clean \$M/src-m 25 4000 nomerge.txt 2>&1 | tail -1
    python3 trim_imports.py \$M/src-m decls-mathlib.tsv decls-batteries.tsv decls-aesop.tsv decls-plausible.tsv decls-Qq.tsv 2>&1 | tail -1
    cp \$M/src-m.bundles.tsv bundles.tsv
    rsync -a --checksum --delete \$M/src-m/ \$M/src/; rm -rf \$M/src-m
    nf=\$(find \$M/src -name '*.lean' | wc -l); nl=\$(find \$M/src -name '*.lean' -print0 | xargs -0 cat | wc -l)
    echo \"== \$(date -u +%H:%M:%S) merged $n source: \$nl lines, \$nf files\" | tee -a ~/rh-build/build-min.log
    rm -f ~/run-min.log; tmux new -d -s min ~/build-min.sh"
  last=-1; still=0
  while true; do
    sleep 180
    st=$(ssh -i $K -o ConnectTimeout=20 $H 'r=$(grep -q RESULT ~/run-min.log 2>/dev/null && tail -1 ~/run-min.log); e=$(awk "/^== .* source: /{n=0} / error: /{n++} END{print n+0}" ~/rh-build/build-min.log); echo "$e|$r"') || continue
    e=${st%%|*}; r=${st#*|}
    if [ -n "$r" ] && [ "$e" = 0 ]; then echo "$(date -u +%H:%M) merged $n CLEAN: $r"; exit 0; fi
    if [ "$e" = "$last" ]; then still=$((still+1)); else still=0; fi; last=$e
    if [ "$e" -gt 0 ] && { [ -n "$r" ] || [ "$still" -ge 2 ]; }; then
      out=$(ssh -i $K $H 'cd ~/research/min; awk "/^== .* source: /{f=0} /^== .*merged [0-9]+ source:/{f=1} f && / error: /" ~/rh-build/build-min.log | grep -o "src/[^:]*\.lean" | sed "s#^src/##; s#\.lean\$##; s#/#.#g" | sort -u > failing.txt
        awk -F"\t" "NR==FNR{f[\$1]=1; next} (\$1 in f){print \$2}" failing.txt bundles.tsv >> nomerge.txt; sort -u -o nomerge.txt nomerge.txt
        echo "$(wc -l < failing.txt) failing modules; $(wc -l < nomerge.txt) files now kept out of bundles"')
      echo "$(date -u +%H:%M) merged $n: $e errors. $out"; break
    fi
  done
done
echo "stopped after 20 merged rounds"; exit 1
