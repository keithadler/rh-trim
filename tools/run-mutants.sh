#!/usr/bin/env bash
# Give every file in DIR (the clean slice first, then each mutant) to every kernel; one TSV row per
# (file, kernel): exit code, wall seconds, last line of output.
#   run-mutants.sh DIR CLEAN.ndjson [JOBS]
set -u
DIR=$1; CLEAN=$2; JOBS=${3:-16}
L=$(ls -d ~/.elan/toolchains/*v4.36.0*)/bin; K=~/kernels
OUT=$DIR/verdicts.tsv
one() {
  f=$1; kern=$2; base=$(basename $f .ndjson)
  case $kern in
    lean)     cmd=("$L/leanchecker" --from-export "$f") ;;
    paranoid) cmd=("$L/leanchecker-paranoid" --silent --from-export "$f") ;;
    nanoda)   cfg=$(mktemp --suffix=.json)
              printf '{"export_file_path":"%s","permitted_axioms":["propext","Quot.sound","Classical.choice","Lean.trustCompiler"],"unpermitted_axiom_hard_error":false,"nat_extension":true,"string_extension":true,"print_success_message":true}' "$f" > "$cfg"
              cmd=("$L/nanoda_bin" "$cfg") ;;
    tenet)    cmd=("$K/tenet/tenet" check "$f" --quiet --jobs 1) ;;
    tenet-hs) cmd=("$K/tenet-hs-bin" check "$f" --summary) ;;
    tenet-jvm) cmd=(env JAVA_TOOL_OPTIONS=-Xmx8g "$K/tenet-jvm/bin/tenet-jvm" "$f") ;;
  esac
  s=$(date +%s.%N)
  tmp=$(mktemp); timeout 300 "${cmd[@]}" > "$tmp" 2>&1; rc=$?
  e=$(date +%s.%N)
  res=$(tail -c 300 "$tmp" | tr '\n\t' '  '); rm -f "$tmp"
  [ "$kern" = nanoda ] && rm -f "$cfg"
  printf '%s\t%s\t%s\t%.2f\t%s\n' "$base" "$kern" "$rc" "$(echo "$e - $s" | bc)" "$res"
}
export -f one; export L K
: > $OUT
{ echo "$CLEAN"; ls $DIR/m*.ndjson; } | while read f; do
  for k in lean paranoid nanoda tenet tenet-hs tenet-jvm; do echo "$f $k"; done
done | xargs -P "$JOBS" -n 2 bash -c 'one "$0" "$1"' >> $OUT
echo "wrote $OUT ($(wc -l < $OUT) rows)"
