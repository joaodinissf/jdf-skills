# review-flow

*The labels say whose turn it is. The models keep each other honest.*

Runs pull-request review between coding agents on GitHub. One agent
implements, a different model reviews, an orchestrator keeps the flow in
order, and a human merges. Three labels carry the state:

| Label | Colour | Meaning |
|---|---|---|
| `review:requested` | `#FBCA04` | Ready for a first review or a new round. |
| `review:approved` | `#0E8A16` | Current head approved with CI green. |
| `review:changes-requested` | `#D93F0B` | Latest review has unresolved findings. |

Any agent can take a role from any repository:

```text
/review-flow setup        owner/repo     create the labels, sweep stale ones
/review-flow implement    owner/repo     open drafts early, re-request after every push, watch them
/review-flow review       owner/repo     poll for review:requested, review, post, set the verdict
/review-flow orchestrate  owner/repo     label hygiene, routing, merges with the human's OK, releases
```

Options: `pr=<n>`, `every=5m`, `for=3h`, and `post` (default) or `draft` for
the reviewer.

The reviewer and the orchestrator poll until their time runs out, so you can
start one and leave it. The reviewer refuses work its own model wrote. Only
the human marks a pull request ready, and nothing merges without a clean
approval at the current head and the human's OK.

`scripts/labels.sh` sets one review label and removes the other two in one
call, so a stale verdict never sits beside a new request.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s review-flow
```

Needs the GitHub CLI (`gh`), signed in with access to the repository.
