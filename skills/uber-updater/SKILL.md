---
name: uber-updater
description: Find every package manager on a machine, collect what each one reports as out of date, and update only what the user approved — behind two hard stops, one to choose the scope and one to confirm the exact commands. Tiers the work by blast radius (packages and command-line tools, graphical applications, language toolchains) because those fail differently and deserve separate answers. Reports state no update can fix — shadowed managers, orphaned installs, packages that need removing rather than upgrading — without touching it. Use when asked to update everything, to check what is outdated, to bring a machine current, or after a partial upgrade has left something broken.
---

# Uber updater

*Find every manager; change nothing without a yes.*

A working machine accumulates package managers the way a house accumulates keys.
The system one, the language ones, the version managers, and the several that
arrived as a dependency of something else. Each has its own verb for *what is
old* and its own verb for *make it new*, and nobody remembers all of them. The
practical result is a machine updated unevenly: whatever the user thinks of gets
updated often, and everything else silently rots.

The reflex fix — a shell alias chaining every update command with `&&` — fails
for a reason worth naming up front: **the upgrade that breaks a machine is never
the one being thought about.** It is a runtime moving a major version under
configuration that hardcoded the old one. Sequencing that behind `&&` means
discovering it in whatever shell opens next, with no memory of what changed.

So this skill separates *knowing* from *doing*, and never merges them. Finding
what is outdated is free and can be done in full. Changing anything requires the
user to have seen a plan and said yes — twice, once to the scope and once to the
commands.

## Four stages

| Stage | Nature | Ends with |
|---|---|---|
| 1. Detect the managers | read-only | an inventory |
| 2. Collect what is outdated | read-only | a list, per manager, per tier |
| 3. **Scope gate** | **hard stop** | the user chooses tiers or a subset |
| 4. **Command gate** | **hard stop** | the user sees exact commands and confirms |
| 5. Execute and report | writes | what changed, what failed, what was skipped |

Stages 1–2 may always run. Stages 3–4 are described below as hard stops and mean
it: ending the turn is the control. Nothing in stage 5 runs in the same turn as
the plan that proposed it.

## Stage 1 — detect by evidence, never by memory

Do not assume a manager is present because the language is, or absent because it
is unfashionable. Probe, and probe two independent ways.

**On PATH.** Resolve each candidate command and record *where* it resolved and
what version it reports. The path matters as much as the presence: two installs
of the same tool is a common state, and only the earlier one on PATH is real.

**On disk.** Managers leave home directories, caches and store directories that
outlive the binary. Check those independently. A directory with no binary is not
a manager — it is residue, and belongs in the report as such, not in the update
plan.

Cast the net across every category, not the ones that come to mind:

| Category | What to look for |
|---|---|
| System / OS | the platform's own manager, and any alternative or third-party one |
| Language runtimes | one manager per language ecosystem present, plus its global-install location |
| Version managers | tools that install *other* toolchains; they update differently from packages |
| Application managers | graphical applications installed by a manager rather than by hand |
| Vendored SDKs | large vendor toolchains that ship a private updater of their own |
| Editor / plugin ecosystems | extension and plugin systems belonging to a specific tool |
| Container / VM tooling | images and machines that update independently of the host |

### A starting checklist

Categories are what to think in; names are what to actually probe. This list is
a floor, not a ceiling — probe everything here that could plausibly exist on the
platform, then keep going. The manager worth finding is usually the one absent
from any list, which is why stage 1 probes rather than recalls.

| Ecosystem | Probe for |
|---|---|
| System (macOS) | `brew`, `port`, `nix`, `mas` |
| System (Linux) | `apt`, `dnf`, `yum`, `pacman`, `zypper`, `apk`, `nix`, `snap`, `flatpak` |
| System (Windows) | `winget`, `choco`, `scoop` |
| JavaScript | `npm`, `pnpm`, `yarn`, `bun`, `deno`, `corepack` |
| Python | `pip`, `pipx`, `uv`, `conda`, `mamba`, `poetry`, `pdm`, `hatch`, `rye` |
| Rust | `cargo` (outdated needs `cargo-update`), `rustup` |
| Go | `go install` targets (outdated needs a helper such as `gup`) |
| Ruby | `gem`, `bundler` |
| JVM | `mvn`, `gradle`, `sbt`, `sdk` (SDKMAN), `cs` (Coursier), `jbang` |
| PHP · Perl · Lua | `composer`; `cpan`, `cpanm`; `luarocks` |
| Haskell | `ghcup`, `cabal`, `stack` |
| BEAM | `mix`/hex, `rebar3` |
| .NET · Swift | `dotnet tool`; `swift package`, `mint` |
| Other languages | `opam`, `nimble`, `pub`, `julia` (Pkg), `R` (install.packages) |
| Version managers | `mise`, `asdf`, `nvm`, `fnm`, `volta`, `rbenv`, `pyenv`, `nodenv`, `jenv`, `tfenv` |
| Tool ecosystems | `gh extension`, `kubectl krew`, `helm`, editor/plugin managers |
| Vendor SDKs | cloud CLIs with private component updaters (`gcloud`, `aws`, `az`) |
| Containers | `docker`, `podman` — images update independently of the host |

Two entries in that table carry a warning worth repeating: `cargo` and `go`
install binaries but ship **no built-in way to ask what is outdated**. Either
use the ecosystem's helper or report the installed set without a comparison —
never report them as clean, which is what a naive sweep does.

Then record **PATH order itself**. It is the evidence for every shadowing
question later, and it cannot be reconstructed afterwards.

Absence is a finding. A machine with three managers is a valid answer and a
short report; inventing a fourth to look thorough is worse than saying three.

## Stage 2 — collect what is outdated

Ask every detected manager what it considers out of date. Six rules make the
answers trustworthy:

**Ask for global scope explicitly.** Most language managers answer about the
*current directory* when it contains a manifest, and about globally installed
packages only when told to. Run from a neutral directory and pass the global
flag. Otherwise a project's dependencies get reported — and worse, updated — as
though they were the machine's.

**Some managers have no concept of "outdated".** Several install from a source
that carries no version index, so nothing can be compared. Say that plainly and
list what is installed instead. Do not fabricate a comparison, and do not quietly
omit the manager because it did not fit the table.

**A query that errors is not a query that returned zero.** Misconfiguration
makes managers fail loudly — a global directory missing from PATH, an absent
credential, an unreachable index. Record it as *could not determine*, which is a
finding, and never as *nothing to do*, which is a lie the user will act on.

**One manager's failure must not abort the sweep.** Collect independently and
keep going. A chained command that dies on the third of eleven managers reports
eight as clean when they were never asked.

**Deprecated is not outdated.** A package whose upstream is dead is at its final
version, so it is *current* and will never appear in an outdated list. It still
needs action — removal, or migration to a replacement — and that action is a
deletion, not an upgrade. Query it separately if the manager can report it, and
report it under its own heading so it is never silently swept into an "update
all".

**Respect holds.** Managers let a user pin, hold or freeze a package precisely so
that bulk updates skip it. Read that list before planning and exclude what it
names. A pin is a decision someone already made; overriding it silently discards
that decision.

## Three tiers, because they fail differently

Group everything collected into three tiers. The grouping is the point: it lets
a user accept the boring 90% and think about the rest.

| Tier | What it holds | How it fails |
|---|---|---|
| **1 — packages & tools** | libraries, command-line programs, plugins | a tool changes flags or output; annoying, reversible |
| **2 — applications** | graphical applications managed by a manager | a running application is quit and replaced mid-session; unsaved work is at risk |
| **3 — toolchains** | compilers, interpreters, runtimes, and the managers that install them | *everything built against them* changes at once; breakage appears later, elsewhere |

Tier 3 deserves its separation. A runtime moving a major version is the single
most common cause of a machine that worked yesterday and does not today, and the
damage never shows up where the change was made — it shows up in whatever
configuration, script or shell profile referenced the old version. Present tier 3
so a user can decline it alone.

## Stage 3 — the scope gate (hard stop)

Present the full picture: each tier, each manager, counts and specific versions,
plus what could not be determined and why. Then **end the turn.**

Offer real granularity — everything, a tier, a single manager, or a named subset.
"All or nothing" is not a choice; it pushes users into accepting tier 3 to get
tier 1.

Silence is no. A presented plan is not an approved plan. Partial approval is
normal and is acted on exactly as given: approving one tier is not a hint that
the others are welcome.

Call out inside the plan, before the gate, anything that is not a plain upgrade:

- major-version jumps, which change behaviour rather than fix bugs;
- anything in tier 2 that is **currently running**;
- deprecated packages, which need removal rather than upgrade;
- upgrades that would create a **split-brain**: installing a package through one
  manager when a different manager owns that runtime. The two disagree
  immediately afterwards, and the loser is whichever one the user next invokes.
  Propose these individually with the conflict named; never fold them into a
  bulk action.

## Stage 4 — the command gate (hard stop)

Approval of *scope* is not approval of *commands*. Show the exact command list
that will run, in order, for the approved scope only. Then **end the turn again.**

This second stop is not ceremony. Between the two gates the scope was narrowed,
and this is where a user sees that a chosen tier expands to something they did
not picture — a flag that removes as well as upgrades, a manager that upgrades
itself along the way. It is also the last point at which the whole thing can be
called off cheaply.

Never widen what was approved. If executing reveals extra work — a dependency
that must move first, a second manager holding the same package — stop and
return to stage 3 with it. Discovering more work is not permission to do more
work.

**Never elevate privileges to satisfy a user-space manager.** A permission error
from a manager that installs into a user's own directory means something is
structurally wrong — usually that the target is owned by a *different* manager.
Elevating privileges converts a clean refusal into files the owning manager can
no longer manage, and the next legitimate operation either fails or silently
discards them. Diagnose the ownership instead, and report it.

## Stage 5 — execute, tier by tier

Run one tier at a time and report after each. A tier that fails does not block
the next; the user chose them separately and deserves them reported separately.

Expect partial success and treat it as normal rather than as an error to hide.
Bulk update commands frequently update many packages and then stop at one they
cannot handle. **The remainder is the finding.** Report how many moved, how many
did not, and why — never round a partial result up to success.

When something fails, diagnose the cause before offering a fix, and prefer the
narrowest fix that addresses it. These classes recur across every ecosystem:

- **The manager does not own the target.** Something else placed a file where the
  manager expects to write. Refusing is correct behaviour, not a bug; the fix is
  to identify what put it there.
- **The registry disagrees with the filesystem.** A package was removed by hand
  while the manager still lists it as installed. Upgrades may partially execute
  before failing on the missing pieces. The fix is to reconcile the registration,
  which is a separate decision from upgrading.
- **The binary cannot self-update.** Some builds are compiled without an
  updater, or are installed by a manager that reserves that job. Retrying the
  self-update never succeeds; route the update to whichever manager owns it.
- **The source no longer exists.** A package installed from a repository or a
  local path that has since disappeared can never be updated. Report it as
  unmanageable and stop attempting it.
- **The write lands inside another manager's read-only area.** Managers commonly
  keep installed artefacts read-only on purpose. Report the ownership; do not
  force the write.

After any tier 3 change, **verify in a newly started shell.** Toolchain upgrades
break configuration that referenced the previous version, and the current shell
has that configuration already loaded, so it cannot show the damage. A new shell
is the only honest test.

## Needs attention — report, never fix

Some findings are not updates and must never be folded into one. Collect them in
their own section, describe each precisely enough to act on, and **change none of
them.** They are decisions with context the skill does not have.

- **Shadowed installs** — the same tool present twice, only one reachable. Say
  which wins and by what PATH position.
- **Unreachable installs** — a manager whose global directory is not on PATH, so
  everything it installs is invisible.
- **Idle managers** — installed, managing nothing, while another manager does
  that job. Often a migration someone abandoned halfway.
- **Residue** — home or cache directories belonging to uninstalled tools.
- **Orphans** — installed packages whose upstream source is gone.
- **Duplicate toolchains** — two installs of the same version under different
  names. Usually deliberate; always worth surfacing.
- **Deprecated packages** — need replacing or removing. Include the upstream
  end-of-life date when the manager reports one: it separates *act today* from
  *act this year*, and treating those alike either panics the user or lets a
  real deadline pass.
- **Path anomalies** — duplicated entries, or an ordering that makes a manager's
  output misleading.

Suggest a fix for each in words. Do not execute one. Mixing removals into an
update run is how an update run deletes something.

## Report

- **Updated** — per tier, per manager, with versions moved.
- **Failed** — with the diagnosed class, not just the error text.
- **Skipped** — what was not approved, and what was deliberately held back
  (a conflicting upgrade, a pinned package), so nothing looks forgotten.
- **Could not determine** — managers whose query failed, and why.
- **Needs attention** — the section above.

If everything is current, say so and stop. A machine with nothing to update is a
valid and useful answer.

## Traps

- **Deprecated masquerading as current.** A dead package reports no update
  because none exists. Bulk updaters therefore report it as fine forever, and it
  is the one package guaranteed to need action.
- **Errors read as zero.** A failed query and an empty result look identical
  once summarised into a count. Keep them distinct at every step; conflating
  them tells the user a manager is clean when it was never successfully asked.
- **Project scope read as global.** Running a global query inside a project
  directory answers about the project. The plan then proposes upgrading a
  codebase's dependencies as machine maintenance.
- **The chained `&&`.** One failure aborts the rest, and the untouched managers
  are reported as having nothing to do.
- **Self-update inside the sweep.** A manager that upgrades itself mid-run can
  change its own command-line interface, so later steps in the same run break.
  Update a manager as its own approved step.
- **Split-brain installs.** Installing a package through a manager when another
  manager owns that runtime. Both then claim the same name and the answer
  depends on PATH order — the hardest class of bug to see, because both are
  "installed correctly".
- **Elevated privileges as a shortcut.** Turns a safe refusal into an unmanageable
  state, and the artefacts are discarded by the owning manager's next upgrade
  regardless.
- **Toolchain bumps verified in the current shell.** The shell already loaded the
  old configuration and will keep working. The breakage waits for the next one.
- **Silent scope creep.** Finding extra work mid-execution and doing it. Both
  gates exist to make scope explicit; widening after them discards the consent
  they collected.
- **Applications updated while running.** Tier 2 quits and replaces a running
  application. Unsaved work is lost, and the user was mid-sentence in it.
- **The manager nobody remembers.** The one installed as a dependency of
  something else years ago is the one furthest out of date, and the one an
  update habit built on memory will never reach. It is the reason stage 1 probes
  rather than recalls.
- **A query that succeeds while answering a different question.** Stage 2 warns
  that an error is not a zero; this is the subtler cousin, and it is worse
  because nothing looks wrong. Ask a manager about a setting under the wrong
  name and most will answer *unset* rather than *no such setting* — so a
  protection that is present gets reported as missing, and the fix that follows
  changes nothing or undoes something. Confirm names against the tool's own
  documentation before concluding anything is absent, and prefer a check whose
  result would visibly differ if the setting really were missing.
- **Measuring the environment from inside a polluted one.** Any claim about
  `PATH`, environment variables or shell configuration must be made from a
  clean shell. A process that inherits an already-populated environment and
  then re-applies the user's config will observe duplicates and orderings that
  the user's real shell never produces. Reporting those invents work; acting on
  them deletes configuration that was doing its job.
