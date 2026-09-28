# TikZ figures

Use TikZ when the paper already has TikZ figures, or when a figure must
share the paper's fonts and mathematics exactly. The `.tex` source is the
scalpel: people edit coordinates, distances and labels as text.

## File layout

- `figures/<name>.tex`: one picture, compiled on its own to
  `figures/<name>.pdf`, which the paper includes with `\includegraphics`.
  This keeps compile errors out of the paper and lets you look at the figure
  alone.
- Start from [`../assets/figure.tex`](../assets/figure.tex). It crops the page to
  the picture with pdfTeX primitives, so it needs no `standalone` or
  `preview` package. If the installation has `standalone`,
  `\documentclass[tikz]{standalone}` works too.
- With more than one TikZ figure, move the `\tikzset{...}` styles into
  `figures/figstyle.tex` and `\input` it from each figure. The styles are
  the paper's design tokens: change a colour or a line weight once.

## Fonts

Match the paper. Look at its preamble:
- IEEEtran and most IEEE templates use Times: `\usepackage{newtxtext,newtxmath}`,
  or `mathptmx` in smaller installations.
- acmart uses Libertine: `\usepackage{libertine}\usepackage[libertine]{newtxmath}`.
- For sans-serif labels, `\usepackage{helvet}` with
  `\renewcommand\familydefault{\sfdefault}`. Latin Modern Sans (`lmodern`) is
  in every installation.

Before choosing, check that the package exists with `kpsewhich newtxtext.sty`. A
small TeX installation may lack font metrics. The compile then fails with
"I can't find file" for a `.tfm`. Choose a font that is present, or tell the
user which package to install (`tlmgr install <package>`). Installing is
their call.

## Drawing

- Libraries: `positioning` (`right=12mm of a`), `arrows.meta`
  (`Stealth[length=2mm]`), `fit` (a group box around nodes), `calc`
  (coordinates between nodes), `backgrounds` (group fills behind nodes).
- Place nodes relative to each other with one distance per level, so gaps
  are equal. Avoid absolute coordinates except for the first node.
- Orthogonal routing: `(a) -| (b)` and `(a) |- (b)`, or explicit corner
  points. Label edges with `node[lbl, above] {...}` on the path.
- Groups: `\node[group, fit=(a) (b) (c), label={[anchor=north]north:Base Station}] {};`
  inside `\begin{scope}[on background layer]`.
- Data-derived figures: loop with `\foreach`, or generate the `.tex` from a
  script that holds the data. The script is then the source.

## Compile and look

```sh
pdflatex -interaction=nonstopmode -halt-on-error figures/name.tex
grep "Missing character" name.log     # glyphs dropped without an error
uv run <skill>/scripts/check_figure.py figures/name.pdf --width single --png name.png
```

Run pdflatex in the figure's folder, or pass `-output-directory`. Some
engines drop missing glyphs silently. The grep catches them.
