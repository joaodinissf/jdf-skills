---
name: handover
description: Write a HANDOVER.md that lets the next session continue this one without repeating its mistakes, or resume from one. Every claim in it is checked against the repository before it is written, and resuming starts by checking what changed since. Use when the user invokes /handover, or /handover resume.
disable-model-invocation: true
argument-hint: "[resume] [focus or notes]"
---

# Handover

*Leave the next session a map, not a memory.*

A session ends with knowledge that is in no file: what was tried and failed,
why a decision went one way, which command proves the work. The next session
starts without it and pays for it again. A handover writes that knowledge
down, at the project root, in a form the next session can check.

Two modes:

- `/handover [notes]` writes `HANDOVER.md`.
- `/handover resume` reads it, checks it against the repository, and reports
  before any work starts.

## Write

### 1. Collect the state

Run only these commands:

- `git rev-parse --show-toplevel`, `git branch --show-current`,
  `git rev-parse --short HEAD`
- `git status --short`, `git diff --stat`, `git log --oneline -15`
- `date '+%F %T'`

Do not run other commands to fill the document. Do not read environment
variables, home-directory dotfiles, or any file outside the repository.

### 2. Check before you write

Write from the conversation, then check each claim before it goes in:

- A file, function or path you cite: open it and confirm it exists and says
  what you claim.
- "Done" or "works": cite the evidence from this session (a test run, a
  command output, a commit). If there is none, the item is not done.
- A claim you could not check: keep it only if it matters, and mark it
  `(unverified)`.

A handover that is wrong costs more than one that is short.

### 3. Write HANDOVER.md

Replace the file; do not append. If a `HANDOVER.md` already exists, read it
first and carry forward the parts that are still true: decisions still in
force and dead ends still worth avoiding. Drop the rest.

Keep it under about 150 lines. When it is too long, cut in this order:
additional notes, the file map, what worked. Never cut what failed, the
decisions, or the next step.

```markdown
# Handover: <one-line title>

<date> · branch `<branch>` · HEAD `<short sha>` <subject>
Working tree: <clean | summary>

## Goal
<what this work is for, in two or three sentences>

## Done
- <result> — <evidence: test, command, commit>

## In progress
- <item> — <state, and what is left>

## Failed or rejected
- <approach> — <why it failed or was rejected; what to do instead>

## Decisions
- <decision> — <reason>

## Traps
- <surprise, edge case or environment quirk the next session would hit>

## Check it works
`<the command that shows the work is correct, and what it should print>`

## Next step
<one task, not a menu: what to do first, and how to know it is done>

Prompt for the next session:
> <a paragraph the user can paste to start the next session>

## Files
| File | Why it matters |
|---|---|
```

Omit a section that has nothing true to say rather than padding it.

### 4. Check for secrets, then report

Never write credentials, tokens, keys, passwords or URLs that carry them. If
one matters as context, write `[redacted: <what it is>, in <file>]`.

After writing, scan the file and fix any hit:

```sh
grep -nEi '(api[_-]?key|secret|token|password|passwd|bearer)[^ ]*[:=]|-----BEGIN|ghp_|gho_|github_pat_|sk-[a-z0-9]|xox[abp]-|AKIA[0-9A-Z]{16}|://[^ /]+:[^ @]+@' HANDOVER.md
```

Do not stage or commit `HANDOVER.md`. If `.gitignore` does not list it, tell
the user they may want to add it.

Report in one or two lines: where the file is, and the next step it names.

## Resume

1. Read `HANDOVER.md`. If there is none, say so and stop.
2. Compare it with the repository:
   - `git log --oneline <sha>..HEAD` and `git diff --stat <sha>` — what
     changed since it was written;
   - the current branch against the recorded one;
   - every file it cites — does it still exist?
3. Report: the goal, the next step, and every difference you found
   ("handover says X; repository now shows Y"). Run the check command if it
   is cheap and has no side effects; otherwise say how to run it.
4. Wait for the user to confirm the next step before you work on it.

## Traps

- **Writing from memory.** The conversation says a test passed; the test was
  never run. Check, or mark it unverified.
- **A log instead of a map.** Narrating the session in order. The next session
  needs the current state and the route, not the history.
- **A menu of next steps.** Five options hand the decision back. Pick one.
- **Silent drift.** Resuming from a handover written three commits ago as if
  it were current.
