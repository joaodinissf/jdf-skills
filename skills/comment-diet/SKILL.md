---
name: comment-diet
description: Cut comments — in code and in configuration files alike — down to the ones that are load-bearing; remove prose that restates the code, argues a decision already made, records the incident that prompted the change, or describes another file's behaviour. Use when a diff carries more comment than code, when asked to shorten or trim comments, when asked whether comments are load-bearing, or when told a change is over-documented or too verbose.
---

# Comment diet

A comment is re-read by everyone who ever reads that line, forever. That is its
price, and most comments do not repay it.

The commonest failure is not sloppiness. It is a careful explanation, written
while the reasoning was fresh, placed where the reasoning does not belong.

## Where the bloat comes from

Work out an answer, defend it, then write the defence into the file. What
lands is the argument, not the instruction — every objection raised while the
change was being made becomes a line that outlives the objection.

Three questions get confused:

| the question | where the answer belongs |
|---|---|
| what does this line do? | the code |
| why is the code like this? | a comment, if not obvious |
| why did this change? | the commit message |
| why this approach over that one? | the pull request or the issue |

Comments swell when the last two answers are written into the second position.

## The load-bearing pass

Before shortening anything, decide separately, for **every comment the change
adds or touches**, whether it is load-bearing.

A comment is **load-bearing** when removing it would let a competent reader make
a wrong change. Everything else is decoration, however true.

Make this its own pass, one comment at a time, and commit to a verdict before
looking at length. Judging the two together corrupts both: a long comment starts
to read as padding and a terse one as necessity, when length predicts neither.
Some of the most load-bearing comments are the longest, because the constraint
they carry is genuinely intricate.

State the verdict per comment; two words each is enough. A comment that cannot
be argued as load-bearing has already failed, and the tests below decide only
whether it is deleted outright or compressed to the part that survives.

## The tests

Run them in order. Each one deletes material the next would have had to judge.

**Restatement.** Does the code already say it? A comment saying a value is
guarded, beside a guard, is noise. Delete without replacement.

**Relocation.** For each remaining line, ask which of the four rows above it
belongs to. Anything about *why this changed*, *what was failing before*, or
*why the alternative was rejected* moves to the commit message or the pull
request. Cut it from the file; it is not lost, only correctly placed.
Temporal phrasing is the reliable surface marker here — *no longer*, *used
to*, *now that*, *previously* — each one a why-this-changed sentence that has
escaped into the file, meaningful only to a reader who remembers the
before-state.

**Durability.** Does it describe something outside this file — another
module's behaviour, a tool's defaults, what some other job does? That breaks
silently when the other thing changes, and nothing will catch it. Keep only if
the coupling is real and load-bearing, and then state the constraint rather
than the other file's current behaviour.

**Ratio.** Is the comment longer than the code it introduces? Not a rule, but
past roughly one line of comment per line of code, look again — the excess is
usually justification that failed one of the tests above.

**Audience.** Was the reader of this line the person it was written for? Prose
answering a reviewer's objection is addressed to the reviewer. That
conversation ended.

## What earns its place

Trimming is not deleting. These survive every pass:

- **Non-obvious environmental constraints.** Facts about the machine, the
  platform or the deployment that the code cannot show. A reader cannot derive
  these and will break things without them.
- **Dangerous invariants.** Anything where the obvious edit is wrong. State the
  consequence, not the history.
- **Why-not.** A rejected obvious approach, in one clause — this is the highest
  value-per-word comment there is, because it prevents the same wrong change
  being made repeatedly.
- **Units, ranges, ownership, lifetimes.** Anything the type system does not
  carry.
- **Deliberate omissions.** Something absent on purpose reads as an oversight
  unless it is marked.

The common thread: each is a fact a competent reader cannot recover from the
code. That is what load-bearing means in practice, and it is the whole
criterion.

## Rewriting

Compress rather than delete when a survivor is verbose. Most over-long comments
have one load-bearing clause and several supporting sentences; keep the clause.

- Lead with the constraint, not the story leading to it.
- One sentence per idea. A comment needing a paragraph break is usually two
  comments, or one comment and a commit message.
- Drop the reasoning chain, keep the conclusion. *X, so Y, which means Z*
  becomes *Z*, unless Y is itself the surprising part.
- Prefer a clause at end of line over a block above, when it fits.

## Applying to a diff

Work on added and modified comments; leave untouched ones alone unless asked.

1. List every comment in the diff with the code it introduces.
2. Give each one a load-bearing verdict, before reading it for length.
3. Run the tests in order; mark each comment keep / compress / move / delete.
4. For anything marked move, write the destination text — a commit message or
   pull request paragraph. The content survives; only its location changes.
5. Report the before/after line counts, and show the relocated prose so nothing
   is silently lost.

A change is usually right when the comments left are ones the author would have
written without having just had the argument.

## The trap

Over-correcting strips the constraints along with the justification, and a
missing constraint is far more expensive than a redundant sentence. When a
comment fails a test but you cannot tell whether it encodes a real constraint,
compress it to the constraint and keep it. Uncertainty resolves toward keeping.
