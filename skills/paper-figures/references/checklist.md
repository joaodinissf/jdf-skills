# Checklist for a rendered figure

Look at the PNG, not at the code. Go through the lists in order: a
correctness defect makes legibility irrelevant.

## 1. Correctness

- Every element, label and connection from the request is present, spelled
  as in the paper, in the paper's notation (subscripts, symbols, units).
- Every arrow points in the direction the text says data or control flows.
- Numbers and edges match the data. For a data-derived figure, spot-check
  two or three against the data by hand.
- What the text refers to (panel letters, phase names, a worked example) is
  visible and labelled the same way.
- A claim in the caption holds for every bar, line or panel it covers.
- Nothing is invented: no placeholder value is presented as a real one.

## 2. Legibility

- No label overlaps another label, a line or a node. No text is clipped at the
  figure edge.
- The smallest text is readable at print size. `check_figure.py` reports the
  smallest size. Subscripts and superscripts print at about 70 % of their base
  size. Set mathematical labels at 8 pt or more, so the scripts stay at about
  5.5 pt or more. A warning that only concerns those scripts is acceptable.
- The figure is exactly the width it was drawn for (one column or the full
  text width). `check_figure.py` reports it.
- In greyscale, every distinction survives. Render with `--grey` and look:
  fills with near-equal lightness need a hatch or a different lightness.
- Alignment: siblings share edges or centres and have equal gaps. Arrows run
  straight or at right angles, and cross as rarely as the topology allows.
- One thing draws the eye first: the element the caption talks about.

## 3. Does it look generated?

These make a figure look machine-made or amateur. Remove them unless the
paper's other figures use them.

- A different colour for every block, for no reason.
- Shadows, gradients, 3D bevels, glow.
- Rounded corners on everything.
- Arrowheads of mixed styles or sizes. Arrows without labels where the relation
  is not obvious.
- Uneven gaps and eyeballed offsets.
- Emoji, clip-art icons, decorative pictograms.
- Bold everywhere, or more than two type sizes.
- Centred paragraphs inside boxes. Put sentences in the caption, not in the
  figure.
- A title inside the figure that repeats the caption.
- The tool's default look: draw.io's light blue and orange fills, Mermaid's
  default theme, matplotlib's default blue and orange with the top and right
  spines, Times at 12 pt.

Finish with one question: **could this figure belong to any paper?** If it
could, it is generic. Make the paper's own contribution visible: give the
new or changed component the single emphasis.
