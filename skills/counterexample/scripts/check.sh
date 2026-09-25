#!/usr/bin/env bash
# Rerun every formal check listed in specs/checks and compare each result with
# its expectation. Copy this file to specs/check.sh; run it from anywhere.
#
# One check per line, whitespace-separated; '#' starts a comment:
#
#   kind  path                    config           expect  note
#   tla   Claim/Claim.tla         Claim.cfg        pass    compare-and-set claim
#   tla   Claim/Claim.tla         ClaimBefore.cfg  fail    the code before the fix
#   lean  lean/Launch             Audit.lean       pass    proofs and axiom audit
#
# Paths are relative to this directory; a TLA+ config sits beside its spec.
# expect is pass or fail. An expected fail passes only on a real violation
# (invariant, action property, deadlock or liveness), never on a broken model.
# Lean checks only pass: a counterexample in Lean is a theorem that builds.
#
# Environment: TLA2TOOLS (path to tla2tools.jar), JAVA (default: java).
# Pass check files as arguments to run those instead of ./checks.

set -uo pipefail

here=$(cd "$(dirname "$0")" && pwd)
java=${JAVA:-java}
jar=${TLA2TOOLS:-$HOME/.local/share/tla/tla2tools.jar}
allowed_axioms="propext Quot.sound Classical.choice"

files=("$@")
[ ${#files[@]} -gt 0 ] || files=("$here/checks")

run_tla() { # spec config -> pass | fail | error, plus a detail line
  local spec=$1 config=$2 dir out
  dir=$(dirname "$spec")
  out=$(cd "$here/$dir" && "$java" -XX:+UseParallelGC -cp "$jar" tlc2.TLC \
    -workers auto -cleanup -metadir "${TMPDIR:-/tmp}/tlc-$$-$(basename "$spec" .tla)" \
    -config "$config" "$(basename "$spec")" 2>&1)
  local states
  states=$(grep -Eo '[0-9,]+ distinct states found' <<<"$out" | tail -1)
  if grep -q 'No error has been found' <<<"$out"; then
    echo "pass ${states:-}"
  elif grep -Eq 'is violated|Deadlock reached|Temporal properties were violated' <<<"$out"; then
    echo "fail $(grep -Eo '(Invariant|Action property) [A-Za-z0-9_]+|Deadlock reached|Temporal properties were violated' <<<"$out" | head -1)"
  else
    echo "error $(grep -Em1 'Error|error|Exception' <<<"$out" | cut -c1-120)"
  fi
}

run_lean() { # project audit -> pass | error, plus a detail line
  local dir=$here/$1 audit=$2 out axioms bad=
  if ! out=$(cd "$dir" && lake build 2>&1); then
    echo "error build failed: $(grep -m1 'error' <<<"$out" | cut -c1-120)"; return
  fi
  if grep -q "declaration uses 'sorry'" <<<"$out"; then
    echo "error a proof uses sorry"; return
  fi
  [ -f "$dir/$audit" ] || { echo "error missing $audit"; return; }
  if ! out=$(cd "$dir" && lake env lean "$audit" 2>&1); then
    echo "error audit failed: $(head -1 <<<"$out" | cut -c1-120)"; return
  fi
  grep -q 'axioms' <<<"$out" || { echo "error the audit printed no axioms"; return; }
  axioms=$(grep -o 'depends on axioms: \[[^]]*\]' <<<"$out" |
    sed 's/.*\[//; s/\]//' | tr ',' '\n' | tr -d ' ' | sort -u)
  for a in $axioms; do
    case " $allowed_axioms " in *" $a "*) ;; *) bad="$bad $a" ;; esac
  done
  if [ -n "$bad" ]; then echo "error disallowed axioms:$bad"; else echo "pass"; fi
}

total=0 mismatches=0
for file in "${files[@]}"; do
  [ -f "$file" ] || { echo "no such check file: $file" >&2; exit 2; }
  while read -r kind path config expect note; do
    case $kind in ''|'#'*) continue ;; esac
    total=$((total + 1))
    case $kind in
      tla) result=$(run_tla "$path" "$config") ;;
      lean) result=$(run_lean "$path" "$config") ;;
      *) result="error unknown kind $kind" ;;
    esac
    got=${result%% *} detail=${result#"$got"}
    if [ "$got" = "$expect" ]; then mark=ok; else mark=MISMATCH; mismatches=$((mismatches + 1)); fi
    printf '%-8s %-5s %-32s %-22s expect %-4s got %-5s %s%s\n' \
      "$mark" "$kind" "$path" "$config" "$expect" "$got" "${note:-}" "${detail:+ —$detail}"
  done <"$file"
done

echo "$((total - mismatches)) of $total checks as expected"
[ "$mismatches" -eq 0 ]
