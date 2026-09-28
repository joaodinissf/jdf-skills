# Design for paper figures

A paper figure has one job: to make one claim easy to see. It is read at
print size, often in greyscale, next to the text that refers to it.

## Content

- **Draw the mechanism, not an inventory.** Show only the components the claim
  depends on. Show the boundary that is crossed, the data that moves, the
  stage that is added. Group or leave out everything else.
- **One figure, one claim.** The caption states the claim. The figure has no
  title of its own.
- **For a comparison, draw the difference.** Draw the same structure twice
  with only the changed part emphasised, or once with the change marked.
- **Choose the smallest view.** If a three-row table or one sentence makes
  the point, do not draw a figure.
- **Label every arrow** whose meaning is not obvious. Use one to three words,
  such as "writes" or "r₀₀".

## Hierarchy

- **Emphasis.** One element carries the emphasis: usually the paper's
  contribution, or the active part of a step. Give it the single accent (a
  darker fill, a heavier stroke, or one colour). Everything else is white or
  light grey with black strokes.
- **Type.** At most two sizes and two weights per figure. Labels are
  regular, and group titles may be bold.
- **Strokes.** Three levels are enough. 0.4 pt for grids and secondary
  lines, 0.8 pt for boxes and edges, 1.2 pt for the emphasised path.
- **Space.** The gap between groups is larger than the gap inside a group.
  Put more space above a group title than below it.

## Alignment

- Place everything on a grid. Siblings share an edge or a centre line, and
  the gaps between them are equal. Eyeballed offsets read as noise.
- Route arrows straight or at right angles. Avoid crossings where the
  topology allows.
- Keep the same element in the same place across panels, so that the eye
  compares only what changes.

## Colour and text

- **Colour.** Colour is optional in a paper figure, and greyscale is the
  baseline. Use colour to repeat a distinction that lightness, a hatch or a
  line style already makes. Do not let colour carry a distinction alone.
- **Fills.** Keep fill lightness well apart: `check_figure.py` warns below
  15 L*. Use at most three or four fill levels.
- **Palette.** The default in `paper_style.py` puts Paul Tol's
  high-contrast colours first, because they stay distinct in greyscale, and
  Okabe-Ito next, because it is safe for colour-blind readers.
- **Text colour.** Text is black or dark grey. Text on a fill is black or
  white, chosen by the fill's lightness. Never give text the colour of its
  series.
- **Consistency.** A configuration, component or series keeps its colour, hatch
  and position in every figure of the paper. Keep the tokens in one place:
  `paper_style.py`, a TikZ `figstyle.tex`, or one set of draw.io style strings.

## Words for the correction round

When the user asks for a change in words, or when you review your own render,
these verbs name the common moves:

- **distill**: remove boxes and labels that the claim does not need.
- **quieter**: lighten fills, thin strokes, and remove the emphasis from all but one element.
- **emphasise**: give the key element the single accent.
- **align**: snap to the grid, equalise gaps, straighten arrows.
- **label**: name the unlabelled arrows and elements that the text refers to.
- **diff**: for a before/after figure, emphasise only what changed.
