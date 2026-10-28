---
name: review-flow
description: Run label-routed pull-request review between coding agents on GitHub. One agent implements, a different model reviews, and an orchestrator keeps labels, merges and releases in order; three labels (review:requested, review:approved, review:changes-requested) carry the state. Modes set up a repository, or make this agent the implementer, the reviewer or the orchestrator, polling for its work. Use when the user invokes /review-flow, asks an agent to act as implementer, reviewer or orchestrator for a repository, or asks to set up agent review labels.
disable-model-invocation: true
argument-hint: "<setup|implement|review|orchestrate> [owner/repo] [pr=<n>] [every=5m] [for=3h] [post|draft]"
---

# Review flow

*The labels say whose turn it is. The models keep each other honest.*

Several agents work on one repository. One writes a pull request, another
model reviews it, and a human merges. They do not talk to each other
directly. The pull request's review label says whose turn it is, and every
agent polls for the labels that concern it.

## Arguments

`/review-flow <mode> [owner/repo] [options]`

- **mode:** `setup`, `implement`, `review` or `orchestrate`.
- **owner/repo:** the GitHub repository. Default: the current checkout's
  `origin`.
- **pr=<n>:** limit the work to one pull request (repeatable).
- **every=<interval>:** the polling interval. Default `5m`.
- **for=<duration>:** how long to keep polling. Defaults: reviewer `3h`,
  implementer `2h` per pull request, orchestrator `3h`.
- **post** or **draft:** whether the reviewer posts on GitHub by itself
  (`post`, the default) or shows its draft to the human first (`draft`).

If the mode is missing, ask for it. Never guess a role.

## The labels

| Label | Colour | Meaning |
|---|---|---|
| `review:requested` | `#FBCA04` | Ready for a first review or a new round; replaces any previous review state. |
| `review:approved` | `#0E8A16` | Current head approved with applicable CI green; manual and human merge gates still apply. |
| `review:changes-requested` | `#D93F0B` | Latest review has unresolved findings; re-request review after addressing them. |

Rules that every mode follows:

1. **One review label at a time.** Every change sets one label and removes the
   other two in the same call. Use `scripts/labels.sh`; it does this.
2. **A verdict belongs to a head.** A push makes the old verdict stale, so the
   implementer re-requests review after every push.
3. **Merged or closed pull requests carry no review label.** Whoever merges or
   closes removes it at once; the orchestrator sweeps for leftovers.
4. **Labels are for agents. GitHub's ready state is for humans.** Only the
   human moves a draft to ready. Never undo the human's change.
5. **The reviewer is never the implementer's model.** See
   [Model independence](#model-independence).
6. **Nothing merges without a clean approval at the current head and the
   human's explicit OK** for that pull request, given at that moment.

`scripts/labels.sh` takes `setup`, `request`, `verdict`, `clear` and `sweep`.
Run it with no arguments for usage.

## Attribution

Everything an agent writes on GitHub ends with one line naming its model, on
its own line after a blank line:

```text
<sub>Assisted by <model></sub>
```

For example `<sub>Assisted by Claude</sub>` or `<sub>Assisted by Codex</sub>`.
Commits end with the `Co-Authored-By:` trailer the agent's host prescribes.
Text on GitHub must stand on its own: no references to chat, sessions, local
files or other agents' private notes.

## Polling

The reviewer and the orchestrator are watchers: started once, they keep
checking until their time runs out. The implementer watches only the pull
requests it labelled.

Use the host's own scheduler when it has one (for example `/loop`,
`ScheduleWakeup` or a cron tool). Otherwise run a shell loop with `sleep` in
the background and read its output when it ends. Each tick:

1. Query GitHub for the work that concerns you (below).
2. Do it, or note that there is none.
3. Report one line per tick: the time, what you found, what you did.

A quiet tick costs one query; do not start other work to fill it. Stop when
`for` runs out, when there is nothing left to watch, or when the human says
so. At the end, report what you did and what is still open.

When a tick fails (network, authentication, rate limit), report it and retry
on the next tick. After three failures in a row, stop and tell the human.
Never present a degraded run as a result.

## setup

1. Check access: `gh auth status` and `gh repo view <owner/repo>`.
2. `scripts/labels.sh setup <owner/repo>`. It creates the labels, or updates
   their colour and description; running it again changes nothing.
3. Remove any other review-routing labels only if the human confirms them by
   name.
4. `scripts/labels.sh sweep <owner/repo>`.
5. Show the human this paragraph for the repository's agent instructions
   (`AGENTS.md`, `CLAUDE.md` or similar), and add it only if they agree:

   > Pull requests are reviewed by agents through three labels:
   > `review:requested`, `review:approved`, `review:changes-requested`. Set
   > one and remove the other two in the same call. After every push to a
   > pull request, set `review:requested` again. Remove all three when it
   > merges or closes. The reviewing model is never the implementing model.
   > Only a human marks a pull request ready, and nothing merges without a
   > clean approval at the current head and a human's OK.

## implement

You write the change. You never review, approve or merge it.

**Start.**

1. Work in your own git worktree on a new branch from the up-to-date default
   branch. Never commit to the default branch, and never touch another
   agent's worktree.
2. Follow the repository's own instructions for commits, tests and pull
   request descriptions.

**Open the pull request early.**

1. As soon as the commits exist, push and open the pull request **as a
   draft**, then `scripts/labels.sh request <owner/repo> <pr>`.
2. Run the slower local checks after that, not before. If one fails, fold the
   fix in (below) and request review again.

**After every push,** run `scripts/labels.sh request <owner/repo> <pr>`.

**Fix review findings in place.**

1. Fold each fix into the commit it fixes: `git commit --fixup=<sha>`, then
   `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash <base>`.
2. Push with `git push --force-with-lease`, to your own branch only.
3. Reply to each finding by its number or thread, naming the commit that
   fixes it. If you disagree, say why; do not resolve a thread you did not
   fix.

If the repository's instructions say to stack fix commits instead, follow
them.

**Watch** each pull request you labelled, every `every`, for up to `for`
after its last request:

| You see | Do |
|---|---|
| `review:changes-requested` | Read the review, fix, push, request review again. |
| `review:approved` | Stop watching it. Report it as ready for the human. |
| Red CI on your head | Fix it, push, request review again. |
| Merge conflict with its base | Rebase onto the base, push, request review again. |
| A question from the human | Answer it, then go on watching. |

**Never:** approve, merge or close; add or remove human reviewers; mark a
draft ready; push to a branch someone else works on; review your own work.

## review

You judge other agents' pull requests. You never change them.

**Each tick,** list the open pull requests labelled `review:requested`
(limited to `pr=` if given):

```sh
gh pr list --repo <owner/repo> --label review:requested --state open \
  --json number,title,headRefOid,author,isDraft
```

For each one:

1. **Skip unchanged work.** Find your own latest review on it. If its body
   carries `<!-- review-flow head=<sha> -->` with the current head, skip the
   pull request: the label is stale, so set the verdict label you gave then.
2. **Check independence.** Read the commits' `Co-Authored-By:` trailers and
   the `Assisted by` lines. If your model wrote any of it, do not review it.
   Leave the label and tell the human once. If no line names a model, review
   it.
3. **Review at the head.** Fetch `pull/<n>/head` and read the diff against its
   base, the description, the linked issue, earlier review threads and CI.
   Check that every earlier finding is fixed or answered.
4. **Write the review.**
   - Lead with the verdict in one sentence.
   - Number the findings. Give each a `file:line`, the concrete failure (this
     input, this state, this wrong result) and a severity: P1 blocks the
     merge, P2 should be fixed, P3 is optional.
   - Put line-specific findings inline when the host allows it.
   - Keep it short. Report only what you checked; mark a doubt as a doubt.
   - End with the hidden marker `<!-- review-flow head=<full sha> -->` and
     the attribution line.
5. **Post or draft.**
   - With `post` (the default), post one review per pull request:
     `gh pr review <n> --approve` if there are no P1 or P2 findings,
     `--request-changes` otherwise. GitHub does not let an account approve or
     request changes on its own pull request; when it refuses, post the same
     body with `--comment` and state the verdict in its first line.
   - With `draft`, show the draft to the human and post only after their OK.
6. **Set the label** to match: `scripts/labels.sh verdict <owner/repo> <pr>
   approved` or `changes-requested`. An approval needs green required CI at
   that head; while CI is still running, wait for it on a later tick.

If the head changes while you review, discard the review and start again on
the next tick.

**Never:** commit, push, rebase, merge or close; edit the pull request's
title, body or other labels; request human reviewers.

## orchestrate

You keep the flow moving for the human. You do not write the changes, and you
do not review them.

**Each tick:**

1. **Label hygiene.**
   - Run `scripts/labels.sh sweep <owner/repo>`.
   - Fix any open pull request whose label contradicts its state: two review
     labels, a verdict older than the head, or `review:requested` on a pull
     request whose head has a fresh review marker.
   - Check a pull request's state before labelling it.
2. **Routing.** Report pull requests that wait on someone:
   - approved and ready for the human;
   - changes requested with no push since;
   - requested for longer than two reviewer ticks with no review;
   - red CI or merge conflicts.
3. **Merges.**
   - Propose them one at a time. Merge only after the human's explicit OK for
     that pull request at that moment, with the repository's merge method and
     a head check (`gh pr merge <n> --match-head-commit <sha>`).
   - Clear its review labels at once: `scripts/labels.sh clear`.
   - Leave the next merge until the previous one's release or deploy pipeline
     has reached its verification stage. On many pipelines a new push to the
     default branch cancels the previous commit's runs, so quick merges skip
     their checks.
4. **Releases.**
   - Judge a pipeline by its gate: the commit status or check it publishes,
     or the deployed version. Never judge it by a workflow run's conclusion,
     because a run whose jobs were all skipped also reports success.
   - Report a failed or cancelled stage at once.

**Never:** merge, close, promote or deploy without the human's OK for that
item; request human reviewers unless the human says so; delete branches,
worktrees or sessions that are not yours.

## When something goes wrong

Stop and report: what you saw, what you think caused it, what you propose.
Do not chain fixes the human did not ask for. Do not retry a refused action
in another way.
