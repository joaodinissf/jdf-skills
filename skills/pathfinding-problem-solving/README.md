# pathfinding-problem-solving

*Search from both ends; trust only a chain checked link by link.*

Finds a route to a goal when the route is unknown. It grows a forward frontier
from what is established and a backward frontier from the goal, by asking "what,
if true, would suffice?", until the two meet. A meeting is only a candidate: the
chain counts as a solution when every link has been verified on its own. Dead
branches are recorded with the reason they died.

Works for proofs, research programmes, engineering goals, debugging and
strategy, and scales to a multi-agent workflow with the frontiers kept in files.
When the route is known and only its details are not, use
[`recursive-planner`](../recursive-planner) instead.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s pathfinding-problem-solving
```

## Sources and attribution

Written from scratch. The method is old and not ours:

- bidirectional heuristic search — Ira Pohl, "Bi-directional search",
  *Machine Intelligence 6* (1971);
- means–ends analysis — the General Problem Solver of Allen Newell,
  J. C. Shaw and Herbert A. Simon (1959);
- "working backwards" as a problem-solving heuristic — George Pólya,
  *How to Solve It* (1945).
