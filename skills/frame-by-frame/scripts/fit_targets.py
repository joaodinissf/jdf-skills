#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Shrink target rectangles to the visible content inside them, so overlays centre on what the eye sees.

    uv run fit_targets.py shot.png 984,644,92,18 [x,y,w,h ...]     # print fitted rectangles
    uv run fit_targets.py --steps shots.json [--images shots/]       # rewrite each step's "target"

Accessibility frames include shadows and padding (a button's frame runs below its visible edge; a menu-bar
item is taller than the bar), and hand-measured rectangles drift. For each rectangle: estimate the background
from a thin ring just outside it, keep the pixels inside that differ clearly from that background, strip
border or separator lines at its edges, and take the bounding box of what remains.

With --steps, each step {"image": ..., "target": [x, y, w, h]} is fitted; the original is kept as
"target_raw", so rerunning fits from the original again. A sibling shots.js (window.SHOTS = ...) is rewritten
too when it exists.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import median

from PIL import Image

MARGIN = 3  # the background is sampled on a ring this far outside the rectangle
THRESHOLD = 48  # content differs from the background by more than this in some channel


def fit(img: Image.Image, rect: list[int]) -> list[int]:
    x, y, w, h = rect
    W, H = img.size
    px = img.load()
    x0, y0 = max(0, x - MARGIN), max(0, y - MARGIN)
    x1, y1 = min(W - 1, x + w + MARGIN), min(H - 1, y + h + MARGIN)
    border = (
        [px[i, y0] for i in range(x0, x1)]
        + [px[i, y1] for i in range(x0, x1)]
        + [px[x0, j] for j in range(y0, y1)]
        + [px[x1, j] for j in range(y0, y1)]
    )
    bg = tuple(median(c[k] for c in border) for k in range(3))
    cols = range(max(0, x), min(W, x + w))
    rows = range(max(0, y), min(H, y + h))
    fg = {
        (i, j)
        for j in rows
        for i in cols
        if max(abs(px[i, j][k] - bg[k]) for k in range(3)) > THRESHOLD
    }

    # A full-width row (or full-height column) at the rectangle's edge is a border or separator, such as a
    # window edge just under a menu bar, not the element. Strip those from the edges inwards only: a solid
    # button is full-width on every row and must survive.
    def full_row(j):
        return sum((i, j) in fg for i in cols) > 0.9 * len(cols)

    def full_col(i):
        return sum((i, j) in fg for j in rows) > 0.9 * len(rows)

    ry, rx = list(rows), list(cols)
    for seq, full in ((ry, full_row), (rx, full_col)):
        while len(seq) > 1 and full(seq[-1]) and not full(seq[len(seq) // 2]):
            seq.pop()
        while len(seq) > 1 and full(seq[0]) and not full(seq[len(seq) // 2]):
            seq.pop(0)
    keep = [(i, j) for i, j in fg if ry[0] <= j <= ry[-1] and rx[0] <= i <= rx[-1]]
    if not keep:
        return list(rect)
    xs, ys = [i for i, _ in keep], [j for _, j in keep]
    return [min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("image", nargs="?", type=Path)
    ap.add_argument("rects", nargs="*", help="x,y,w,h in image pixels")
    ap.add_argument(
        "--steps",
        type=Path,
        help='JSON with {"steps": [{"image": ..., "target": ...}]}',
    )
    ap.add_argument(
        "--images",
        type=Path,
        help="directory of the step images (default: beside --steps)",
    )
    args = ap.parse_args()

    if args.steps:
        data = json.loads(args.steps.read_text())
        images = args.images or args.steps.parent
        for step in data["steps"]:
            raw = step.get("target_raw") or step.get("target")
            if not raw:
                continue
            path = images / step["image"]
            if not path.exists():
                path = args.steps.parent / "shots" / step["image"]
            step["target_raw"], step["target"] = (
                raw,
                fit(Image.open(path).convert("RGB"), raw),
            )
            print(f"{step['image']}: {raw} -> {step['target']}")
        args.steps.write_text(json.dumps(data, indent=2))
        js = args.steps.with_suffix(".js")
        if js.exists():
            js.write_text("window.SHOTS = " + json.dumps(data) + ";\n")
        return 0

    if not args.image or not args.rects:
        ap.error("give an image and at least one rectangle, or --steps")
    img = Image.open(args.image).convert("RGB")
    for r in args.rects:
        rect = [int(v) for v in r.split(",")]
        print(json.dumps({"raw": rect, "fitted": fit(img, rect)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
