---
name: silly-sweep
description: Sweep a codebase for code that misleads — reimplemented stdlib, comments that contradict the code, checks that cannot fail, tests that do not discriminate, dead weight. Fans out read-only agents by directory and returns ranked findings. Use when asked to look for code smells, cruft, cleanup opportunities, dead code, or "anything silly" in a repo.
---

# Silly sweep

*Sweep the silly away.*

Silly code *misleads*. Not ugly code, not slow code — code that tells a
reader something untrue. A comment describing behaviour that was removed. A guard
that cannot detect the thing it guards against. A test that passes with the
implementation deleted. These cost more than bugs, because a bug is eventually
observed and this is believed.

Rank by how confidently a reader would be misled, not by how odd it looks.

## The taxonomy

Language-agnostic. Every item below has been found in real code in more than one
language; none depends on a particular tool, framework or version.

### 1. Reimplemented standard library
A hand-rolled loop doing what the language ships. Substring search, sorting, key
extraction, prefix trimming, set membership, min/max, error comparison.
*Why it misleads:* the reader assumes a hand-rolled version exists because the
built-in was insufficient, and hunts for the subtlety. There isn't one.

### 2. Comment contradicts code
The comment describes what the code used to do. Includes doc comments, module
headers, README fragments and configuration comments.
*Why it misleads:* worse than no comment. A reader trusts prose over code, so this
inverts the truth rather than merely omitting it.

### 3. A check that cannot fail
A validation, guard, health check or preflight that passes regardless of the
condition it names. Reading a public resource to prove write access. Asserting a
value is non-empty when the failure mode is that it is *wrong*. Catching an
exception that cannot be raised.
*Why it misleads:* it converts an unprotected path into one that looks protected —
strictly worse than no check, because it stops anyone adding a real one.

### 4. A test that does not discriminate
It passes with the implementation removed. Common causes: the assertion is
satisfied by a coincidence of the fixture; the fixture omits the case that
distinguishes correct from incorrect; the test asserts shape rather than behaviour.
*How to check:* mentally delete the implementation. Does the test still pass? If
so, say so — that is the finding.

### 5. Loudness undone at a boundary
A function returns an error and its caller logs-and-continues, so the stated
contract ("fails loudly") is false one layer up. Also: an error swallowed in a
retry, an exception caught and dropped, a non-zero exit ignored by a wrapper.
*Why it misleads:* the loudness is real in the unit and absent in the system, so
tests and code review both endorse it.

### 6. Nondeterministic selection
Choosing one element from an unordered collection — a hash map, a set, a directory
listing, a concurrent result set — and treating the choice as stable. The symptom
is a decision, an error message or an output that differs between runs.
*Why it misleads:* it works when you check it and fails for someone else.

### 7. Dead weight
Written but never read. Declared but never used. Exported with no caller. A
configuration option nothing consults. An injected value nobody reads. A field
populated for an audience that does not exist.
*Why it misleads:* a reader assumes something depends on it and preserves it
through every refactor.

### 8. Drifted duplication
The same non-trivial logic in several places where the copies no longer agree. The
divergence is the finding; identical copies are merely a refactor opportunity.

### 9. Misleading name
The name promises one thing and the body does another. A validator that mutates. A
getter that writes. A "temporary" workaround older than most of the file.

### 10. Absurd construct
Comparing a boolean to a boolean literal. A conditional whose branches are
identical. A null check after a guaranteed-non-null. A lock guarding nothing. A
retry that cannot succeed on a second attempt. Catching and rethrowing unchanged.

## How to run it

Discover the repo's shape first, then partition. Do not hardcode a layout — it
will be wrong for the next project.

1. Identify the languages and the top-level source directories (build manifests,
   workspace files, or just the directory tree).
2. Partition into **6–10 areas** of roughly comparable size. Group small
   directories; split a large one by subdirectory.
3. One agent per area, in `parallel()`. Use **Sonnet** — this is pattern-matching
   over a lot of text, not deep reasoning, and the volume matters more than the
   depth.
4. A final agent ranks and de-duplicates.

### Rules every sweep agent needs

Include these verbatim in each agent prompt. The first one exists because a sweep
without it will run for hours and return nothing:

```
HARD BUDGET: target 15 tool calls, maximum 25, then answer with what you have.
A partial answer delivered beats a thorough one that never arrives.

DO NOT run the build, the full test suite, or any whole-repo compile. On a large
repo these take hours and are not needed to spot silly code.

Report only what you VERIFIED by reading the code. No "might be", no "consider
whether". If you did not read it, it does not go in.

Skip generated code entirely: vendored directories, build output, anything with a
"do not edit" header, lockfiles, compiled schemas.

Skip test files unless the silly thing is the test itself (category 4).

An empty findings list is a valid and useful answer. Do not pad.
```

### A trap worth naming

Search tools take single-letter flags that silently change behaviour rather than
erroring. In ripgrep, `-r` is `--replace` and `-E` is `--encoding`; a pattern like
`rg -ril foo` rewrites every match to `il` and looks like a result. Instruct agents
to use long flags (`--line-number`, `--fixed-strings`, `--glob`) so output is never
silently mangled. A mangled grep does not fail — it invents a finding.

### Schema

Ask for structured output so the ranking phase has something to sort:

```
category   one of the ten above
file       repo-relative
line       integer
what       one sentence: what is silly, and what it should be
severity   high = actively misleads or hides a bug
           medium = wastes a reader's time
           low = cosmetic
```

### Report shape

- **Worth fixing** — a table, high severity first, capped at ~20 rows. Say how many
  were cut rather than silently truncating.
- **Cosmetic** — one line each, no table.
- **Clean areas** — name them. "Nothing here" is information.
- **Patterns** — anything in three or more places is a codebase habit, not an
  instance. Name it as a habit; that is the finding worth acting on.

## Calibration

Three failure modes, in order of how much damage they do:

**Confident wrongness about someone else's rules.** The most dangerous finding is
one that calls correct code broken, because acting on it breaks something that
worked. It happens when a sweep judges code written against a framework, DSL,
template language or library whose conventions it is guessing at. A real example:
a sweep declared a package-manager formula "invalid syntax" and claimed every
build using it would fail. The line was the framework's documented idiom.

So: **if a claim depends on how an external thing behaves, verify it against that
thing's documentation or source, or downgrade it to a question.** Say "this looks
unusual for X — worth confirming" rather than "this is broken". Include this rule
in every agent prompt; it is the one that prevents actively harmful output.

**Padding.** An agent that finds nothing tends to invent something. Say explicitly
that empty is fine, and drop anything phrased as a question rather than a claim.

**Style complaints.** Naming preferences, formatting, "this could be a switch" —
the linter's job, not this. If removing it would not change what a reader believes
about the code, it is not a finding.

When unsure whether something qualifies, ask: *would a competent reader form a
false belief from this?* If no, drop it.

And before reporting anything as high severity, ask the inverse: *if I am wrong
about this, what happens to whoever acts on it?* High severity is a claim that
someone should change working code. Earn it.

## After the sweep

Findings in categories 3 and 4 — checks that cannot fail, tests that do not
discriminate — are the ones to act on first. Both mean something is currently
believed to be protected and is not, so they carry the highest chance of a live
defect hiding behind them.

Category 2 findings are the cheapest to fix and the most valuable per line changed:
correcting a lying comment costs one edit and removes a permanent trap.
