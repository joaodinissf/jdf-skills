# Determinism

Rendering calls `seek(t)` once per frame, or several times per frame with
motion blur. It calls in order for a video and in any order for `check` and
`sheet`. The picture must depend on `t` alone.

## The page contract

| Name | Meaning |
|---|---|
| `#stage` | The frame. Its box sets the output size; give it an explicit width and height. Without it the viewport is the frame (`--size WxH`, default 1920×1080). |
| `window.DURATION` | Length in seconds. Absent or 0 means a still. |
| `window.seek(t)` | Draw the moment `t` seconds in. It may be `async`; the renderer waits for it. |
| `window.READY` | Optional promise the renderer awaits before the first frame: set it when setup loads or decodes anything asynchronously. |
| `?render` | Present in the URL while rendering. The page must not start its own playback loop. |

`seek` must not keep state between calls. Write "position at `t`", not "move
a little from last time". Where a simulation truly needs history, such as
particles or physics, precompute it at setup into an array indexed by frame,
and have `seek` read from that array.

## What the renderer controls

Before any page script runs, `render.py` installs:

- **A clock.** `Date`, `Date.now()` and `performance.now()` return the
  frame's time, plus a fixed epoch for dates.
- **A frame queue.** `requestAnimationFrame` callbacks are held, then called
  with the frame's time after each `seek`, up to four rounds. A loop that
  redraws itself from its timestamp therefore draws the right frame.
- **Random numbers.** `Math.random` is seeded from the frame time. A frame
  gets the same values each time it is drawn, and different frames get
  different ones. At setup, before any `seek`, the sequence is fixed too.
- **CSS and Web Animations.** Every `document.getAnimations()` entry is
  paused and set to the frame's time, so CSS `@keyframes` and
  `element.animate()` follow `t`.
- **SMIL.** Each top-level `<svg>` is paused and set with `setCurrentTime(t)`.

This is a safety net, not a licence. Deriving everything explicitly from
`t` in `seek` stays the clearest design.

## Libraries

Drive a library's own timeline from `seek`. Never let it play.

| Library | In setup | In `seek(t)` |
|---|---|---|
| GSAP | `const tl = gsap.timeline({ paused: true })` | `tl.totalTime(t)` |
| anime.js | `const a = anime({ ..., autoplay: false })` | `a.seek(t * 1000)` |
| Lottie | `lottie.loadAnimation({ ..., autoplay: false })` | `anim.goToAndStop(t * 1000, false)` |
| three.js | `new WebGLRenderer({ preserveDrawingBuffer: true })`, and no `setAnimationLoop` | update the scene from `t`, then `renderer.render(scene, camera)` |
| Canvas 2D | — | clear, then draw everything from `t` |
| D3 | build scales and data joins | set attributes from `t`; skip `transition()` |

GSAP repeats: use a finite `repeat` computed from the duration. A
`repeat: -1` has no defined length.

## Fonts

Fonts are the most common cause of a frame that differs between machines, or
of a first frame drawn in the wrong face.
- Embed each face with `@font-face`, as a file beside the page or as a
  `data:` URL. The renderer loads every declared face before the first frame.
- A font named in CSS that is neither declared nor installed makes
  `check` fail, because text is being drawn in a fallback.
- System fonts (`system-ui`, `ui-sans-serif`) are acceptable for drafts.
  They differ between operating systems, so embed a face for anything
  delivered.

## Images, video and screenshots

- `<img>` elements in the markup load before the first frame, because the
  renderer waits for the page's load event. Anything loaded from script
  (`new Image()`, `fetch`, a decoder) must be awaited through
  `window.READY = (async () => { ... })()`.
- Web fonts, images and scripts fetched from the network make a render depend
  on the network, and `check` warns about them. Download them beside the
  page.
- **Footage:** seeking a `<video>` element is not frame-accurate in a
  headless browser. Extract the frames first:

  ```sh
  ffmpeg -i clip.mp4 -vf fps=30 clip/%05d.jpg
  ```

  In `seek`, show `clip/${String(Math.floor(t * 30) + 1).padStart(5, '0')}.jpg`.
  Preload them in `window.READY`: create `Image` objects and
  `await img.decode()` on each. The other way is to render the graphics with
  `--alpha` and composite them over the footage with ffmpeg; see
  [`output.md`](output.md).

## Rendering side effects in Chrome

Chrome decides when to paint an element on its own compositing layer, and
that decision can depend on the frames drawn before. Text then antialiases
slightly differently when a frame is revisited, although `seek` is pure.
`check` reports this as a purity failure in which only text edges
differ.

The remedy is `will-change: transform, opacity` on elements whose opacity or
transform `seek` changes. It pins their layers, so the pixels no longer
depend on history. The template does this. Frames rendered in order, as
`video` renders them, are reproducible either way.

Other constraints:
- Output is sRGB, with no hinting.
- A pixel density above 1 (`--scale 2`) doubles the resolution of every
  output.
- WebGL runs on a software rasteriser unless the browser has a GPU. It is
  slower, but consistent.

## What the renderer cannot fix

- State kept between `seek` calls, such as counters or accumulating
  physics. `check` reports it as impure.
- Content from the network that changes over time.
- Work that finishes asynchronously after `seek` returns, unless `seek`
  awaits it.
- Different fonts or browser versions on another machine. For byte-identical
  output across machines, pin the browser (`--channel`, or one Playwright
  version) and embed every font.
