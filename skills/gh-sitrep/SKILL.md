---
name: gh-sitrep
description: Report everything on GitHub that waits on the user — pull requests (reviews requested, their own unlanded PRs, bot PRs in repositories they own), issues (assigned, mentioning them, untriaged in their repositories), security alerts (Dependabot, code scanning, secret scanning), red default-branch CI, deployments waiting for approval, pending invitations and unread notifications — as a few headline numbers, a per-repository breakdown and the items that need a decision. Strictly read-only. Use when asked for a GitHub sitrep, "what's waiting on me", "how many open PRs or issues do I have", a dependency-PR or security-alert count, or a check of the backlog across projects.
---

# GitHub sitrep

*A few numbers you can keep an eye on, and the short list behind them.*

Work on GitHub piles up in several ways. Someone asks you for a review. You
open something and never land it. A bot opens dozens of pull requests in
repositories you forgot you own. Someone files an issue nobody answers. A
security alert sits in a tab nobody visits. Each one is cheap on its own;
together they become a backlog nobody can size. This skill sizes it. It gives a
few numbers the user can track over time, and the short list of items that move
them.

It changes nothing. It does not comment, merge, close, rebase, label or
re-request. Every action it suggests goes to the user as a proposal.

## Who counts as "the user's"

Resolve this; do not assume it. Every bucket depends on the answer.

- **The account:** `gh api user -q .login`.
- **Owners the user answers for:** the personal account, plus each
  organisation where the user is an admin or owner. List the user's
  organisations, check each one's role, and **show the list and ask the user
  to confirm it before reporting**. Being a member of an organisation does not
  make its pull requests the user's.
- **Forks:** a fork the user owns is theirs, but a pull request from it into
  the parent repository waits on the parent's maintainers. Report it under
  "waiting on others".
- **Exclude archived repositories** from every query (`archived:false`).

The search syntax spells the owner scope as
`user:<login> org:<org1> org:<org2>`.

## The buckets

### Pull requests

| Bucket | Meaning | Search query (all `is:pr is:open archived:false`) |
|---|---|---|
| **Review requested** | Someone is blocked on the user | `review-requested:@me` |
| **Assigned** | Explicitly handed to the user | `assignee:@me` |
| **Mine, in my repos** | The user's own work, not yet landed | `author:@me` + owner scope |
| **Mine, elsewhere** | Contributions waiting on other maintainers | `author:@me` minus owner scope |
| **Bots, in my repos** | Dependency updates nobody has triaged | `author:app/dependabot` (and `app/renovate`, …) + owner scope |

Search for `review-requested` directly, not through `user-review-requested`.
`review-requested` also counts requests made to a team the user belongs to,
and those still wait on the user.

Also count `mentions:@me` among open pull requests. These are threads where
someone asked the user something without making a formal review request.

### Issues

| Bucket | Meaning | Search query (all `is:issue is:open archived:false`) |
|---|---|---|
| **Assigned** | Work handed to the user | `assignee:@me` |
| **Mentioning me** | Someone is waiting for an answer | `mentions:@me` |
| **Untriaged, in my repos** | Opened by others; nobody has replied | `comments:0 -author:@me` + owner scope |
| **Mine** | Issues the user filed that are still open | `author:@me` |

The untriaged bucket can be large and noisy, because bots file issues too.
Report the count. List the oldest few, and split out any whose author is a
bot.

### Security alerts

These are the items most likely to need attention and least likely to be seen,
because they sit in a repository's Security tab.

- **Dependabot alerts:** for an organisation,
  `gh api "orgs/<org>/dependabot/alerts?state=open&per_page=100" --paginate`.
  For a personal account there is no account-wide endpoint, so loop over
  `repos/<owner>/<repo>/dependabot/alerts?state=open`. Count the alerts by
  `.security_advisory.severity`.
- **Code scanning** and **secret scanning:** the same pattern, at
  `orgs/<org>/code-scanning/alerts` and `orgs/<org>/secret-scanning/alerts`, or
  per repository.

Report the number at each severity, critical first. If any alert is critical
or high, list each one with its repository, package and advisory. If an
endpoint is refused or returns nothing, the feature may be off, or the user may
lack the permission to read it. Say "not readable" or "none", whichever is
true; never fold the refusal into a 0.

### Everything else that waits on the user

- **Red default-branch CI.** It isn't a pull request, but it blocks every pull
  request that lands after it, and it is how a merge done without waiting for
  CI shows up later. For each repository in the owner scope that has open
  pull requests or recent pushes, check the newest run on the default branch.
  Report the repositories where that run failed.
- **Deployments waiting for approval:**
  `repos/<owner>/<repo>/actions/runs?status=waiting`. A run sits here until
  someone approves it.
- **Invitations:** `user/repository_invitations` and
  `user/memberships/orgs?state=pending`. Invitations expire.
- **Notifications:** `notifications` (unread) and
  `notifications?participating=true`, grouped by `.reason`. Report the
  participating count. The rest is mostly subscription noise.

## How to query

**Count with the GraphQL search API**, which returns a total without paging:

```sh
gh api graphql -f query='query($q:String!){search(query:$q,type:ISSUE,first:1){issueCount}}' \
  -f q='is:pr is:open archived:false review-requested:@me' -q .data.search.issueCount
```

**Break down by repository** by paging through the nodes:

```sh
gh api graphql --paginate -f query='query($q:String!,$endCursor:String){
  search(query:$q,type:ISSUE,first:100,after:$endCursor){
    pageInfo{hasNextPage endCursor}
    nodes{... on PullRequest{number title url createdAt isDraft mergeable
      repository{nameWithOwner} reviewDecision}}}}' \
  -f q='<bucket query>' -q '.data.search.nodes[]'
```

**Cross-check CLI shortcuts against the API.** A convenience command can
silently return nothing for a query the search API answers, especially when
filtering on bot authors. If a shortcut and the API disagree, report the API's
number and say that they disagreed.

**Confirm every zero.** The search API sometimes returns an empty result, with
a count of 0 and no rows, and no error. Re-run the query each time a bucket
comes back empty, and report 0 only when two runs agree. Also check every count
against the number of rows the same query returned. If they disagree, run the
query again; do not pick one of the two.

**Expect lag.** The search index trails real state by minutes. If the user has
just merged or closed pull requests, a bucket can still count them. When a
number must be exact right now, re-list that one repository with
`gh pr list --repo <repo> --state open` and say which numbers you re-checked.

## The report

Lead with the numbers, then give the detail.

1. **Headline:** one line per bucket with its count, grouped as pull requests,
   issues, security and other. Put critical and high alerts first, in their
   own line. Keep the bucket names the same in every report so the user can
   compare reports over time.
2. **Waiting on the user, oldest first:** review requests, assigned items,
   mentions, waiting deployments and invitations, with age and a link.
3. **Per repository:** a table with one row per repository and one column per
   bucket. Sort by total.
4. **Decisions:** the short list worth acting on:
   - The user's own pull requests that are conflicting, failing, approved but
     unmerged, or older than a month.
   - Draft pull requests left open for a long time.
   - Bot pull requests that are conflicting or old enough that a rebase
     request will probably close them as superseded.
   - Stacked pull requests, grouped as one stack, not counted as unrelated
     items.
5. **Red default branches**, with the failing workflow and a link to the run.
   **Critical and high alerts**, each with its repository, package and a link
   to the advisory.
6. **Links:** a clickable `https://github.com/pulls?q=…` address for each
   bucket, URL-encoded. The user can bookmark these and needs no tool to check
   again.
7. **Gaps:** name what the report does not cover. That includes other hosts
   (GitLab, Gitea, …), owners the user chose to leave out of scope, and any
   repository the API refused to show.

**An empty bucket is a valid answer.** Print it as 0. Never fill a bucket with
near-misses so that it has something in it.

## Rules

- Read-only, always. When the report suggests an action, such as closing
  superseded bot pull requests, asking for rebases or landing an approved PR,
  make it a proposal. The user approves each batch separately.
- Report numbers you measured. If a number came from a stale index or a
  partial page, say so next to it.
