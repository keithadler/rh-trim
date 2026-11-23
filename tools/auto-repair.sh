#!/usr/bin/env bash
# Repair loop for the minified build: when a round's errors stop growing (or the build ends), feed them to
# repair.py and start the next round; stop on a clean result. Prints one line per round.
cd ~/rh-sandbox
H=ubuntu@77.112.217.157; K=~/.ssh/rh-build
round=$(ssh -i $K $H 'grep -o "round [0-9]* source" ~/rh-build/build-min.log | tail -1 | grep -o "[0-9]*"')
last=-1; still=0; t0=$(date +%s)
while [ "$round" -lt 120 ]; do
  sleep 180
  st=$(ssh -i $K -o ConnectTimeout=20 $H 'r=$(grep -q RESULT ~/run-min.log 2>/dev/null && tail -1 ~/run-min.log); e=$(awk "/^== .* source: /{n=0} / error: /{n++} END{print n+0}" ~/rh-build/build-min.log); echo "$e|$r"') || continue
  e=${st%%|*}; r=${st#*|}
  if [ -n "$r" ] && [ "$e" = 0 ]; then echo "$(date -u +%H:%M) round $round CLEAN: $r"; exit 0; fi
  if [ "$e" = "$last" ]; then still=$((still+1)); else still=0; fi; last=$e
  if [ "$e" -gt 0 ] && { [ -n "$r" ] || [ "$still" -ge 2 ] || [ $(( $(date +%s) - t0 )) -ge 1200 ]; }; then
    ssh -i $K $H 'tac ~/rh-build/build-min.log | sed "/^== .* source: /q" | tac' > /tmp/build-min.log
    rep=$(python3 tools/repair.py /tmp/build-min.log decls-project.tsv extra-names.txt revert-files.txt); rc=$?; rep=$(echo "$rep" | grep -v "^  unmatched" | tr "\n" " ")
    if [ $rc = 3 ]; then echo "$(date -u +%H:%M) round $round STUCK: $rep"; exit 2; fi
    round=$((round+1)); echo "$(date -u +%H:%M) round $((round-1)): $e errors. $rep"
    tools/min-round.sh "round $round" 2>&1 | grep "source:" ; last=-1; still=0; t0=$(date +%s)
  fi
done
echo "stopped after 120 rounds"; exit 1
