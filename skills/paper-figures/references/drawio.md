# draw.io figures

Use a `.drawio` file for block and architecture diagrams that people will
polish by hand. In the draw.io editor (desktop, web or the VS Code
extension) a person drags a box and its arrows follow, retypes a label, and
aligns a row. Claude can read the edited file and continue from it.

## The file

A `.drawio` file is XML. Write it uncompressed, so both people and Claude
can read the changes in a diff:

```xml
<mxfile>
  <diagram name="system">
    <mxGraphModel gridSize="5" grid="1" page="0" math="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- a group: a container, children use coordinates relative to it -->
        <mxCell id="bs" value="Base Station" vertex="1" parent="1"
          style="container=1;collapsible=0;verticalAlign=top;fontStyle=1;fillColor=#F2F2F2;strokeColor=#000000;fontFamily=Helvetica;fontSize=11;html=1;">
          <mxGeometry x="0" y="0" width="140" height="170" as="geometry"/>
        </mxCell>
        <mxCell id="dl" value="DL Inference" vertex="1" parent="bs"
          style="rounded=0;whiteSpace=wrap;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Helvetica;fontSize=11;html=1;">
          <mxGeometry x="20" y="120" width="100" height="30" as="geometry"/>
        </mxCell>
        <!-- an edge attached to its ends: it follows when a box moves -->
        <mxCell id="e1" value="Result" edge="1" parent="1" source="dl" target="fix"
          style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;endFill=1;endSize=4;strokeColor=#000000;fontFamily=Helvetica;fontSize=10;labelBackgroundColor=#FFFFFF;html=1;">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- **Attach every edge** with `source` and `target`. An edge given only as
  points does not follow its boxes, and that defeats the purpose of the file.
- **Containers** (`container=1`) hold the members of a group. Children use
  coordinates relative to the container, so the group moves as one.
- **Set the style explicitly on every cell**: `fontFamily`, `fontSize`,
  `fillColor`, `strokeColor`. The editor's defaults (light blue `#DAE8FC`,
  orange `#FFE6CC`, Helvetica 12) look generated.
- **Put cells on the grid** (`gridSize` 5), with equal gaps between siblings.
  Use `edgeStyle=orthogonalEdgeStyle`, and set `exitX/exitY/entryX/entryY`
  when an edge must leave or enter at a given side.
- **Flipped shapes** (`flipH=1`, `flipV=1`) mirror their connection points, so
  an edge attached to "the right side" lands on the left. Prefer a rotation
  or a separate shape, or set `exitX/exitY` explicitly. Check the wiring in
  the render.
- **Dashed and emphasised lines**: `dashed=1`, `strokeWidth=1.5`.
- **Notation**: set `math="1"` on `mxGraphModel`, and write `\(q_{10}^{(i-1)}\)`
  in labels. The editor typesets them with MathJax. Look at the export,
  because MathJax output varies.
- **Generated from data**: a script can write the `.drawio` file (for example
  one node per stage in a list). After a person edits the file by hand, the file
  is the source. Do not regenerate it and lose their edits. Change it in
  place instead.

## Export and look

Export with the desktop application's command line. The app is `drawio` on
Linux and Windows, and `/Applications/draw.io.app/Contents/MacOS/draw.io`
on macOS:

```sh
drawio -x -f pdf --crop -o figures/system.pdf figures/system.drawio
drawio -x -f png -s 4 -o figures/system.png figures/system.drawio
```

- `--crop` makes the PDF page the size of the diagram.
- `-f svg --embed-diagram` (or `-e`) writes an SVG that opens again in draw.io
  as an editable diagram.
- Labels with `html=1` become `<foreignObject>` in SVG exports, and LaTeX
  drops them. Deliver the PDF, or set `html=0` on cells whose SVG will be
  used.
- On a headless Linux machine, the export needs a virtual display:
  `xvfb-run -a drawio -x ...`.

If the application is not installed, say so and give the install command
(`brew install --cask drawio`, or the package from the draw.io releases
page). Installing is the user's call. Without it, deliver the `.drawio`
file and say that it was not rendered or looked at.

**Size.** draw.io units are screen pixels. In the exported PDF one unit is
about 0.72–0.75 pt, so `fontSize=11` prints at about 8 pt, and a diagram
about 340 units wide fills a 3.5 in (252 pt) column. Plan the geometry at that
scale. Then measure the exported PDF with `check_figure.py --width single`.
If the width is wrong, scale all geometry and font sizes by the same factor,
and check again. Do not let LaTeX rescale the figure: its text would change
size.
