# Craft

Defaults, not laws. Each one says what it is for, so that it can be broken
deliberately. Every duration is in seconds, never in frames: frame counts
silently double in speed when the frame rate changes.

## Easing

| Movement | Curve | `cubic-bezier` | Template |
|---|---|---|---|
| Arriving, entering | fast start, long settle | `0.16, 1, 0.3, 1` | `ease.out` |
| Moving between two places on screen | slow, fast, slow | `0.83, 0, 0.17, 1` | `ease.inOut` |
| Leaving | slow start, fast finish | `0.7, 0, 0.84, 0` | `ease.in` |
| Opacity crossfade, constant drift, a clock hand | none | linear | `ease.linear` |

Linear motion on position or scale reads as mechanical. Keep it for opacity,
for continuous drift, and for things that are mechanical on purpose.

Clamp every interpolation at both ends. An unclamped value keeps moving
before its start and after its end, and the element appears where it
should not. The template's `at(t, start, dur, ease)` clamps; so does `track`.

**Springs** (`spring(t, start, w, z)` in the template) are closed-form, so any
`t` can be asked directly:

| Feel | ω (rad/s) | ζ | Settles in about |
|---|---|---|---|
| Crisp UI pop, a word | 18–22 | 0.75–0.85 | 0.25 s |
| General entrance | 13–16 | 0.8 | 0.35 s |
| Large element, a camera | 7–10 | 0.95–1 | 0.5–0.6 s |
| Playful accent, used once | 16 | 0.5–0.6 | visible overshoot |

Settling time ≈ 4 / (ζ·ω). ζ = 1 never overshoots; below about 0.7 it
bounces, which is a stylistic choice, not a default.

Scale is perceived as a ratio, so a zoom from 1× to 8× that is linear in
scale seems to slow down. Interpolate the logarithm, as in
`Math.exp(lerp(Math.log(a), Math.log(b), p))`.

## Durations

| Moment | Typical |
|---|---|
| Small element entering (a word, an icon) | 0.25–0.45 s |
| Panel, card or chart entering | 0.4–0.7 s |
| Full-frame move or scene change | 0.6–1.2 s |
| Exit | about 0.6–0.75 of the matching entrance |
| Stagger between siblings | 0.04–0.1 s; the whole cascade under about 0.6 s |
| Hold on a finished state to be read | ≥ 1 s, plus about 0.3 s per word of new text |

Rendered motion wants longer holds than interface motion. A viewer cannot
pause, scroll back or hover. They have to read it at the speed it plays.

## Choreography

- **One focal point at a time.** Decide what the viewer looks at first in
  each beat, and let everything else wait or recede.
- **Entrances move two or three properties together**, for example opacity
  with a 20–70 px rise and a 0.94→1 scale. An element that only fades in
  looks like a slide transition.
- **Stagger by importance, not source order**: headline before detail, the
  number before its label.
- **Exits exist and are quicker than entrances.** Things that simply vanish
  at a cut look unfinished.
- **Build, breathe, resolve.** Roughly the first third of a beat introduces,
  the middle holds with at most one small continuing motion so the frame
  is not dead, and the end settles or hands over.
- **Contrast of pace.** When everything moves all the time, nothing reads
  as important. Stillness after a move makes the move land. Vary the
  pacing within a piece, too: the slowest beat can be two or three times
  slower than the fastest.
- **Do not start at exactly 0.** Offset the first motion by 0.1–0.3 s, so
  that the first frame is a composed still and not a half-drawn state.
  Where the first frame becomes the thumbnail or preview, make it the
  finished picture instead.
- **Transform the object, do not swap it.** A bar chart that becomes a
  line through the same values, or a button that grows into the panel it
  opens, explains the relationship between them. A crossfade between two
  pictures explains nothing.
- **Loops:** the frame after the last is the first. Either return every
  property to its start value, or build the timeline from periodic
  functions of `t / DURATION`. `check --loop` tests this.

## Layout and type

- Design for the frame, not a page: nothing scrolls, and all of it is seen
  at once, at a distance, possibly small.
- **Safe area**: keep text at least about 6% of the width from the sides and
  9% of the height from the top and bottom. At 1920×1080 that is roughly
  120 px and 100 px. Vertical social formats add platform interface
  overlays; see [`output.md`](output.md).
- **Minimum sizes** at 1080 px on the short side: headline 80 px or more,
  supporting text 40 px or more, labels 28 px or more. Scale them with the
  frame. If text does not fit at these sizes, cut words rather than
  shrinking the type.
- Hero type: weight 600–800, tracking −0.02 to −0.03 em, line-height
  1.0–1.1. Body: regular weight, line-height 1.3–1.4.
- Use `font-variant-numeric: tabular-nums` on changing numbers, so the digits
  do not jitter as they count.
- Use flow layout (flex, grid, padding) for the settled state, and
  transforms for motion. Absolute coordinates everywhere make any change
  of copy a rebuild.
- An element that scales or overshoots needs clearance at its largest
  size, not only its resting one.

## Colour

- Give colours roles: ground, surface, ink, muted, accent. Use about 60%
  ground, 30% surface and ink, 10% accent. The accent marks the one thing
  to look at, so one accented element per frame is usually right.
- Check contrast for text: at least 4.5:1 for body text, and 3:1 for
  headline sizes.
- With a brand, use its colours and type exactly and ask for the files. A
  near-miss looks worse than a neutral palette.

## What makes it look generated

Avoid these unless the brief asks for them:
- the purple-to-blue gradient background;
- glow on everything;
- gradient-filled text;
- bouncy easing on every element;
- a typewriter effect outside a real input field;
- particles for their own sake;
- emoji standing in for icons;
- three-dot loaders;
- stock "abstract tech" shapes;
- everything entering from the same direction with the same curve.

More than two elements animating with the same curve and duration at the
same moment reads as a template.

## Product and interface demos

- **Recreate the interface in HTML** when the demo needs to be crisp, to
  change easily, or to show states that are hard to reach. Match the real
  layout, type and colours from screenshots. Simplify whatever is not the
  point of the demo.
- **Use real screenshots** as images when exact fidelity matters. Pan, zoom
  and annotate them.
- **Composite real footage** when the actual behaviour must be seen. See
  [`determinism.md`](determinism.md) for how to make video frame-accurate.
- A cursor reads as human when it moves along a slight arc with ease-in-out,
  pauses about 0.1–0.2 s before a click, and shows the press with a brief
  scale to about 0.9.
- Zoom in on the area that matters instead of shrinking a whole desktop
  into the frame. Label the thing being shown, not the steps to get there.

## An optional cinematic finish

For film-like pieces, not interfaces or diagrams, these layers go on top of
the composition, from bottom to top:

1. **Moving ground:** two large, heavily blurred radial gradients of the
   palette colours, drifting slowly (`sin(t / 8)` scale motion).
2. **Content.**
3. **Grade:** an accent-coloured layer at 10–25% opacity with `mix-blend-mode:
   soft-light`, and a slight darkening towards the top and bottom.
4. **Grain and vignette:**
   - grain is an SVG `feTurbulence` noise tile at about 5% opacity, offset
     by a hash of the frame index so that it changes every frame yet stays
     deterministic;
   - the vignette is a radial gradient from transparent at about 55% to
     20% black at the corners.

Grain enlarges GIFs a great deal and fights their palette: leave it out of
GIFs.
