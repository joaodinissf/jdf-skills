# paper-figures

*Describe the figure in words. Get a figure that could go in the paper, and a
source you can still edit.*

Makes figures for scientific papers (block and architecture diagrams, graphs
computed from data, result plots) as editable sources: a matplotlib script,
a draw.io file or TikZ. Each exports a vector PDF at the column width. The
agent pins down what the figure must show before it draws. It then renders
the figure, checks it with a script, looks at it in colour and greyscale,
and fixes it before delivering.

The source is the deliverable, not only the image. A person can still take a
scalpel to it: drag a box in draw.io, change a number at the top of the
script, or edit a TikZ distance. Claude can then pick up the edited source
and continue.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s paper-figures
```

For the scripts, [`uv`](https://docs.astral.sh/uv/). The draw.io route needs
the [draw.io desktop app](https://www.drawio.com/) for export, and the TikZ
route needs a TeX distribution.

## Use

- "Draw the system overview for Section 3: the base station on the left with
  the B beamforming patterns and the DL inference block, the mobile device
  on the right, phases A–D, one column wide."
- "From this parity-check matrix H, draw the Tanner graph and one check-node
  update per panel, in black and white."
- "Plot the speedups in results.csv as grouped bars, one group per matrix,
  with the geometric mean."
- "Redraw Figure 4 of our old paper so it fits the ISCA template."
- "Should this figure be Mermaid, Python or TikZ?"

## How it chooses

| The figure | Route |
|---|---|
| Plots, and anything computed from data | matplotlib script, with `paper_style.py` shared by all figures |
| Block diagrams that people will polish by hand | draw.io file, exported with the desktop app |
| Papers that already use TikZ, or figures that must match the paper's fonts | TikZ, compiled on its own |

Mermaid is for drafts only: it cannot fix positions. Excalidraw and tldraw
suit talks, not papers.

## Files

| File | Read when |
|---|---|
| [`SKILL.md`](SKILL.md) | Always: the method and the route choice |
| [`references/matplotlib.md`](references/matplotlib.md) | Writing a figure script or a plot |
| [`references/drawio.md`](references/drawio.md) | Writing or exporting a `.drawio` file |
| [`references/tikz.md`](references/tikz.md) | Writing or compiling a TikZ figure |
| [`references/design.md`](references/design.md) | Before drawing: emphasis, hierarchy, alignment, colour |
| [`references/checklist.md`](references/checklist.md) | Looking at a rendered figure |
| [`references/venues.md`](references/venues.md) | Finding the column width |
| [`scripts/paper_style.py`](scripts/paper_style.py) | Copied into the paper's `figures/`: size, fonts, palette, export |
| [`scripts/check_figure.py`](scripts/check_figure.py) | After every render: width, fonts, text size, greyscale, contrast |
| [`assets/figure.tex`](assets/figure.tex) | Starting a TikZ figure |

## Related

- `dataviz` (built into Claude Code and claude.ai): chart form, palette
  validation, mark specifications.
- [K-Dense scientific-visualization](https://github.com/K-Dense-AI/claude-scientific-skills)
  (MIT): a publication matplotlib style and figure audits.
- [SciencePlots](https://github.com/garrettj403/SciencePlots) (MIT):
  matplotlib styles for journals, including IEEE.
- [impeccable](https://github.com/pbakaus/impeccable) (Apache-2.0): a design
  vocabulary and critique commands.
- [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
  (MIT): research workflow skills, including paper figures and systems-paper
  writing.

## Credits

Ideas were adapted in new words and code. No text or code was copied.

- K-Dense scientific-visualization (MIT): fixed physical size instead of a
  tight bounding box, Type 42 fonts, a greyscale lightness screen.
- ARIS paper-figure (MIT): render and then verify, correctness before style.
- Orchestra AI-Research-SKILLs academic-plotting (MIT): one script per
  figure, kept for reproducibility.
- thesis-figure-skill (MIT): a named list of the ways academic figures look
  machine-made. Checking the compile log for missing glyphs.
- dataviz and artifact-diagramming (Anthropic): a second channel for colour,
  direct labels, drawing the mechanism, labelled arrows.
- impeccable (Apache-2.0): a vocabulary of correction moves.
- Paul Tol's colour schemes and the Okabe-Ito palette: the default colours.
- Rougier, Droettboom and Bourne, "Ten Simple Rules for Better Figures"
  (PLoS Comput Biol, 2014), and Wilke, *Fundamentals of Data Visualization*.
