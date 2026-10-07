# recursive-planner

*Plan the whole route coarsely; plan only the next step in detail.*

Plans large work at two resolutions: a coarse high-level plan for the whole
route, and a detailed plan for the next step only. After each step it re-enters
plan mode, revises the high-level plan with what the step taught, and only then
details the next one. A step too big to plan concretely becomes its own
sub-plan, run by the same loop. Every pass ends in an approval.

User-invoked only: `/recursive-planner <what you want done>`.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s recursive-planner
```
