# Column widths

Draw every figure at the width it will be printed. Then LaTeX includes it
at 100 % and its text keeps the size it was drawn at.

## Measure it from the paper

When the paper's source is available, measure. Put these lines in the
document body temporarily, compile, and read the log:

```latex
\typeout{COLUMNWIDTH=\the\columnwidth}
\typeout{TEXTWIDTH=\the\textwidth}
```

```sh
grep -E "COLUMNWIDTH|TEXTWIDTH" paper.log     # e.g. COLUMNWIDTH=252.0pt
```

Convert to inches: TeX points ÷ 72.27. Remove the lines afterwards.

Without a TeX installation, read the document class and its options
(`\documentclass[conference]{IEEEtran}`, `\documentclass[sigconf]{acmart}`)
and use the table below.

## Common templates

These are the widths of the standard templates. A venue can change its
template in any year. Check the call for papers, or measure.

| Template | Single column | Full width (`figure*`) |
|---|---|---|
| IEEEtran (conference and journal, two columns) | 3.5 in (88.9 mm) | 7.16 in (181.9 mm) |
| acmart `sigconf` / `sigplan` (two columns) | 3.33 in (84.7 mm) | 7.0 in (177.8 mm) |
| LNCS (one column) | — | 4.8 in (122 mm) |

Computer-architecture venues use these templates. ISCA, MICRO and HPCA
have used IEEEtran-based templates. ASPLOS has used acmart `sigplan`.
Confirm for the year you target.

## Heights and fonts

- **Height.** Choose a height that the content needs. A plot is usually about
  0.6× its width. Tall diagrams are acceptable in one column, but a full page
  height is rarely right.
- **Text.** In a two-column paper, figure text of 7–9 pt matches the body
  (which is about 10 pt) after the caption. Text below 6 pt is hard to read in
  print. `check_figure.py` warns about it.
