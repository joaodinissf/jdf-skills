# uber-updater

*Find every manager; change nothing without a yes.*

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

## Install

```sh
npx skills add joaodinissf/jdf-skills -s uber-updater
```
