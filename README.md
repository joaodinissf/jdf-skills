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

| Skill | What it does |
|---|---|
| [`silly-sweep`](skills/silly-sweep) | Finds code that misleads: comments, guards and tests that say something untrue. |
| [`perennial-docs`](skills/perennial-docs) | Rewrites documentation written as a record of the work that produced it. |
| [`comment-diet`](skills/comment-diet) | Cuts comments back to the ones a competent reader would miss. |
| [`technical-english`](skills/technical-english) | Writes clear, controlled technical English inspired by ASD-STE100. |
| [`branch-pruner`](skills/branch-pruner) | Brings a repository back to one checkout without losing any work. |
| [`uber-updater`](skills/uber-updater) | Finds every package manager on a machine and updates only what you approve. |
| [`system-model`](skills/system-model) | Models a system in TLA+ or Lean 4 so its assumptions can be checked. |
| [`frame-by-frame`](skills/frame-by-frame) | Makes motion graphics and images as code, then renders and looks at every frame. |
| [`paper-figures`](skills/paper-figures) | Makes paper figures as editable sources (matplotlib, draw.io, TikZ) at column width, then checks and looks at them. |
| [`recursive-planner`](skills/recursive-planner) | Plans the next step in detail and the rest coarsely, re-planning after every step. |
| [`para-tidy`](skills/para-tidy) | Roasts a file tree, then tidies it with PARA one approved folder at a time, never overwriting or deleting. |

## Favourite skills

Other people's skills that earned a place in my setup. Nothing here is mine.
Why each one is here: [FAVOURITES.md](FAVOURITES.md).

| Skill | Author | What it does |
|---|---|---|
| [`show-me`](FAVOURITES.md#show-me) | humanlayer | Explains with the smallest visual that does the job. |
| [`ponytail`](FAVOURITES.md#ponytail) | DietrichGebert | Makes the agent stop at the simplest solution that holds. |
| [`caveman`](FAVOURITES.md#caveman) | JuliusBrussee | Strips filler from replies; keeps code and error text exact. |
| [`wayfinder`](FAVOURITES.md#wayfinder) | mattpocock | Plans large work as an issue on the real tracker. |
| [`andrej-karpathy-skills`](FAVOURITES.md#andrej-karpathy-skills) | Forrest Chang | Four rules from Karpathy's notes on where agent coding goes wrong. |
| [`skill-creator`](FAVOURITES.md#skill-creator) | Anthropic | Anthropic's own skill for writing skills. |
| [`asd-ste100`](FAVOURITES.md#asd-ste100) | danyuchn | Rewrites dense English into Simplified Technical English. |
| [`impeccable`](FAVOURITES.md#impeccable) | Paul Bakaus | Gives the agent a vocabulary for frontend design. |
| [`code-simplification`](FAVOURITES.md#code-simplification) | addyosmani | Simplifies working code, checking why each piece exists first. |
| [`code-review-and-quality`](FAVOURITES.md#code-review-and-quality) | addyosmani | Asks whether a refactor reduces complexity or only moves it. |
| [`yagni-principle`](FAVOURITES.md#yagni-principle) | kayaman | Asks whether each piece is needed now or built speculatively. |

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
machine sharing none of the tools that taught it. `system-model` names its two
formalisms because they are its method, not its subject; everything it says
about the system under study is phrased as behaviour — a state transition,
a lock, a transaction — rather than as any one framework. `frame-by-frame`
names a browser and ffmpeg because rendering is its method; it asks for no
animation library, and every duration it recommends is in seconds, so it
survives a change of frame rate as well as of tools.

They are also written to fail quietly rather than loudly: an empty result is a
valid answer, and each says so explicitly. A skill that must find something will
invent something.

## Licence

MIT
