"""Shared figure style for one paper.

Copy this file into the paper's figures/ folder once, then import it from
every figure script so all figures share one size, font and palette:

    import paper_style as ps
    fig, ax = ps.figure(width="single")
    ...
    ps.save(fig, "speedup")          # speedup.pdf, speedup.svg, speedup.png

Change VENUE, FONT and the palette here, not in individual scripts.
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

# Column and text widths in inches. Measure them from the paper's template
# when you can (see references/venues.md) and correct these values.
WIDTHS_IN = {
    "ieee": {"single": 3.5, "double": 7.16},
    "acm": {"single": 3.33, "double": 7.0},
}
VENUE = "ieee"

# "sans" suits block diagrams and plots. "serif" matches Times body text
# and suits figures dense with mathematical notation.
FONT = "sans"
FONT_PT = 8
SMALL_PT = 7

# Paul Tol's high-contrast set first: it stays distinct in greyscale.
# Okabe-Ito follows for more series. Pair each colour with a hatch or marker.
PALETTE = [
    "#004488",
    "#DDAA33",
    "#BB5566",
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#56B4E9",
]
HATCHES = ["", "////", "\\\\\\\\", "xxxx", "...."]
MARKERS = ["o", "s", "^", "D", "v", "P"]
INK = "#000000"
MUTED = "#6E6E6E"
LIGHT_FILL = "#E8E8E8"

# Stroke weights in points: grid, normal, emphasis.
LW_HAIR, LW, LW_BOLD = 0.4, 0.8, 1.2


def apply():
    """Set the rcParams. figure() calls this, so scripts rarely need to."""
    sans = ["Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"]
    serif = ["Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"]
    mpl.rcParams.update(
        {
            "font.family": "sans-serif" if FONT == "sans" else "serif",
            "font.sans-serif": sans,
            "font.serif": serif,
            "mathtext.fontset": "dejavusans" if FONT == "sans" else "stix",
            "font.size": FONT_PT,
            "axes.titlesize": FONT_PT,
            "axes.labelsize": FONT_PT,
            "xtick.labelsize": SMALL_PT,
            "ytick.labelsize": SMALL_PT,
            "legend.fontsize": SMALL_PT,
            "legend.frameon": False,
            "axes.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.prop_cycle": mpl.cycler(color=PALETTE),
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "lines.linewidth": 1.0,
            "lines.markersize": 4,
            "hatch.linewidth": 0.5,
            "patch.linewidth": LW,
            "grid.linewidth": LW_HAIR,
            "grid.color": "#CCCCCC",
            # TrueType (Type 42) keeps text searchable and embeds cleanly.
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            # Text stays text in the SVG, so it can be edited in Inkscape.
            "svg.fonttype": "none",
            # A fixed page size: "tight" would change the physical width.
            "savefig.bbox": "standard",
            "savefig.dpi": 300,
            "figure.dpi": 150,
        }
    )


def width_in(width="single"):
    """Width in inches for "single", "double" or a number of inches."""
    if isinstance(width, (int, float)):
        return float(width)
    return WIDTHS_IN[VENUE][width]


def figure(width="single", height=None, aspect=0.62, **subplots_kw):
    """A figure at the final printed size. Returns (fig, ax) like plt.subplots."""
    apply()
    w = width_in(width)
    h = height if height is not None else w * aspect
    subplots_kw.setdefault("layout", "constrained")
    return plt.subplots(figsize=(w, h), **subplots_kw)


def value_grid(ax, axis="y"):
    """A hairline grid on the value axis only, drawn behind the data."""
    ax.grid(True, axis=axis)
    ax.set_axisbelow(True)


def save(fig, stem, outdir=None):
    """Write stem.pdf, stem.svg and a 300 dpi stem.png preview. Returns the paths."""
    out = Path(outdir) if outdir else Path.cwd()
    out.mkdir(parents=True, exist_ok=True)
    paths = [out / f"{stem}.{ext}" for ext in ("pdf", "svg", "png")]
    for p in paths:
        fig.savefig(p)
    return paths
