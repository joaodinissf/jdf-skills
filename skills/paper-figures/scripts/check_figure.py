# /// script
# requires-python = ">=3.10"
# dependencies = ["pdfplumber>=0.11", "pypdf>=4", "pypdfium2>=4"]
# ///
"""Audit a figure file before it goes into a paper.

    uv run check_figure.py figure.pdf [--width single|double|INCHES] [--venue ieee|acm]
                                      [--png preview.png] [--grey preview-grey.png]
    uv run check_figure.py figure.svg

For a PDF it reports the page size against the column width, fonts that are
not embedded or are Type 3, the smallest text size, fill colours that are
hard to tell apart in greyscale, and text with low contrast on its fill.
--png and --grey render previews to look at; --grey shows the figure as a
black-and-white printer would.

For an SVG it reports the size and text held in <foreignObject>, which most
LaTeX pipelines and vector editors drop.

Exit status: 0 when there are no errors (warnings allowed), 1 otherwise.
"""

import argparse
import itertools
import re
import sys
from pathlib import Path

WIDTHS_IN = {
    "ieee": {"single": 3.5, "double": 7.16},
    "acm": {"single": 3.33, "double": 7.0},
}
MIN_TEXT_PT = 6.0
MIN_DELTA_L = 15.0
MIN_TEXT_CONTRAST = 4.5


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb_of(color):
    """pdfplumber colour (grey, RGB or CMYK tuple) to an sRGB triple in 0..1, or None."""
    if color is None:
        return None
    if isinstance(color, (int, float)):
        color = (color,)
    color = tuple(float(v) for v in color if isinstance(v, (int, float)))
    if len(color) == 1:
        return (color[0],) * 3
    if len(color) == 3:
        return color
    if len(color) == 4:
        c, m, y, k = color
        return ((1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k))
    return None


def luminance(rgb):
    r, g, b = (srgb_to_linear(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def lightness(rgb):
    """CIE L* (0 black .. 100 white) from relative luminance."""
    y = luminance(rgb)
    return 116 * y ** (1 / 3) - 16 if y > 216 / 24389 else y * 24389 / 27


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hexof(rgb):
    return "#" + "".join(f"{round(v * 255):02X}" for v in rgb)


def target_width(width, venue):
    if width is None:
        return None
    try:
        return float(width)
    except ValueError:
        return WIDTHS_IN[venue][width]


def check_fonts(path, errors, warnings):
    from pypdf import PdfReader

    seen = {}
    for page in PdfReader(path).pages:
        fonts = (page.get("/Resources") or {}).get("/Font") or {}
        for ref in fonts.values():
            font = ref.get_object()
            name = str(font.get("/BaseFont", "?")).lstrip("/")
            subtype = str(font.get("/Subtype", ""))
            desc = font.get("/FontDescriptor")
            if desc is None and "/DescendantFonts" in font:
                desc = font["/DescendantFonts"][0].get_object().get("/FontDescriptor")
            desc = desc.get_object() if desc is not None else {}
            embedded = any(k in desc for k in ("/FontFile", "/FontFile2", "/FontFile3"))
            seen[name] = (subtype, embedded)
    for name, (subtype, embedded) in sorted(seen.items()):
        if subtype == "/Type3":
            warnings.append(
                f"font {name} is Type 3 (bitmap-like; set pdf.fonttype 42 in matplotlib)"
            )
        elif not embedded:
            errors.append(f"font {name} is not embedded")
    return seen


def check_pdf(args):
    import pdfplumber

    errors, warnings, notes = [], [], []
    with pdfplumber.open(args.file) as pdf:
        if len(pdf.pages) != 1:
            warnings.append(f"{len(pdf.pages)} pages; a figure is usually one page")
        page = pdf.pages[0]
        w_in, h_in = page.width / 72, page.height / 72
        notes.append(
            f"page {w_in:.2f} x {h_in:.2f} in ({page.width:.0f} x {page.height:.0f} pt)"
        )

        target = target_width(args.width, args.venue)
        if target:
            if w_in > target * 1.02:
                errors.append(
                    f"wider than the target {target:.2f} in: LaTeX will shrink it and its text"
                )
            elif w_in < target * 0.9:
                warnings.append(
                    f"narrower than the target {target:.2f} in: fine if intended, "
                    f"but text scales up if it is included at full width"
                )

        # Rotated glyphs report their advance as height; measure them across.
        sizes = [
            c["size"] if c.get("upright", True) else c["x1"] - c["x0"]
            for c in page.chars
            if c.get("text", "").strip()
        ]
        if sizes:
            smallest = min(sizes)
            notes.append(f"text sizes {smallest:.1f}-{max(sizes):.1f} pt")
            if smallest < MIN_TEXT_PT:
                warnings.append(
                    f"smallest text is {smallest:.1f} pt (below {MIN_TEXT_PT} pt at print size)"
                )
        else:
            notes.append("no text found (text may be outlined as paths)")

        fills = {}
        rects = []
        patterns = set()
        for obj in page.rects + page.curves:
            if not obj.get("fill"):
                continue
            rgb = rgb_of(obj.get("non_stroking_color"))
            if rgb is None:
                patterns.add(str(obj.get("non_stroking_color")))
                continue
            key = hexof(rgb)
            fills[key] = rgb
            rects.append((obj["x0"], obj["top"], obj["x1"], obj["bottom"], rgb))

        if patterns:
            notes.append(
                f"{len(patterns)} pattern fills (hatches) not audited by colour; look at --grey"
            )
        coloured = sorted(
            (
                (lightness(rgb), key)
                for key, rgb in fills.items()
                if lightness(rgb) < 97
            ),
        )
        if coloured:
            notes.append(
                "fills by L*: " + ", ".join(f"{k} {l:.0f}" for l, k in coloured)
            )
        for (l1, k1), (l2, k2) in itertools.pairwise(coloured):
            if l2 - l1 < MIN_DELTA_L and k1 != k2:
                warnings.append(
                    f"fills {k1} and {k2} differ by only {l2 - l1:.0f} L*: "
                    f"hard to tell apart in greyscale; add a hatch or change lightness"
                )

        low = set()
        for ch in page.chars:
            if not ch.get("text", "").strip():
                continue
            ink = rgb_of(ch.get("non_stroking_color")) or (0, 0, 0)
            cx, cy = (ch["x0"] + ch["x1"]) / 2, (ch["top"] + ch["bottom"]) / 2
            under = [r for r in rects if r[0] <= cx <= r[2] and r[1] <= cy <= r[3]]
            if not under:
                continue
            fill = min(under, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))[4]
            if contrast(ink, fill) < MIN_TEXT_CONTRAST:
                low.add((hexof(ink), hexof(fill), round(contrast(ink, fill), 1)))
        for ink, fill, c in sorted(low):
            warnings.append(
                f"text {ink} on fill {fill} has contrast {c}:1 (below {MIN_TEXT_CONTRAST}:1)"
            )

    fonts = check_fonts(args.file, errors, warnings)
    if fonts:
        notes.append("fonts: " + ", ".join(sorted(fonts)))

    if args.png or args.grey:
        import pypdfium2 as pdfium

        image = pdfium.PdfDocument(args.file)[0].render(scale=300 / 72).to_pil()
        if args.png:
            image.save(args.png)
            notes.append(f"wrote {args.png}")
        if args.grey:
            image.convert("L").save(args.grey)
            notes.append(f"wrote {args.grey}")
    return errors, warnings, notes


def check_svg(args):
    errors, warnings, notes = [], [], []
    text = Path(args.file).read_text(errors="replace")
    head = re.search(r"<svg\b[^>]*>", text)
    if head:
        dims = re.findall(r'\b(width|height|viewBox)="([^"]+)"', head.group(0))
        notes.append("svg " + ", ".join(f"{k}={v}" for k, v in dims))
    if "<foreignObject" in text:
        errors.append(
            "text is held in <foreignObject> (HTML); LaTeX and vector editors usually drop it. "
            "Export a PDF instead, or disable HTML labels"
        )
    if "<text" not in text and "<foreignObject" not in text:
        notes.append(
            "no <text> elements: text is outlined as paths and cannot be edited"
        )
    return errors, warnings, notes


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("file")
    ap.add_argument("--width", help='"single", "double" or inches')
    ap.add_argument("--venue", default="ieee", choices=sorted(WIDTHS_IN))
    ap.add_argument("--png", help="write a 300 dpi preview")
    ap.add_argument("--grey", help="write a 300 dpi greyscale preview")
    args = ap.parse_args()

    if not Path(args.file).is_file():
        sys.exit(f"no such file: {args.file}")
    suffix = Path(args.file).suffix.lower()
    if suffix == ".pdf":
        errors, warnings, notes = check_pdf(args)
    elif suffix == ".svg":
        errors, warnings, notes = check_svg(args)
    else:
        sys.exit(f"unsupported file type {suffix}; give a .pdf or .svg")

    for n in notes:
        print(f"note: {n}")
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print("check: " + ("fail" if errors else "pass"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
