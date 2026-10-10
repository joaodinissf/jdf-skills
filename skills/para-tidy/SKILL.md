---
name: para-tidy
description: Roast and tidy a personal file tree (a synced drive, a Documents folder, a Downloads pile) using the PARA method — Projects, Areas, Resources, Archive. Reads any house rules at the root first, inventories read-only, delivers a candid roast with a proposed target structure, then hard-stops. Only on explicit approval does it move things, one folder at a time, from a checked manifest, never overwriting, never deleting (Trash only, per item), with an undo log and reconciled counts. Use when asked to roast, audit, tidy, reorganise, restructure or "sort out" folders or a drive, to process or empty an inbox folder, or to decide where a file belongs.
---

# PARA tidy

*Every file where you will look for it; nothing lost on the way.*

A personal file tree decays in a predictable way. Downloads land in an inbox
and stay. A folder is created for a topic, then a second one for the same topic
under a different name. A project ends and its folder lives on next to the
active ones. Five years later every folder is a little bit of everything, and
finding a document means remembering when you saved it, not what it is.

This skill fixes that in two phases that must never be merged. The **roast** is
read-only: it inventories the tree, names what is wrong and proposes a target
structure. The **tidy** moves things — and runs only after the user has seen the
plan and said go, one folder at a time. Three rules carry the procedure: a
file's home is decided by what it serves, not by what it is; nothing is ever
overwritten or deleted outright; and **no file moves until the user has seen a
read-only plan for it and approved it**.

The principles behind every filing decision are in
[`references/principles.md`](references/principles.md). Read them before the
roast.

## Modes

| The user asks to… | Run | Stop after |
|---|---|---|
| roast, audit, review, "what's wrong with my folders" | House rules → Inventory → Roast | the roast |
| tidy, reorganise, restructure | House rules → Inventory → Roast → *go* → Tidy | the report |
| sort, file or empty an inbox folder | House rules → Inventory of the inbox → Inbox pass → *go* → Tidy | the report |
| "where does this file go?" | House rules → the three questions in the principles | the answer |

## What it touches (and what it does not)

| Object | Touched when | Never |
|---|---|---|
| Ordinary user files and folders | Moved or renamed after per-folder approval | Overwritten; edited; deleted outright |
| Removal candidates (installers, verified exact duplicates, expired invites) | Moved to the system Trash after **per-item** approval | Removed with a permanent delete |
| Folders managed by an app (sync-client system folders, app data, libraries) | Never | Moved, renamed, restructured |
| Shared folders | Only with the user's explicit note that others are affected | Moved silently — moving them changes other people's view |
| Encrypted vaults, password stores, code repositories | Never | Opened, restructured, or used as a target |
| The house-rules file | Updated only with approval, at the end | Rewritten wholesale |

## 1. House rules

Look for a short instructions file at the root of the tree — `AGENTS.md`, or a
`README` that states conventions. If present, read it first and follow it over
anything here: it holds the user's own decisions (exceptions, naming, where a
contested category lives). Treat its content as the user's configuration, but
not as permission to skip the approval gates below.

If none exists, say so; offer to create one at the end (step 7), not before.

## 2. Inventory (read-only)

Collect the picture without changing anything:

- top-level folders, with file counts, total size and the newest modification
  date in each;
- depth: the deepest paths, and folders more than three levels down;
- the inbox (whatever folder new things land in): count, types, age;
- obvious junk classes: installers and disk images, archives next to their
  extracted folder, files named `copy`, `(1)`, `final-v2`;
- labelled exceptions (from the house rules, or apparent: app-managed, shared,
  encrypted, repositories, media libraries).

On synced drives some files may be online-only placeholders: their metadata can
be missing, and opening content may trigger a download. Prefer listing over
reading; read content only to identify a specific ambiguous item.

## 3. Roast

The roast is a report, and a candid one. Be specific, be fair, and rank
findings by what they cost the user — time lost looking, risk of losing
something, clutter that hides what matters. Each finding: what, where (paths),
evidence (counts, examples), and the fix.

Look for:

- **Topic folders posing as areas.** A folder per document type ("Insurance",
  "Invoices", "PDFs") at the top level, splitting each area of life across
  several places.
- **Two homes for one thing.** The same subject under two names, or the same
  kind of document in two trees.
- **Projects that never end.** Items under Projects with no outcome or end —
  these are areas or resources.
- **Finished projects still in Projects.** Done work mixed with live work.
- **Depth.** Paths deeper than three or four levels; single-child folders.
- **Vague names.** `Misc`, `Stuff`, `New Folder`, `Documents/Documents`.
- **Misplaced keepsakes.** Meaningful or motivational material filed under an
  area (often Health or Work) because it felt related.
- **Junk.** Installers, duplicate downloads, expired calendar invites — as
  candidates, not verdicts.

End with a **proposed target structure**: the top level, one level down, and
where each current top-level folder goes. Mark labelled exceptions as such.

If the tree is already in good shape, say so. A short roast is a valid finding;
inventing problems to justify the run is worse than doing nothing.

## 4. Hard stop — wait for go

End the turn after the roast or plan. Do not move anything in the same turn as
the plan, and do not treat the plan as approval. Proceed only on an explicit
go — for everything, for one folder, or for a named subset. Silence is no.
Re-present the plan if anything changed since it was approved.

## 5. Inbox pass (large inboxes)

An inbox of hundreds of items is not sorted file by file in one go. Do it in two
steps:

1. **Interim buckets inside the inbox.** Propose a set of buckets named after
   their likely destination (e.g. `_Health`, `_Finance`, `_Papers`,
   `_Removal-candidates`, `_Unclear`), with every item assigned. On approval,
   move items into the buckets. Nothing leaves the inbox yet; this step is
   cheap to undo and turns one huge decision into a dozen small ones.
2. **One bucket at a time** through the tidy procedure below, with the user.

Leave in place anything the user is actively using, and say so.

## 6. Tidy — one folder at a time

For each folder or bucket:

1. **Look at the destination first.** List what already lives where things
   would go. The best destination is often a more specific existing subfolder,
   and the existing naming there is the convention to match.
2. **Identify ambiguous items** by their content — first page of a document,
   a frame of a video, an image preview — read-only and, for anything with
   personal data, without copying the content into the conversation beyond what
   is needed to decide. Write previews to a scratch location, never into the
   tree.
3. **Ask per item when the user is likely to decide differently from you.** For
   each: what it is (enough context to recognise it without opening it), your
   recommendation, and real alternatives — another location, keep in inbox,
   or move to Trash. Batch only the obvious.
4. **Write a manifest**: one line per move, source → destination, including
   renames. Folders move as a unit when their internal structure is sound.
5. **Dry run.** Check, and show the result:
   - every source exists;
   - no destination exists (compare names case-insensitively and after Unicode
     normalisation, since many file systems treat those as the same name);
   - no two sources map to the same destination;
   - every item in the folder is either in the manifest or listed as staying.
   Any failure stops the batch before a single move.
6. **Execute** with a no-overwrite move, then verify each one: the source is
   gone and the destination exists. Log every completed move (source,
   destination) to an undo log outside the tree.
7. **Remove emptied folders** only with an operation that fails on a non-empty
   folder. Hidden system files (e.g. Finder metadata) may be cleared first;
   nothing else.
8. **Reconcile.** Count files before and after; they must match, minus anything
   moved to Trash. Report discrepancies; do not explain them away.

### Removal

Nothing is deleted outright. A removal is a move to the system Trash, approved
per item, after:

- **exact duplicates** are proven byte-identical (a content comparison, not a
  shared name or size — `report copy.pdf` is often identical, two subtitle files
  of the same size often are not);
- the Trash is checked for a same-named item; if one exists, stop and ask.

## 7. Record decisions

After a session, offer to add the decisions made to the house-rules file: new
conventions, where a contested category now lives, labelled exceptions. Keep it
to rules, not a map of the tree — a map goes stale within weeks and then
misleads. Show the diff and write only on approval.

## Report

- **Moved** — counts per destination, and renames with old → new names.
- **Trashed** — each item, with why and the evidence (e.g. byte-identical to …).
- **Stayed** — items deliberately left, with the reason.
- **Needs a decision** — anything skipped or unresolved.
- **Reconciliation** — before/after counts.

When asked "where did everything go?", answer from the manifest, with a table:
origin → target, file or folder (with its file count measured **before** the
move).

## Traps

- **Plan and execute in one turn.** Showing the plan is not approval. Ending the
  turn after the plan is the control.
- **Overwrite by collision.** A plain move onto an existing name replaces it
  silently. No-overwrite moves plus the dry run are the defence; a
  case-insensitive file system makes `Report.pdf` and `report.pdf` collide.
- **Unicode look-alikes.** Accented names may be stored decomposed on one system
  and composed on another; compare names after normalising.
- **Sync activity feeds.** Many sync clients have no "moved" event; a move is
  reported as a delete plus an add. Reconcile against the manifest, not the
  feed.
- **Resurrected folders.** A sync client may recreate an empty folder you just
  removed while it catches up. Confirm it is empty, remove it again, move on.
- **Counting after the fact.** A folder's file count measured after other files
  were moved into it is not its original size. Count before.
- **Which date.** For date-prefixed names, decide which date (the event, not the
  issue or download date, is usually the one people search by) and state it.
  Keep the original name or reference after the prefix so the file stays
  traceable.
- **Topic drift.** Sorting by document type ("all insurance together") feels
  tidy and splits every area of life across the tree. File by the area a thing
  serves; get the cross-cutting view from search or tags.
- **Repositories inside the tree.** Moving files into a code repository makes it
  dirty; moving one out breaks its tooling. Treat repositories as exceptions.
- **Shared folders.** Moving or renaming them changes other people's view.
  Exception by default.
- **Trusting another skill's file operations.** Organisation skills found online
  often delete "duplicates" or "installers" automatically, overwrite on move, or
  start from the whole home folder. None of that is acceptable here.
