# matplotlib figures

Use a script when the figure is computed from data, and for every plot.
The script is the source: a person edits its data and its named constants,
or asks Claude for a change, and runs it again.

## Script shape

```python
# /// script
# dependencies = ["matplotlib>=3.8", "numpy"]
# ///
"""Tanner graph of H with one check-node update per panel.  uv run tanner.py"""
import numpy as np
import paper_style as ps

# Data: the drawing is computed from these.
H = np.array([[1, 1, 1, 0, 0, 0, 0, 0], ...])
UPDATES = [(0, 0), (1, 4), (2, 6), (3, 7)]

# Knobs: numbers a person may want to nudge, named and in one place.
PANEL_GAP = 0.35
LABEL_OFFSET = {"q10": (-0.08, 0.0)}

def main():
    fig, axes = ps.figure(width="single", height=4.6, nrows=len(UPDATES))
    ...
    ps.save(fig, "tanner")

if __name__ == "__main__":
    main()
```

- **Data at the top, computed drawing below.** Edges come from `H`, bars from
  the results table, stage boxes from a list of stages. Assert that the data
  is consistent (every highlighted edge exists in `H`), so a wrong edit fails
  loudly.
- **Knobs** are the scalpel. Put every value a person might want to tune
  (gaps, offsets for one label, emphasis) in named constants, not deep in
  the drawing code.
- `paper_style.py` sets the size, fonts, palette and export. Copy it into
  the paper's `figures/` folder once and import it everywhere, so all
  figures of the paper agree.

## Diagrams with matplotlib

Use one axes with `ax.set_aspect("equal")`, `ax.axis("off")` and data
coordinates in a unit that suits the layout (one grid cell, one millimetre).

- Boxes: `matplotlib.patches.Rectangle` or `FancyBboxPatch` with
  `boxstyle="square,pad=0"`. Rounded corners only when the paper's other
  figures use them.
- Arrows: `FancyArrowPatch(posA, posB, arrowstyle="-|>", mutation_scale=6,
  shrinkA=0, shrinkB=0)`. Compute the start and end on the box edges, so
  arrows touch the boxes and do not overlap them.
- Circles and nodes: `Circle`. Draw nodes after edges (`zorder`) so edges
  end cleanly under them.
- Text: `ax.text(x, y, s, ha="center", va="center")`. Use mathtext for
  notation: `r"$q^{(i-1)}_{10}$"`.

### Label placement

Overlapping labels are the most frequent defect. Place labels by measuring
them, not by guessing offsets:

1. Draw the label, then get its extent in data units:
   `bb = txt.get_window_extent(fig.canvas.get_renderer()).transformed(ax.transData.inverted())`.
2. Move it along the normal of the line it labels by half its extent plus a
   small gap, so it clears the line at any angle.
3. Check the label against the other labels and nodes. When two collide,
   move the one with more free space, or put it on the other side.

## Plots

- **Form first.** Bars for a few categories, lines for trends over an
  ordered axis, points for correlation. Small multiples instead of more
  than about five series in one panel.
- **Second channel.** Every series has a colour and a hatch (bars) or a
  marker shape (lines), taken from `ps.PALETTE` with `ps.HATCHES` or
  `ps.MARKERS` in the same order. The series order and style stay the same
  in every figure of the paper.
- **Labels.** Label up to four series directly, at the line end or on the
  bar. Otherwise use a frameless legend in one row above the plot, or in
  empty plot space, never over data.
- **Axes.** Units on every axis label. A log scale when values span orders of
  magnitude, with "(log scale)" in the label. No dual y-axes: normalise to
  a baseline instead (speedup ×, energy relative to baseline).
- **Grid.** A hairline grid on the value axis only (`ps.value_grid(ax)`).
- **Summaries.** Say how means are taken (geometric mean for ratios such as
  speedup). Put a mean bar or line in the same style as the data, and
  labelled.
- **Honesty.** Start bar axes at zero. Plot only configurations measured
  under comparable conditions. Never invent a value; label placeholders as
  placeholders.

## Output

`ps.save(fig, "name")` writes:
- `name.pdf`: the deliverable, with Type 42 fonts embedded;
- `name.svg`: text kept as text, so it can be edited in a vector editor;
- `name.png`: a 300 dpi preview to look at.

The size is fixed: `savefig.bbox` is `"standard"`, so the PDF is exactly the
width it was drawn for. Do not pass `bbox_inches="tight"`: it changes the
physical width, and LaTeX then rescales the text.
