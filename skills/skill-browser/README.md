# skill-browser

*Skills on request, not by surprise.*

The one skill your agents discover. Everything else lives in a library they do
not load on their own. Ask an agent to consult your skills: it lists names and
one-line descriptions from the library, and loads only the skill you pick. A
loaded skill's relative paths resolve against its own folder, and its
`allowed-tools` limits are kept even though the client does not enforce them.

The library is `library/` next to this skill. Each skill there has its
`SKILL.md` renamed to `SKILL.dormant.md`, so that no client discovers it,
however deep it searches. A sync tool fills the library from git repositories
and records the sources in `manifest.txt`.

## Install

Link this folder into each agent's skills folder. Link nothing else.
