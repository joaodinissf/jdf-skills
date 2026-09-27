---
name: frame-by-frame
description: Make motion graphics and still images by writing them as code — an HTML, SVG or canvas page whose every frame is a pure function of time — then render them deterministically to MP4, WebM, MOV with alpha, GIF or PNG, and inspect the rendered frames before delivering. Use when asked for an animation, motion graphic, animated explainer, title sequence, logo sting, kinetic typography, animated chart, product or UI demo video, looping GIF, social clip, poster, banner, thumbnail, diagram image or any visual that code can draw. Not for photorealistic imagery an image model should generate, nor for animating a live application's UI.
---

# Frame by frame

*Decide every frame before drawing one. Look at them before calling it done.*

A capable agent can write striking motion as code. What separates a result
worth shipping from a plausible one is rarely the code. It is deciding the
states and timing before building, and looking at the rendered frames
afterwards, because code that runs says nothing about what a viewer sees.

The method has one rule that everything else rests on: **every frame is a
function of time alone.** A page exposes `seek(t)`; given `t` in seconds it
draws that moment, in any order, as often as asked. Then a frame can be
rendered, inspected, compared and fixed independently, and the video is
the same on every run.

## Scope

In scope: anything a browser can draw. That includes typography, shapes,
charts, diagrams, SVG illustration, canvas and WebGL scenes, and interface
mock-ups for product demos. Screenshots, footage and images can be
composited in as assets. That includes a demo of a real desktop application
composed from its screenshots, as described in
[`references/product-demos.md`](references/product-demos.md). Still images
are the degenerate case: one frame at one `t`.

Say so plainly, and do not force the method, when:

- the request is for photorealistic imagery or a likeness, which an image or
  video model produces and code does not;
- the request is to animate a live application's UI. That is interaction
  design in the product's own code, not a rendered artefact;
- the deliverable depends on sound design. Audio can be muxed into the output,
  but this method does not compose or time it.

## 1. Write the brief

Before code, write a brief of a few lines. Show it to the user when the
request is open to interpretation; otherwise record it and proceed.

- **Message:** the one thing a viewer should take away. If it takes two
  sentences, it is two pieces.
- **Frame:** width × height and where it will be seen (see
  [`references/output.md`](references/output.md) for common sizes and safe
  areas); duration; fps; format; loop, hold or end.
- **Fixed content:** exact words, numbers, names and logos, each marked with
  its source. Kept apart are measured figures, targets, and illustrative
  values, which must be labelled on screen as illustrative. Never invent a
  statistic, quote, price or date. Never redraw a real logo from memory;
  ask for the file.
- **Beats:** a table of times and states, which is the storyboard:

  | t (s) | on screen | what changes |
  |---|---|---|
  | 0.0 | empty ground | — |
  | 0.3–1.1 | headline | words rise in, staggered |
  | 1.1–4.8 | headline, rule, subline | hold; hero word drifts |
  | 4.8–5.3 | — | everything leaves, faster than it came |

- **Look:** palette as roles (ground, surface, ink, muted, accent), typeface,
  and one reference if the user has one.

Ask only for what would change the result, in one batch. That is usually
the fixed content and the frame. Everything else is a stated assumption the
user can overturn.

## 2. Build the page

Start from [`assets/template.html`](assets/template.html). It defines the
contract: `#stage` sized to the frame, `window.DURATION`, `window.seek(t)`,
a browser preview that plays in a loop, and helpers for easing, springs,
keyframe tracks and seeded randomness. Read
[`references/craft.md`](references/craft.md) before choreographing, and
[`references/determinism.md`](references/determinism.md) before bringing in
a library, canvas, WebGL, video or anything random.

1. **Lay out the most complete state statically first**, with real content,
   in normal HTML and CSS flow. If that frame does not work as a still, no
   motion will save it.
2. **Then animate towards and away from it** in `seek(t)`: compute each
   property from `t` and set it. No CSS transitions or animations running on
   their own, no timers, no state carried between calls.
3. Keep it one self-contained file where practical. Embed or place fonts
   and images beside it; nothing fetched from the network at render time.

For a still image, build the same way with `DURATION = 0`, or leave `seek`
out altogether.

## 3. Render and look

The renderer is [`scripts/render.py`](scripts/render.py). Before page
scripts run, it replaces the clock and the random-number generator with
controlled ones. Paths in the commands below are relative to this skill's
directory; call the script by its full path from the user's project.

```sh
uv run scripts/render.py check page.html --loop           # defects, as text
uv run scripts/render.py sheet page.html sheet.png --at 0.3,0.8,1.5,3,5   # frames to look at
```

**Running it.** Prefer `uv run`. The script declares its own dependency
(Playwright) inline, so `uv` provides it in an isolated environment with no
global install. Without `uv`, create a virtual environment and
`pip install playwright`. It needs a Chromium:
- `--channel chrome` uses an installed Google Chrome;
- otherwise `uv run --with playwright playwright install chromium` downloads one.

Video needs `ffmpeg` on `PATH`. Installing anything is the user's call: say
what is missing and the command, rather than installing unasked.

**`check`** samples the timeline and fails on:
- page errors, a `seek` that throws, and failed requests;
- a font that did not load, or a named font that is not available;
- a `seek` that is not pure: a frame differs when revisited;
- a timeline in which nothing moves;
- with `--loop`, a seam where `seek(DURATION)` differs from `seek(0)`.

It warns about text clipped by its box or leaving the frame, and about
network requests. Fix every error. Decide on each warning; some text leaves
the frame on purpose.

**`sheet`** writes one labelled image of chosen frames. Choose times from the
brief:
- the first frame and the last;
- each beat's settled state;
- one moment inside every transition, not only the resting states;
- for a loop, the frame just before the end.

Then **look at the sheet** and at full-size stills where detail matters
(`still --at t --scale 2`). A check that passes does not mean the frames
look right. Go through this list, most frequent first:

- something visible before its entrance or after its exit (an unclamped
  interpolation);
- text cramped against an edge, outside the safe area, or wrapping into an
  orphan;
- a fallback font, or glyphs missing;
- low contrast: small text over a busy or similar-coloured background;
- more than one thing competing to be looked at first;
- an empty or unreadable first frame, where a thumbnail or autoplay shows it;
- dead air, meaning a stretch where nothing new happens, or everything
  moving at once;
- motion that snaps: a jump between two adjacent frames. Sample two frames
  one step apart around the moment in question;
- an overlay off its target: a highlight, cursor, callout or label a few
  pixels from the thing it points at, or clipped at the frame edge. A sheet
  is too small to show it. Render each such moment at `--scale 2`, crop
  around the target and compare centres. Rectangles taken from accessibility
  frames or measured by hand are rarely the visible edges; fit them to the
  pixels first.

Fix, then run `check` and `sheet` again. Two or three rounds usually settle
it. If defects remain after that, report them rather than circling.

## 4. Render the deliverable

```sh
uv run scripts/render.py video page.html out.mp4             # H.264, for sharing
uv run scripts/render.py video page.html out.gif --fps 15    # loops in docs and chat
uv run scripts/render.py video page.html out.mov --alpha     # ProRes 4444, for compositing
uv run scripts/render.py still page.html out.png --at 3 --scale 2
```

`--blur 4` to `--blur 8` adds motion blur, with the frame sampled several
times across a half-frame shutter. It is worth using for fast movement and
not otherwise. After encoding, `video` reads the file back and fails if its
size, duration or frame count differs from the page. For formats, sizes,
GIF palettes, alpha and audio, see
[`references/output.md`](references/output.md).

## 5. Report

State what was made and what was verified, in the terms the checks
support:

- **Outputs:** each file's path, size, duration and format.
- **Checks:** which ones ran, what they found, and what was fixed.
- **Frames looked at:** which times, and anything judged but left as it is,
  with the reason.
- **Assumptions:** those the user has not confirmed, such as copy,
  illustrative data, a stand-in for a logo, or a font substitution.
- **Rerun:** the commands to render again.

Do not describe a result as polished, on-brand or accurate beyond what was
checked. "The checks pass and the sheet shows no clipping" is a finding.
"Looks great" is not.
