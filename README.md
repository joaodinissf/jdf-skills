# jdf-skills

Agent skills for keeping a codebase honest.

Both skills here go after the same failure from opposite sides: something that
reads as true and is not. One looks for it in code, the other in prose.

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

## Design notes

Both skills are language- and framework-agnostic on purpose. Nothing in either
names a version, a toolchain or a vendor, so neither needs revisiting when those
change.

Both are also written to fail quietly rather than loudly: an empty result is a
valid answer, and both say so explicitly. A skill that must find something will
invent something.

## Licence

MIT
