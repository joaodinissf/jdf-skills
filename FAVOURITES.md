# Favourite skills

Other people's skills that earned a place in my setup. Nothing here is mine.

## show-me

**humanlayer** · [source](https://github.com/humanlayer/skills/tree/main/plugins/show-me/skills/show-me)

Explains with the smallest visual that does the job: pseudocode for logic, a call
tree for runtime flow, a component tree for UI, a sequence diagram for ordering.

Here because the failure it fixes is the one prose is worst at. A paragraph
describing what calls what is a diagram the reader has to draw themselves.

## ponytail

**DietrichGebert** · [source](https://github.com/DietrichGebert/ponytail)

Makes the agent think like the laziest senior developer in the room: stop at the
first rung that holds, and prefer the code you never wrote.

Here for the premise, not the numbers. An independent benchmark measured roughly
a quarter to a half of the advertised savings — about −15% code and −10% cost
against an advertised −54% and −20%. A real effect, smaller than the README says.

## caveman

**JuliusBrussee** · [source](https://github.com/JuliusBrussee/caveman)

Strips articles, filler and hedging from replies while keeping code, commands and
exact error text intact. Several compression levels, the deepest barely English.

Here as the honest extreme of something [`comment-diet`](skills/comment-diet)
does carefully. Worth knowing that its own rules cost 1–1.5k input tokens every
turn, so whole-session savings land well under the advertised 65%.

## wayfinder

**mattpocock** · [source](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder)

Plans work too large for one session as a map issue on the real tracker, with
child decision tickets resolved one at a time.

Here because of where it puts the state. The plan is not a scratch file the agent
keeps to itself — it is an issue the team can read, and it outlives the session
that made it.

## andrej-karpathy-skills

**Forrest Chang** · [source](https://github.com/multica-ai/andrej-karpathy-skills)

Four rules derived from Karpathy's January 2026 notes on where agent coding goes
wrong: think before coding, simplicity first, surgical changes, verifiable goals.

Here because "surgical changes" is the rule an agent breaks most often and the
one hardest to notice being broken. Karpathy has not endorsed it.

## skill-creator

**Anthropic** · [source](https://github.com/anthropics/skills/tree/main/skills/skill-creator)

Anthropic's own skill for writing skills, alongside the spec and a template.

Here because it is the reference for the format everything in this repository is
written in, and it settles questions about frontmatter that guessing does not.

## asd-ste100

**danyuchn** · [source](https://github.com/danyuchn/asd-ste100-skill)

Rewrites dense English into Simplified Technical English for a reader that cannot
ask what you meant: an agent parsing a tool description, an error string or an
inter-agent instruction.

Here as the complement to [`technical-english`](skills/technical-english), not a
replacement. Mine is a style applied to everything written from invocation
onwards; this one is a transform that takes text and returns a rewrite. It also
splits its rules into the ones checkable without ASD's dictionary and the ones
that are only a direction of travel, which is a more useful admission than simply
naming the limitation.

## impeccable

**Paul Bakaus** · [source](https://github.com/pbakaus/impeccable)

Gives the agent a vocabulary for frontend design: critique the hierarchy, distill
a crowded page, polish the details. Builds on Anthropic's frontend-design skill
with guidance on typography, colour, layout, motion and interaction, plus checks
for recurring design anti-patterns.

One skill, with focused commands. `audit` reports technical issues in
accessibility, performance, theming and responsive behaviour; `critique` reviews
visual hierarchy, clarity and usability, with priorities for what to improve.
`distill` removes clutter, `clarify` improves UI copy, `typeset` refines typography,
and `polish` finishes an existing interface within its design system.

Here because “make it look better” leaves the agent guessing. A named design
problem is easier to fix than a request to make something prettier.

After [installation](https://impeccable.style/docs/), run `/impeccable init` in
agent chat to capture project context. Then name the page or component:

```text
/impeccable audit the checkout form
/impeccable critique the checkout form
/impeccable polish the checkout form
```

Use `audit` or `critique` to review, then `polish` to make refinements. In Codex,
use `$impeccable` in place of `/impeccable`.

## code-simplification

**addyosmani** · [source](https://github.com/addyosmani/agent-skills/tree/main/skills/code-simplification)

Simplifies working code without changing what it does. Before anything is removed,
it asks why that thing exists (Chesterton's Fence). It then looks for concrete
patterns: a wrapper that adds nothing, a strategy pattern with one strategy, dead
code.

Here because it names the opposite failure too. Inlining a helper that gave a
concept its name, or merging two simple functions into one complex one, is not
simpler. It also keeps refactoring out of feature changes: one of each is two
changes.

## code-review-and-quality

**addyosmani** · [source](https://github.com/addyosmani/agent-skills/tree/main/skills/code-review-and-quality)

Reviews a change on five axes: correctness, readability, architecture, security
and performance. Proposes a named restructuring for each structural problem it
finds, not only the problem.

Here for one question: does this refactor reduce complexity, or only move it?
Count the concepts a reader must hold; if the "cleaner" version leaves that number
the same, it is not cleaner. It prefers deleting an abstraction to polishing one,
and gives four ways to split a change that is too large: stacked, by file group,
horizontal and vertical.

## yagni-principle

**kayaman** · [source](https://github.com/kayaman/skills/tree/main/yagni-principle)

Asks of each piece whether it answers a need that exists now or one that someone
foresees. A configuration option nobody sets, an interface with one
implementation, a marker no caller reads.

Here for cut-or-defer decisions. It separates code that is easy to extend, which
is good structure, from code that is already extended, which is speculation. Its
test is simple: if adding the piece later costs little more than adding it now,
wait.
