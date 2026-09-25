# jdf-skills

Agent skills for keeping a codebase honest.

Each one goes after writing that costs a reader more than it gives: code that
says something untrue, documentation that only made sense the week it was
written, comments that repay nobody for re-reading them.

## Install

```sh
npx skills add joaodinissf/jdf-skills --all      # everything
npx skills add joaodinissf/jdf-skills --list     # see what's here
npx skills add joaodinissf/jdf-skills -s <name>  # just one
```

## Skills

### [`silly-sweep`](skills/silly-sweep) — sweep the silly away

Finds code that **misleads**: a comment describing behaviour that was removed, a
guard that cannot detect what it guards against, a test that passes with the
implementation deleted. Ten categories, ranked by how confidently a reader would
be misled. Fans out read-only agents by area and returns ranked findings.

Not ugly code, not slow code — only code that tells a reader something untrue.

### [`perennial-docs`](skills/perennial-docs) — write the destination, not the path

Finds documentation written as a record of the work that produced it: examples
taken from the last thing touched, warnings about obstacles hit once, ordering
that follows how the work happened. Such a document is usually accurate the day
it is written, which is why it survives review, and useless a year later.

General patterns last. Episodes rot.

### [`comment-diet`](skills/comment-diet) — keep only what is load-bearing

Cuts comments back to the ones that earn their place. A comment is load-bearing
when removing it would let a competent reader make a wrong change; everything
else is decoration, however true. Judges that per comment as its own pass, then
routes what fails — a rejected alternative belongs in the pull request, a reason
for the change belongs in the commit message, neither belongs in the file.

The constraints survive; the argument that produced them does not.

### [`technical-english`](skills/technical-english) — say it so it can be used

Writes clear, controlled technical English inspired by ASD-STE100. It gives
procedures one action per sentence, prefers active voice and stable terminology,
and cuts idiom, filler, and vague claims. It applies from invocation until the
task ends. It does not claim formal ASD-STE100 compliance without the standard's
controlled dictionary.

### [`branch-pruner`](skills/branch-pruner) — one calm checkout, nothing lost

Restores a repository from "branches and worktrees everywhere" to a single calm
checkout. Deletes local branches whose work is already on the default branch —
detecting rebased and cherry-equivalent history, not just true merges, because
`git branch --merged` answers wrongly for a rebase workflow. Removes all extra
worktrees when clean, even for unmerged branches; the refs and commits survive
in the main repository. Anything dirty is a hard stop and a per-item question.

Work that landed needs no branch to survive; uncommitted work git cannot bring
back.

### [`uber-updater`](skills/uber-updater) — find every manager; change nothing without a yes

A machine accumulates package managers the way a house accumulates keys: the
system one, the language ones, the version managers, and several that arrived as
a dependency of something else. Each has its own verb for *what is old*, so
whatever its owner remembers gets updated often and everything else quietly rots.

Detects every manager by probing rather than recalling, collects what each one
reports as out of date, and tiers it by blast radius — packages, applications,
toolchains — because a runtime moving a major version breaks things a library
never could. Two hard stops: one to choose the scope, one to confirm the exact
commands. What no update can fix — shadowed installs, orphans, packages needing
removal rather than upgrade — is reported and left alone.

The upgrade that breaks a machine is never the one anyone was thinking about.

### [`counterexample`](skills/counterexample) — let the checker find the bug

A test checks the orderings someone thought of; a model checker checks all of
them. Models the part of a codebase where order matters — several actors racing,
a response lost after the other side acted, a fold over an event log — in
**TLA+** when actors interleave or **Lean 4** when one state machine or pure
function must hold for every input, choosing per target. A counterexample counts
only once it reproduces as a failing test in the real code; a clean run is
reported as *no counterexample up to size N*, never as *verified*.

Leaves a `specs/` directory and a script that reruns every model, trace replay
and proof, so the evidence outlives the session.

## Favourite skills

Other people's skills that earned a place in my setup. Nothing here is mine.

### [`show-me`](https://github.com/humanlayer/skills/tree/main/plugins/show-me/skills/show-me) — humanlayer

Explains with the smallest visual that does the job: pseudocode for logic, a call
tree for runtime flow, a component tree for UI, a sequence diagram for ordering.

Here because the failure it fixes is the one prose is worst at. A paragraph
describing what calls what is a diagram the reader has to draw themselves.

### [`ponytail`](https://github.com/DietrichGebert/ponytail) — DietrichGebert

Makes the agent think like the laziest senior developer in the room: stop at the
first rung that holds, and prefer the code you never wrote.

Here for the premise, not the numbers. An independent benchmark measured roughly
a quarter to a half of the advertised savings — about −15% code and −10% cost
against an advertised −54% and −20%. A real effect, smaller than the README says.

### [`caveman`](https://github.com/JuliusBrussee/caveman) — JuliusBrussee

Strips articles, filler and hedging from replies while keeping code, commands and
exact error text intact. Several compression levels, the deepest barely English.

Here as the honest extreme of something [`comment-diet`](skills/comment-diet)
does carefully. Worth knowing that its own rules cost 1–1.5k input tokens every
turn, so whole-session savings land well under the advertised 65%.

### [`wayfinder`](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder) — mattpocock

Plans work too large for one session as a map issue on the real tracker, with
child decision tickets resolved one at a time.

Here because of where it puts the state. The plan is not a scratch file the agent
keeps to itself — it is an issue the team can read, and it outlives the session
that made it.

### [`andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills) — Forrest Chang

Four rules derived from Karpathy's January 2026 notes on where agent coding goes
wrong: think before coding, simplicity first, surgical changes, verifiable goals.

Here because "surgical changes" is the rule an agent breaks most often and the
one hardest to notice being broken. Karpathy has not endorsed it.

### [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — Anthropic

Anthropic's own skill for writing skills, alongside the spec and a template.

Here because it is the reference for the format everything in this repository is
written in, and it settles questions about frontmatter that guessing does not.

### [`asd-ste100`](https://github.com/danyuchn/asd-ste100-skill) — danyuchn

Rewrites dense English into Simplified Technical English for a reader that cannot
ask what you meant: an agent parsing a tool description, an error string or an
inter-agent instruction.

Here as the complement to [`technical-english`](skills/technical-english), not a
replacement. Mine is a style applied to everything written from invocation
onwards; this one is a transform that takes text and returns a rewrite. It also
splits its rules into the ones checkable without ASD's dictionary and the ones
that are only a direction of travel, which is a more useful admission than simply
naming the limitation.

## Design notes

The first three are language- and framework-agnostic on purpose. Nothing in
them names a version, a toolchain or a vendor, so none needs revisiting when
those change. `branch-pruner` is git-specific by nature — the domain is the
version control system — but sticks to portable git commands and pins no
versions, clients or hosts. `uber-updater` sits furthest from that ideal by
necessity, since its subject *is* whichever managers a machine happens to have.
It answers by naming categories rather than products — a system manager, a
language's global installs, a version manager — and by describing classes of
failure rather than the packages that exhibited them, so it stays true on a
machine sharing none of the tools that taught it. `counterexample` names its two
formalisms because they are its method, not its subject; everything it says
about the code under test is phrased as runtime semantics — an event loop,
a lock, a transaction — rather than as any one framework.

They are also written to fail quietly rather than loudly: an empty result is a
valid answer, and each says so explicitly. A skill that must find something will
invent something.

## Licence

MIT
