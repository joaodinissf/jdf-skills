# Product demos from a real application

How to show a real desktop application doing something, such as a menu path, a dialog or a feature, as a
composed, shareable animation. The method is:
1. Capture one real screenshot per UI state.
2. Record where each click lands.
3. Compose the motion (cursor, camera, highlights and captions) as a `seek(t)` page.

Every pixel of the product is real. The motion is designed rather than recorded: there is no jitter, no dead
time and no stray notifications. When the product changes, you rerun the capture and render again.

For a web application, skip everything below. Playwright drives the page directly and can screenshot any
state without touching the user's screen.

## What it needs

On macOS, the process that drives the application needs these permissions (System Settings → Privacy &
Security), granted by the user:

- **Accessibility**: to post real mouse and keyboard events (Quartz `CGEventPost`) and to read element
  positions (`AXUIElement`).
- **Screen Recording**: for `screencapture`. Without it, captures show only the wallpaper, silently.
- **Automation → System Events**: to place and size the window.

The capture uses the real pointer and keyboard. Ask the user to keep their hands off them for its duration,
and to silence notifications. Tell them explicitly when the screen is theirs again, and when the application
can be closed.

Windows (UI Automation) and Linux (AT-SPI, `xdotool`) have equivalents.

## Setting up the capture

- **Use a throwaway workspace or profile**, so that nothing of the user's is changed or shown.
- **Place the window at a fixed position and size**, such as 1600×900 below the menu bar, and capture a
  fixed screen region (`screencapture -x -R0,0,W,H`). Then every screenshot and every recorded rectangle
  share one coordinate system.
- **Prepare the starting state off camera**, and check it with a screenshot before capturing.

## Capturing each state

Write a small script that drives the application. For each state:
1. Take a screenshot.
2. Record the rectangle of the element that the next action targets.
3. Perform the action.
4. Wait for the resulting state.

Write the states to a JSON file, and to a `.js` file (`window.SHOTS = …`) so that the composition can load
them from `file://`.

Failures seen in practice, and what fixes each:

| Symptom | Cause | Fix |
|---|---|---|
| The first screenshot shows another app | The app that launched the script is still in front | Click the target window's title bar before the first screenshot |
| The wrong menu opens | A diagonal pointer move from a menu-bar item crosses the neighbouring item | Move in an L: straight down out of the bar, then across |
| Typed text comes out scrambled, or turns into shortcuts | Fast synthetic keys are reordered under load; a modifier set for an earlier shortcut carries over | Type one character at a time (about 0.1 s apart), and set flags explicitly on every event |
| A "result" screenshot shows the dialog still busy | A fixed sleep was too short on a loaded machine | Wait for evidence of the state, such as the window title changing or an element appearing |
| No position for a submenu item | Some toolkits (SWT, for example) do not expose submenu items to accessibility | Measure from a screenshot, then fit it (below) |
| A floating input-source bubble or tooltip appears in some frames | An OS overlay drawn over the application | Cover it with the same area from a frame without it, or wait until it fades |

## Aligning overlays with the pixels

Highlights, the cursor and callouts only read as precise when they sit on what the eye sees. The rectangle
a script records is often not that:

- **Accessibility frames include shadows and padding.** A button's frame runs below its visible edge. A
  menu-bar item's frame is taller than the visible bar.
- **Hand-measured rectangles drift** by several pixels.

**Fit each target to its visible content before composing**, with
[`scripts/fit_targets.py`](../scripts/fit_targets.py):

```sh
uv run scripts/fit_targets.py --steps shots.json     # rewrites each step's target, keeps target_raw
```

It estimates the background just outside each rectangle, keeps what differs from it, strips border lines
at the edges, and takes the bounding box. Pad highlights evenly around the fitted box, and keep them
inside the frame.

**Declare every overlay in `window.ALIGN`, so that `check` measures it.** A contact sheet is too small to
show a 3–5 px offset, and looking is the step that gets skipped:

```js
window.ALIGN = [
  { t: 10.45, overlay: '#ring', target: finishRect, in: '#world' },           // surrounds the button
  { t: 10.7, overlay: '#cursor', target: finishRect, in: '#world',
    hotspot: [2 / 22, 2 / 32] },                                             // tip lands on it
];
```

`check` fails when an overlay:
- is off-centre from its target, or cuts across it;
- is clipped by an ancestor;
- is invisible at its moment;
- has a target whose own visible content is off-centre, meaning the rectangle came from an accessibility
  frame or a hand measurement.

`sheet --align --scale 2` writes one crop per entry, marked OFF where it fails, to look at.

Declare each moment while the state it points at is still on screen. A ring that lingers past the click
frame outlines empty space on the next screen.

## Composing

- **Cut between screenshots on the click frame.** A hard cut matches how the UI itself changes.
- **Draw the cursor inside the zoomed world**, so it moves with the camera:
  - scale it by about `1 / sqrt(zoom)`;
  - follow the same L-shaped paths as the capture;
  - pause for about 0.15 s before each click, and show the press.
- **Keep zoom at or below 1.7× on 1× captures.** Beyond that, upscaled text turns soft. On a 2× (Retina)
  screen, captures stay sharp at higher zoom.
- **Keep the capture and the composition in one folder** with a short README: how to regenerate, what is
  real and what is staged, and anything that must be rechecked after a new capture, such as masks and
  measured rectangles.
