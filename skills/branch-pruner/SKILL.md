---
name: branch-pruner
description: Restore a git repository from "branches and worktrees everywhere" to a single calm checkout — delete local branches whose work is already on the default branch (detecting rebased and cherry-equivalent history, not just true merges), remove all extra worktrees when clean, and stop to ask before anything unrecoverable. Use when asked to prune branches, clean up worktrees, tidy a repo after feature work, or when told "this repo is a mess".
---

# Branch pruner

*One calm checkout; nothing lost.*

A repository accumulates scaffolding: a branch per experiment, a worktree per
review, and six months later `git branch` scrolls. The scaffolding was cheap to
create and is cheap to remove — except that one of those branches holds the only
copy of an afternoon's work, and naive cleanup cannot tell which.

This skill removes everything recoverable and refuses to guess about the rest.
Two rules carry the whole procedure: work that is already on the default branch
needs no local branch to survive, and uncommitted changes are the one thing git
cannot bring back.

## What it cleans (and what it does not)

| Object | Removed when | Kept when |
|---|---|---|
| Local branch | Its work is already on the default branch — by ancestry **or** by rebased/cherry-equivalent history | It has commits not on the default branch |
| Linked worktree | Clean — **regardless of whether its branch is merged** | Dirty; then ask, per worktree |
| Primary worktree | Never | Always |
| Remote branches | Never — local sprawl only | Always |

Worktree removal is orthogonal to merge status. A worktree is just another
checkout directory; the branch ref and its commits live in the main repository's
object database and survive `git worktree remove` untouched. An unmerged
branch's worktree can go the moment the tree is clean.

## Detect the default branch

Do not assume. Resolve it, and say which one you resolved:

```sh
git symbolic-ref refs/remotes/origin/HEAD --short
```

If that fails (no remote, or `origin/HEAD` unset), fall back to whichever of
`main` or `master` exists locally; if both exist, ask. Every classification
below is relative to this branch, so getting it wrong misclassifies everything.

## Inventory

Before touching anything, collect the full picture:

```sh
git worktree list --porcelain
git branch --list --verbose
git status --porcelain=v2
```

Identify the primary worktree (first entry in the list) versus linked ones, the
currently checked-out branch in each, and which trees are dirty. Dirty means
anything git would lose: staged changes, unstaged changes, and untracked files
that are not ignored. Run `git status` inside each linked worktree — the
top-level status does not speak for them.

## Is this branch already on the trunk? (rebase-aware)

This is the step that justifies the skill's existence, so here is the trap by
name: **git says unmerged; the work is already on master after rebase.** When a
branch lands by rebase or squash, the trunk carries equivalent patches under new
SHAs. `git branch --merged` and `git merge-base --is-ancestor` both answer no,
and a cleanup built on them keeps every rebased branch forever — or worse,
teaches its user that `--force`-deleting "unmerged" branches is normally fine.

Classify each branch with two tests, in order:

1. **Ancestry** — the true-merge case:

   ```sh
   git merge-base --is-ancestor <branch> <default>
   ```

   Exit 0 means every commit is on the trunk. Landed.

2. **Patch equivalence** — the rebase case:

   ```sh
   git cherry <default> <branch>
   ```

   Each line marked `-` has an equivalent patch already on the default branch;
   each `+` does not. No `+` lines means the work landed under different SHAs.
   Landed. An empty `git log <default>..<branch>` is **not** a substitute — after
   a rebase that range is never empty, because the old SHAs are gone from the
   trunk entirely.

Any `+` line means the branch still holds unique work. Keep it, and report the
count of unique commits so the user can see what is outstanding. Patch
equivalence is textual: a commit whose content was reworked during landing (a
squash that edited hunks, a conflict resolved differently) shows as `+` even
though its intent shipped. That is the correct answer — the skill cannot know
the intent shipped, and `+` means "deleting this loses something git considers
distinct".

Never classify these as prunable at all:

- the default branch;
- the branch checked out in the primary worktree;
- any branch checked out in a worktree that is staying.

## Order of operations

Destructive work is sequenced so each step makes the next one safe:

1. **Classify** everything using the tests above.
2. **Present the plan** before deleting anything: branches to delete (with the
   evidence — ancestor, or `git cherry` clean), branches kept and why, worktrees
   to remove, dirty items needing a decision. Mass deletion without a shown plan
   is a bug in the procedure, not a style choice.
3. **Remove clean linked worktrees** with `git worktree remove <path>`. Worktrees
   go before their branches: git refuses to delete a branch checked out in a
   worktree, and forcing that ordering leaves a worktree pointing at a ref that
   no longer exists.
4. **Delete landed branches.** Prefer `git branch --delete`; it refuses anything
   it cannot prove merged, which after a rebase means it refuses branches you
   have already proven landed. That refusal is expected, not a warning sign:
   when `git cherry` reported no `+` lines and the branch is in the shown plan,
   `git branch --delete --force` is the correct tool. `--force` on any branch
   *not* proven patch-equivalent discards unique commits and is only ever done
   at the user's explicit, informed request.
5. **Tidy registrations** with `git worktree prune` — this clears stale
   bookkeeping for worktree paths that no longer exist (moved, or deleted
   outside git); it does not touch live worktrees.
6. **Re-run the inventory** and report the final state.

Use long flags throughout (`--delete`, `--force`, `--porcelain`); short flags
differ across git subcommands and read ambiguously in a plan the user is being
asked to approve.

## Dirty means ask

A dirty worktree — or a dirty primary checkout on a branch being considered for
deletion — is a hard stop, per item. Do not batch the question. For each one,
show what is at stake (`git status --short`, and the diff on request) and offer
the real options:

- **stash** — `git stash push` inside that worktree, then remove it;
- **commit** — commit to the branch, which usually reclassifies it as unique;
- **discard** — `git worktree remove --force`, only after the user has seen
  exactly what disappears;
- **skip** — leave the worktree alone and move on.

Untracked files deserve explicit mention: they are the easiest thing to lose,
because they are invisible to every branch-level safety check. So do dirty
submodules, which `git status` in the superproject summarises to a single line.

## Report

- **Removed** — branches deleted (with which test proved them landed) and
  worktrees removed.
- **Kept** — branches with unique commits, with the count of commits not on the
  default branch. This list is the user's real to-do list; it is the point of
  the exercise, not a leftover.
- **Needs a decision** — dirty items skipped or awaiting an answer.

If there is nothing to prune, say so and stop. A tidy repository is a valid
finding, and inventing cleanup to justify the run is worse than doing nothing.

## Traps

- **Rebase-false-unmerged.** Named above; it is the whole reason this skill is
  longer than a shell alias. Any procedure that trusts `--merged` alone fails
  the rebase workflow it will most often be run against.
- **Branch before worktree.** Deleting a branch that a worktree has checked out
  either fails or, forced, strands the worktree on a dead ref. Worktrees first.
- **Force-delete as a habit.** `--force` is justified by evidence (a clean
  `git cherry`) or by an informed user choice — never by impatience with
  `--delete`'s refusal on a branch nothing has vetted.
- **Untracked files.** Invisible to merge checks, gone forever with a forced
  worktree removal. They are why "dirty" includes untracked.
- **A worktree path that no longer exists.** The directory was deleted by hand
  or lives on an unmounted disk. There is nothing to inspect for dirtiness —
  `git worktree prune` clears the registration; do not count it as a removal of
  anything real.
