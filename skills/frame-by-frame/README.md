# frame-by-frame

*Decide every frame before drawing one. Look at them before calling it done.*

Makes motion graphics and still images as code: an HTML, SVG or canvas page
whose every frame is a pure function of time. Renders it deterministically
to MP4, WebM, ProRes with alpha, GIF or PNG, and inspects the rendered
frames before delivering.

The code is the easy part. What makes the difference is writing down the
states and timing first (a brief with a beat table), then looking at the
frames. Checks catch what a viewer would see but the code does not reveal:
a fallback font, clipped text, a frame that moves nothing, a loop that
jumps. A contact sheet then lets the agent look at what those checks cannot
judge.

## Use

- "Make a 6-second title card for the release, 1920×1080 MP4."
- "Animate this chart: bars grow in, then morph into a line. Loop it as a GIF for the README."
- "A 15-second vertical clip showing the three steps of onboarding."
- "A 1200×630 social preview image for this post."
- "Recreate this dialog from the screenshot and show a user filling it in."

## How it renders

`scripts/render.py` is a single Python script with inline dependencies. `uv
run` provides Playwright in an isolated environment, and ffmpeg encodes.
Before the page's scripts run, it installs a controlled clock:
- `Date`, `performance.now` and `requestAnimationFrame` follow the frame's time;
- `Math.random` is seeded per frame;
- CSS animations, Web Animations and SMIL are paused and set to the frame's time.

Pages that read the clock therefore still render identically every time.

| Command | Does |
|---|---|
| `check page.html [--loop]` | Fails on script errors, missing fonts, a `seek` that is not pure, nothing moving, or a loop that jumps. Warns about clipped text and network fetches. |
| `sheet page.html out.png --at …` | A labelled contact sheet of chosen frames, to look at. |
| `still page.html out.png --at T` | One frame, optionally at 2× scale. |
| `video page.html out.{mp4,webm,mov,gif}` | Every frame, with optional motion blur and alpha. It checks the encoded file afterwards. |

## Files

| File | Read when |
|---|---|
| [`SKILL.md`](SKILL.md) | always: scope, brief, build, check, render, report |
| [`references/craft.md`](references/craft.md) | choreographing: easing, springs, durations, layout, type, colour, what looks generated, product demos |
| [`references/determinism.md`](references/determinism.md) | using a library, canvas, WebGL, footage, fonts or randomness |
| [`references/output.md`](references/output.md) | choosing a format and size; GIF, alpha, blur, audio, compositing |
| [`references/product-demos.md`](references/product-demos.md) | demoing a real desktop application from its screenshots: capture, permissions, overlay alignment |
| [`assets/template.html`](assets/template.html) | starting a composition |
| [`scripts/render.py`](scripts/render.py) | checking and rendering |

## Related

- [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0) is a
  full framework built on the same idea. It has a CLI, a studio, about a
  hundred lint rules, layout and contrast audits, and workflows for
  captions, avatars and product videos. Reach for it when you want that
  machinery.
- [Remotion](https://www.remotion.dev) writes video as React components. Its
  licence requires a company licence above a small team size.

This skill depends on neither. It is one script and a contract a page can
meet in plain HTML.

## Credits

Ideas were adapted in new words and code. No text or code was copied.

- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
  (Apache-2.0):
  - a controlled clock injected before page scripts;
  - seeking CSS, Web Animations and library timelines;
  - failing a composition in which nothing moves;
  - "build the end state first";
  - timing and choreography defaults.
- [charlie947/motion-graphics-skills](https://github.com/charlie947/motion-graphics-skills)
  (MIT):
  - the single-file `seek(t)` page with a `?render` mode;
  - a brief with states and timings;
  - separating measured, target and illustrative data;
  - named frames to check;
  - the loop-seam test;
  - a dither-free GIF palette for flat art.
- [Barty-Bart/motion-graphics](https://github.com/Barty-Bart/motion-graphics)
  (MIT):
  - closed-form springs;
  - motion blur from sub-frame samples blended with `tmix`;
  - ProRes 4444 for alpha;
  - contact sheets for inspection.
- [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill)
  (MIT):
  - multi-property entrances;
  - faster exits;
  - rhythm of holds;
  - a render, inspect and fix loop with a named defect list;
  - the optional grade, grain and vignette finish.
- [remotion-dev/skills](https://github.com/remotion-dev/skills),
  [delphi-ai/animate-skill](https://github.com/delphi-ai/animate-skill) and
  [supermemoryai/skills `svg-animations`](https://github.com/supermemoryai/skills/tree/main/svg-animations)
  (no licence stated) informed a few general principles. Those principles
  are restated here, not reproduced: layout for a frame rather than a page,
  minimum type sizes, perceptual scale, easing by direction of travel, and
  seeking SMIL and CSS animation in SVG.
