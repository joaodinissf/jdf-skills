---
name: paper-figures
description: Make figures for scientific papers — block and architecture diagrams, graphs computed from data, and result plots — as editable sources (a matplotlib script, a draw.io file or TikZ) that export vector PDF at the column width, then look at the render and fix it before delivering. Use when asked for a figure, diagram, schematic, plot or chart for a paper, thesis or LaTeX document, to redraw or clean up a paper figure, or to choose between Mermaid, Python, draw.io and TikZ for one. Not for photorealistic images, slides-only graphics or dashboards.
---

# Paper figures

*Describe the figure in words. Get a figure that could go in the paper, and a
source you can still edit.*

A paper figure is judged at print size, often in greyscale, next to text that
refers to it. A plausible render is easy to make. A usable figure says exactly
what the text says, fits the column without scaling, and was looked at before
anyone else saw it.

A figure also changes after its first version. So deliver a source that the
user and Claude can both edit, not only an image. Polishing an exported SVG by
hand is one-way: the next regeneration erases the polish.

The method: pin down what the figure must show, choose a route, generate the
drawing from its data, render, look, fix, and deliver the source with its
outputs.

## Scope

Say so plainly, and do not force the method, when:

- the request is for a photograph, a rendering or a likeness. An image model
  makes those;
- the figure is for slides or a web page only. Screen sizes and dark mode
  follow other rules;
- a table or one sentence makes the point better than a figure.

## 1. Pin down the figure

Take these from the request and from the paper's repository first. Ask only
for what would change the result, in one batch.

- **Message:** what a reader must understand after looking. One sentence.
- **Content:** every element, label and connection, in the paper's exact
  terms and notation. Missing content is the most expensive defect, because
  nobody notices it until review.
- **Data:** if the drawing follows from data (a matrix, a results table, a
  topology, a list of stages), get the data, not a description of the
  picture. The source computes the drawing from it. The figure then cannot
  disagree with the data.
- **Width:** single or double column, and the venue. Measure it from the
  paper's template when there is one. See [`references/venues.md`](references/venues.md).
- **References from the text:** labels, phases, panel letters or examples
  that the prose mentions. They must appear, spelled the same way.

When the repository has a `.tex` file, read its preamble and its figures
folder. The document class gives the width. Existing `.drawio` files,
`.tikz`/`.tex` figures, figure scripts or a style module show how the group
makes figures.

When the user gives an existing figure to redraw, extract the points above
from it and from the paper's text. Then design the new figure instead of
tracing the old one. Fix what the old one got wrong, such as a duplicated
label or inconsistent notation, and report the fix.

## 2. Choose the route

Three routes make figures that belong in a paper. They differ in who edits
the figure next, and how.

| Route | Best for | How the user edits it | Read |
|---|---|---|---|
| **matplotlib script** | Plots. Any figure computed from data | Data and named constants at the top of the script, or a request to Claude | [`references/matplotlib.md`](references/matplotlib.md) |
| **draw.io file** | Block and architecture diagrams that people polish by hand | The draw.io editor: drag a box and its arrows follow | [`references/drawio.md`](references/drawio.md) |
| **TikZ** | Papers that already use TikZ. Figures that must match the paper's fonts exactly | Coordinates and distances in the `.tex` source | [`references/tikz.md`](references/tikz.md) |

Decide with these signals, in this order:

1. **The paper's habits.** Match the tools the repository already uses,
   unless the user asks otherwise.
2. **Data.** If the drawing is computed from data, write a script.
3. **Hand-tuning.** If the layout carries meaning and people will want to
   adjust it, make a draw.io file.
4. **Otherwise** ask in one line, or use a matplotlib script.

Mermaid is acceptable for a quick draft or documentation, where any tidy
layout will do. It cannot fix positions. When the layout matters, change
route and say why. Do not post-process Mermaid's SVG to force a layout.
Hand-drawn tools such as Excalidraw and tldraw look like sketches. They
suit talks and design discussions, not papers.

## 3. Build

Put each figure in the paper's `figures/` folder. Create the folder if
necessary. Use one source per figure, named after it (`figures/tanner.py`,
`figures/system.drawio`, `figures/pipeline.tex`), with its outputs beside it.

- **matplotlib:** copy [`scripts/paper_style.py`](scripts/paper_style.py)
  into `figures/` once per paper, and import it in every figure script. Then
  all figures share one size, font and palette. Put the data and the
  adjustable constants at the top of the script.
- **draw.io:** write uncompressed XML. Attach every edge to its boxes. Set
  the font, size and colours on every cell. Export the PDF with the desktop
  application's command line.
- **TikZ:** start from [`assets/figure.tex`](assets/figure.tex). It compiles
  to a PDF cropped to the picture and needs only the `tikz` package. Match
  the paper's fonts.

For the craft that all three routes share (emphasis, hierarchy, alignment,
colour), read [`references/design.md`](references/design.md) before you draw.
Every distinction that colour carries must also have a second channel:
lightness, a hatch, a marker or a line style. Many readers print in black
and white.

## 4. Render and look

Code that runs says nothing about what a reader sees. After every render:

1. Check the exported PDF:
   ```sh
   uv run scripts/check_figure.py figures/x.pdf --width single --png x.png --grey x-grey.png
   ```
   It reports the page width against the column, fonts that are not
   embedded, the smallest text, fills that look alike in greyscale, and
   low-contrast text. For an SVG, it reports text held in `<foreignObject>`.
   Fix every error. Decide on each warning.
2. **Open the PNG and the greyscale PNG, and look at them.** Go through
   [`references/checklist.md`](references/checklist.md): correctness first,
   then legibility, then the signs of a generated look.
3. Fix, render and look again. Keep the first render as `x-v1.png` when a
   fix changes something visible. Two or three rounds usually settle it.
   If defects remain after that, report them instead of continuing.

Script paths are relative to this skill's directory. Call the script by its
full path from the user's project. `uv run` supplies its dependencies.
Without `uv`, install `pdfplumber`, `pypdf` and `pypdfium2` in a virtual
environment. The draw.io and TikZ routes need the draw.io desktop
application or a TeX distribution. When one is missing, say which one and
give the install command. Installing is the user's call.

## 5. Deliver

- The source, its outputs (PDF, and a PNG preview), and the command that
  regenerates them.
- A LaTeX snippet at the width the figure was drawn for:
  ```latex
  \begin{figure}[t]
    \centering
    \includegraphics[width=\columnwidth]{figures/x.pdf}
    \caption{...}
    \label{fig:x}
  \end{figure}
  ```
  For a double-column figure, use `figure*` and `\textwidth`.
- A short report: what was made, which checks ran and what they found,
  what was fixed, and every assumption the user has not confirmed, such as
  an invented label, an illustrative value or a guessed width. Never invent
  data for a plot. If numbers are missing, ask, or plot placeholder values
  labelled as placeholders.

For a later change, edit the source and render again. Do not regenerate the
figure from scratch: that loses what was already right, and any edits the
user made by hand.

## Related skills

Other skills cover parts of this work in more depth. When one is available,
use it for its craft inside this method:

| Need | Companion skill | Use it for |
|---|---|---|
| Plots | `dataviz`, K-Dense `scientific-visualization`, SciencePlots styles | Choosing the chart form, palette validation, mark specifications |
| Diagram content | `artifact-diagramming` | Drawing the mechanism, labelled arrows, alignment |
| A second opinion | `impeccable` (`critique`, `polish`, `quieter`) | A structured review of the rendered figure |

When a companion's advice conflicts with the paper, the paper wins. This
covers the column width, greyscale print, the paper's fonts and notation, and
what the text refers to. For example, screen text sizes and dark mode do not
apply to print. Without a companion, the references in this skill are
enough.
