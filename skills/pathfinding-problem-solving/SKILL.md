---
name: pathfinding-problem-solving
description: Bidirectional search over statements — grow a forward frontier from what is established and a backward frontier from the goal by asking "what, if true, would suffice?", recursively to a depth cap, until the frontiers meet; then verify the chain link by link. Use for any problem where the target is a claim, design, or outcome and the route is unknown — proofs, research programmes, engineering goals, debugging, strategy. Triggers: "pathfinding", "what would need to be true", "work backwards from the goal", "meet in the middle", "bidirectional search".
---

# Pathfinding problem solving (bidirectional best-first search)

*Search from both ends; trust only a chain checked link by link.*

Use this when the route to the goal is unknown — when it is not yet clear
whether the goal can be reached at all, or from what. When the route is known
and only its details are not, use `recursive-planner` instead; a verified
chain from this skill is a good high-level plan for it.

The problem is a graph whose nodes are statements. An edge X → Y means
"if Y holds then X follows" (Y is a sufficient condition for X). The goal
is a path from something you already have to the thing you want.

## Two frontiers

- **HAVE (forward frontier).** Everything established: axioms, proved
  theorems, verified facts, data, working code, and their cheap
  consequences. Grows by forward chaining: combine two haves into a new
  have, preferring combinations aimed at the current backward leaves.
- **NEED (backward frontier).** Starts at the goal. Grows by backward
  chaining: for a node X, ask *"what, if it existed or were true, would
  make X reachable?"* and record each answer Y as a child, with the
  reason Y ⇒ X and an estimate of how checkable Y is. Depth is capped
  (default 10). A node whose sufficient conditions are all already in
  HAVE is a **connection**.

The two frontiers connect when a NEED leaf matches, or is implied by,
something in HAVE. The chain goal ← Y₁ ← Y₂ ← … ← (have) is the
solution outline. Nothing is a solution until every link is verified.

## Node record

Every node, in both frontiers, carries:

| field | meaning |
|---|---|
| `id`, `side` (have/need), `depth` | bookkeeping |
| `statement` | precise, self-contained, no pronouns |
| `parent`, `why_sufficient` | for NEED: the argument that this node implies its parent; for HAVE: the source or the two parents it was derived from |
| `checkable` | how one would verify this node on its own (script, citation, computation, experiment), and the cost |
| `plausibility` 0–1 | expander's honest estimate that the node is true |
| `score` | heuristic for expansion order: plausibility × checkability × (1 / (1 + depth)); best-first picks the highest |
| `status` | OPEN, EXPANDED, CONNECTED, DEAD (shown false or circular) |

## The loop

1. **Seed.** Write HAVE from the established base. Write the goal as the
   NEED root. If the goal has a positive and a negative form (prove /
   refute), seed both roots; they share HAVE.
2. **Backward expand.** Pick the K best OPEN NEED nodes. For each,
   generate 2–3 sufficient conditions. Reject any that merely restate the
   parent, that are known false, or that are circular (a descendant of
   the node being expanded). Mark a child CONNECTED if it is already in
   HAVE.
3. **Forward expand.** Derive a few new HAVE nodes by combining existing
   ones, aimed at the current NEED leaves (directed, not exhaustive).
4. **Connect.** Compare every new NEED leaf against HAVE (exact match or
   an implication with a stated reason). For each candidate chain, run a
   **verifier** that checks every link independently; a chain with a
   broken link is not a solution, the broken node becomes DEAD or gets
   re-expanded.
5. **Prune.** Drop DEAD nodes; cap the frontier size; keep best-first.
6. **Stop** on a verified chain, on the depth cap for every branch, or on
   budget. Report the verified chains, the deepest live branches, and the
   nodes that died with the reason.

## Rules that keep it honest

- Depth is not progress. Ten levels of plausible "would suffice" can end
  in a node no easier than the goal. The verifier's job is also to flag
  when a NEED node is *harder* than its parent.
- Sufficient conditions must be *strictly easier or different in kind*
  from the parent (a lemma, a computation, a structural fact), never a
  rephrasing.
- A connection is only real when the HAVE node is itself established
  (cite the source) and the implication chain is verified link by link.
- Keep the two frontiers in files, not in one agent's head: the graph is
  the artefact. Every iteration appends; nothing is deleted without a
  recorded reason.
- Record what died. Dead branches are the second most valuable output.

## As a multi-agent workflow

Seed with 2 agents (HAVE, NEED). Loop: K backward expanders in
parallel, 2–3 forward derivers, 1 connector, 1 verifier per candidate
chain, 1 pruner/scorer (plain code where possible). Frontiers live in
JSON; one agent per iteration owns the write. Stop on a verified chain,
depth cap, or budget.
