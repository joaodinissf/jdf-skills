#!/usr/bin/env bash
# Review-flow labels for one GitHub repository.
#
#   labels.sh setup   <owner/repo>          create or update the three labels
#   labels.sh request <owner/repo> <pr>     ask for a (new) review round
#   labels.sh verdict <owner/repo> <pr> approved|changes-requested
#   labels.sh clear   <owner/repo> <pr>     remove every review label
#   labels.sh sweep   <owner/repo> [mine|all|<login,...>]
#                                           clear merged and closed PRs (default: mine)
#
# Each change to a pull request removes the other review labels in the same
# call, so `review:requested` never sits beside a verdict.

set -euo pipefail
export GH_PAGER=cat

usage() {
  sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//' >&2
  exit 2
}

[ $# -ge 2 ] || usage
cmd=$1 repo=$2

# Sets one review label on a pull request and removes the others. With an
# empty label, removes all three.
set_label() {
  local pr=$1 keep=$2 label
  local args=()
  for label in review:requested review:approved review:changes-requested; do
    if [ "$label" = "$keep" ]; then
      args+=(--add-label "$label")
    else
      args+=(--remove-label "$label")
    fi
  done
  gh pr edit "$pr" --repo "$repo" "${args[@]}" >/dev/null
  gh pr view "$pr" --repo "$repo" --json number,labels \
    --jq '"#\(.number) " + ([.labels[].name | select(startswith("review:"))] | join(",") | if . == "" then "(no review label)" else . end)'
}

case $cmd in
  setup)
    gh label create review:requested --repo "$repo" --force --color FBCA04 \
      --description "Ready for a first review or a new round; replaces any previous review state."
    gh label create review:approved --repo "$repo" --force --color 0E8A16 \
      --description "Current head approved with applicable CI green; manual and human merge gates still apply."
    gh label create review:changes-requested --repo "$repo" --force --color D93F0B \
      --description "Latest review has unresolved findings; re-request review after addressing them."
    ;;
  request)
    [ $# -eq 3 ] || usage
    set_label "$3" review:requested
    ;;
  verdict)
    [ $# -eq 4 ] || usage
    case $4 in approved | changes-requested) ;; *) usage ;; esac
    set_label "$3" "review:$4"
    ;;
  clear)
    [ $# -eq 3 ] || usage
    set_label "$3" ""
    ;;
  sweep)
    [ $# -le 3 ] || usage
    authors=${3:-mine}
    case $authors in
      all) filters=("") ;;
      mine) filters=(--author=@me) ;;
      *) IFS=, read -ra logins <<<"$authors"; filters=("${logins[@]/#/--author=}") ;;
    esac
    for filter in "${filters[@]}"; do
      gh pr list --repo "$repo" --state all --limit 300 ${filter:+"$filter"} --json number,state,labels \
        --jq '.[] | select(.state != "OPEN" and ([.labels[].name] | any(startswith("review:")))) | .number'
    done | sort -u |
      while read -r pr; do set_label "$pr" ""; done
    ;;
  *) usage ;;
esac
