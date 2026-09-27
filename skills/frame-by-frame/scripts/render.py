#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.45"]
# ///
"""Render an HTML page that exposes window.seek(t) to stills, contact sheets and video.

    uv run render.py check  page.html [--loop]
    uv run render.py sheet  page.html sheet.png [--at 0,1.5,3 | --n 9]
    uv run render.py still  page.html out.png --at 2.5 [--scale 2]
    uv run render.py video  page.html out.mp4|.webm|.mov|.gif|frames/%05d.png

The page contract: window.seek(t) draws the frame at t seconds from t alone;
window.DURATION is the length in seconds (absent or 0 for a still); an optional
window.READY promise is awaited before the first frame; the frame
is the element #stage, or the viewport when there is none. The page is opened
with ?render appended so it can skip its own preview loop.

Before page scripts run, Date, performance.now and requestAnimationFrame are
replaced with a clock this script sets, and Math.random is seeded from the
frame time, so frames are repeatable even where a page reads the clock.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

CLOCK = r"""
(() => {
  const EPOCH = 1767225600000; // 2026-01-01T00:00:00Z
  let now = 0;
  let seed = 0x6d2b79f5;
  const RealDate = Date;
  function VDate(...a) {
    if (!new.target) return new RealDate(EPOCH + now).toString();
    return a.length ? new RealDate(...a) : new RealDate(EPOCH + now);
  }
  VDate.prototype = RealDate.prototype;
  VDate.now = () => EPOCH + now;
  VDate.parse = RealDate.parse;
  VDate.UTC = RealDate.UTC;
  window.Date = VDate;
  performance.now = () => now;
  const queue = new Map();
  let next = 1;
  window.requestAnimationFrame = (cb) => { queue.set(next, cb); return next++; };
  window.cancelAnimationFrame = (id) => { queue.delete(id); };
  Math.random = () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let x = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
  window.__fbf = {
    async go(t) {
      now = t * 1000;
      seed = (Math.round(t * 1e6) ^ 0x6d2b79f5) | 0;
      for (const a of document.getAnimations()) { a.pause(); a.currentTime = now; }
      for (const svg of document.querySelectorAll('svg')) {
        if (!svg.ownerSVGElement && svg.pauseAnimations) { svg.pauseAnimations(); svg.setCurrentTime(t); }
      }
      if (typeof window.seek === 'function') {
        try { await window.seek(t); } catch (e) { console.error(`seek(${t}) threw: ${e && e.stack || e}`); }
      }
      for (let round = 0; round < 4 && queue.size; round++) {
        const due = [...queue.values()];
        queue.clear();
        for (const cb of due) cb(now);
      }
    },
  };
})();
"""

INFO = r"""
async () => {
  if (window.READY) await window.READY;
  const faces = [...document.fonts];
  await Promise.all(faces.map((f) => f.load().catch(() => null)));
  await document.fonts.ready;
  const stage = document.getElementById('stage');
  const box = stage ? stage.getBoundingClientRect() : null;
  return {
    duration: Number(window.DURATION) || 0,
    hasSeek: typeof window.seek === 'function',
    width: Math.round(box ? box.width : window.innerWidth),
    height: Math.round(box ? box.height : window.innerHeight),
    x: box ? box.left + scrollX : 0,
    y: box ? box.top + scrollY : 0,
    faces: faces.map((f) => ({ family: f.family.replace(/^["']|["']$/g, ''), status: f.status })),
  };
}
"""

# Families named in CSS that are neither declared with @font-face nor installed:
# the text then renders in a fallback that differs between machines.
FONTS = r"""
() => {
  const generic = new Set(['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui',
    'ui-serif', 'ui-sans-serif', 'ui-monospace', 'ui-rounded', 'emoji', 'math', 'fangsong',
    'inherit', 'initial', 'unset', '-apple-system', 'blinkmacsystemfont']);
  const declared = new Set([...document.fonts].map((f) => f.family.replace(/^["']|["']$/g, '').toLowerCase()));
  const ctx = document.createElement('canvas').getContext('2d');
  const width = (font) => { ctx.font = font; return ctx.measureText('mmmmmmmmmmlli WQ@#0123').width; };
  const installed = (fam) => ['monospace', 'serif'].some((g) => width(`40px "${fam}", ${g}`) !== width(`40px ${g}`));
  const missing = new Set();
  for (const el of document.querySelectorAll('body *')) {
    if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    const first = getComputedStyle(el).fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
    const key = first.toLowerCase();
    if (!first || generic.has(key) || declared.has(key)) continue;
    if (!installed(first)) missing.add(first);
  }
  return [...missing];
}
"""

# Text that is clipped by its own box or reaches outside the frame, among
# elements that are actually visible at this time.
LAYOUT = r"""
([x, y, w, h]) => {
  const out = [];
  const visible = (el) => {
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) < 0.05) return false;
    }
    return true;
  };
  const name = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (el.classList.length ? '.' + [...el.classList].join('.') : '');
  for (const el of document.querySelectorAll('body *')) {
    const text = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join('').trim();
    if (!text || !visible(el)) continue;
    const r = el.getBoundingClientRect();
    const label = `${name(el)} "${text.slice(0, 40)}"`;
    // Glyphs overhang a tight line-height by a few pixels; a spilled line is ~1em.
    const cs = getComputedStyle(el), em = parseFloat(cs.fontSize);
    const overflows = el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + em / 2;
    if (overflows && cs.display !== 'inline') out.push(`text overflows its box: ${label}`);
    if (r.width && (r.left < x - 1 || r.top < y - 1 || r.right > x + w + 1 || r.bottom > y + h + 1))
      out.push(`text reaches outside the frame: ${label}`);
  }
  return out;
}
"""

# Mean absolute difference, in percent of full scale, between pairs of PNGs,
# measured on greyscale thumbnails so that noise and antialiasing barely count.
DIFF = r"""
async ([urls, pairs]) => {
  const load = (u) => new Promise((ok, bad) => { const i = new Image(); i.onload = () => ok(i); i.onerror = bad; i.src = u; });
  const imgs = await Promise.all(urls.map(load));
  const W = 160, H = Math.max(1, Math.round(160 * imgs[0].height / imgs[0].width));
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const ctx = c.getContext('2d', { willReadFrequently: true });
  const grey = imgs.map((img) => {
    ctx.clearRect(0, 0, W, H); ctx.drawImage(img, 0, 0, W, H);
    const d = ctx.getImageData(0, 0, W, H).data, g = new Float32Array(W * H);
    for (let i = 0; i < g.length; i++) g[i] = (0.2126 * d[4 * i] + 0.7152 * d[4 * i + 1] + 0.0722 * d[4 * i + 2]) * d[4 * i + 3] / 255;
    return g;
  });
  return pairs.map(([a, b]) => {
    let s = 0; for (let i = 0; i < grey[a].length; i++) s += Math.abs(grey[a][i] - grey[b][i]);
    return 100 * s / grey[a].length / 255;
  });
}
"""

SHEET = """<!doctype html><meta charset="utf-8"><style>
body{{margin:0;background:#1b1b1f;font:14px/1.2 ui-monospace,Menlo,monospace;color:#e6e6e6}}
.g{{display:grid;grid-template-columns:repeat({cols},{tile}px);gap:10px;padding:10px}}
figure{{margin:0}} img{{display:block;width:{tile}px;background:
repeating-conic-gradient(#3a3a40 0 25%,#2a2a2e 0 50%) 0 0/16px 16px}}
figcaption{{padding:4px 2px}}</style><div class="g">{cells}</div>"""


class Page:
    """A browser page holding the composition, with errors and requests recorded."""

    def __init__(self, pw, args, html: Path):
        self.seen: dict[str, list] = {}
        self.remote: list[str] = []
        try:
            self.browser = pw.chromium.launch(
                channel=args.channel or None,
                args=[
                    "--force-color-profile=srgb",
                    "--font-render-hinting=none",
                    "--hide-scrollbars",
                    "--enable-unsafe-swiftshader",
                ],
            )
        except Exception as e:  # noqa: BLE001 - Playwright raises its own Error types
            sys.exit(
                f"cannot start Chromium: {str(e).splitlines()[0]}\n"
                "install it with `uv run --with playwright playwright install chromium`, "
                "or pass --channel chrome to use an installed Google Chrome"
            )
        self.ctx = self.browser.new_context(device_scale_factor=args.scale)
        self.ctx.add_init_script(CLOCK)
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.error(f"page error: {e}"))
        self.page.on(
            "console",
            lambda m: m.type == "error" and self.error(f"console error: {m.text}"),
        )
        self.page.on(
            "requestfailed",
            lambda r: self.error(f"request failed: {r.url} ({r.failure})"),
        )
        self.page.on(
            "request",
            lambda r: (
                r.url.startswith(("http:", "https:")) and self.remote.append(r.url)
            ),
        )
        size = (
            [int(v) for v in args.size.lower().split("x")]
            if args.size
            else [1920, 1080]
        )
        self.page.set_viewport_size({"width": size[0], "height": size[1]})
        self.page.goto(html.resolve().as_uri() + "?render", wait_until="load")
        self.info = self.page.evaluate(INFO)
        if not args.size and self.info["width"] and self.info["height"]:
            # Fit the viewport to the stage, then measure again in case layout moved.
            self.page.set_viewport_size(
                {
                    "width": int(self.info["x"] + self.info["width"]),
                    "height": int(self.info["y"] + self.info["height"]),
                }
            )
            self.info = self.page.evaluate(INFO)
        self.clip = {k: self.info[k] for k in ("x", "y", "width", "height")}

    def error(self, message: str):
        # One line per distinct error; a seek that throws on every frame is one error.
        line = message.strip().splitlines()[0]
        key = re.sub(r"seek\([-\d.e]+\)", "seek(t)", line)
        self.seen.setdefault(key, [line, 0])[1] += 1

    @property
    def errors(self) -> list[str]:
        return [line + (f" (x{n})" if n > 1 else "") for line, n in self.seen.values()]

    @property
    def duration(self) -> float:
        return self.info["duration"]

    def shot(self, t: float, alpha: bool = False) -> bytes:
        self.page.evaluate("t => window.__fbf.go(t)", t)
        return self.page.screenshot(
            type="png", clip=self.clip, omit_background=alpha, animations="allow"
        )

    def close(self):
        self.browser.close()


def times(spec: str | None, n: int, duration: float, fps: float) -> list[float]:
    if spec:
        return [float(v) for v in spec.split(",") if v.strip()]
    if duration <= 0:
        return [0.0]
    last = max(0.0, duration - 1 / fps)
    return [round(last * i / max(1, n - 1), 3) for i in range(n)]


def data_url(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode()


def diffs(pw_page, pngs: list[bytes], pairs: list[tuple[int, int]]) -> list[float]:
    return pw_page.evaluate(
        DIFF, [[data_url(p) for p in pngs], [list(p) for p in pairs]]
    )


def sheet_png(page: Page, shots: list[tuple[float, bytes]], cols: int) -> bytes:
    tile = 480 if len(shots) > 1 else 960
    cols = max(1, min(cols, len(shots)))
    cells = "".join(
        f'<figure><img src="{data_url(p)}"><figcaption>t = {t:.2f}s</figcaption></figure>'
        for t, p in shots
    )
    lab = page.ctx.new_page()
    lab.set_viewport_size({"width": cols * (tile + 10) + 10, "height": 200})
    lab.set_content(SHEET.format(cols=cols, tile=tile, cells=cells))
    lab.wait_for_function("[...document.images].every(i => i.complete)")
    png = lab.screenshot(type="png", full_page=True)
    lab.close()
    return png


def cmd_still(page: Page, args) -> int:
    Path(args.out).write_bytes(page.shot(args.at, alpha=args.alpha))
    print(
        f"wrote {args.out} at t={args.at}s ({page.clip['width']}x{page.clip['height']} @{args.scale}x)"
    )
    return report_errors(page)


def cmd_sheet(page: Page, args) -> int:
    ts = times(args.at, args.n, page.duration, args.fps)
    shots = [(t, page.shot(t, alpha=args.alpha)) for t in ts]
    Path(args.out).write_bytes(sheet_png(page, shots, args.cols))
    print(f"wrote {args.out}: {len(ts)} frames at " + ", ".join(f"{t:g}s" for t in ts))
    return report_errors(page)


def cmd_check(page: Page, args) -> int:
    info, fps = page.info, args.fps
    errors, warnings, notes = [], [], []
    if info["duration"] > 0 and not info["hasSeek"]:
        warnings.append(
            "no window.seek(t): only CSS animations, SMIL and requestAnimationFrame follow the clock"
        )
    if not info["width"] or not info["height"]:
        errors.append("the frame has no size: give #stage an explicit width and height")
    for f in info["faces"]:
        if f["status"] != "loaded":
            errors.append(f"@font-face {f['family']!r} did not load ({f['status']})")
    for fam in page.page.evaluate(FONTS):
        errors.append(
            f"font {fam!r} is neither declared with @font-face nor installed; a fallback renders"
        )

    ts = times(args.at, args.n, info["duration"], fps)
    first: dict[float, bytes] = {}
    layout: dict[str, list[float]] = {}
    for t in ts:
        first[t] = page.shot(t)
        for problem in page.page.evaluate(LAYOUT, list(page.clip.values())):
            layout.setdefault(problem, []).append(t)
    for problem, at in layout.items():
        warnings.append(f"{problem} at t={', '.join(f'{t:g}' for t in at)}")

    if info["duration"] > 0:
        # Revisit in reverse order: a pure seek(t) paints the same pixels again.
        impure = [
            t
            for t in reversed(ts)
            if hashlib.sha1(page.shot(t)).digest() != hashlib.sha1(first[t]).digest()
        ]
        if impure:
            errors.append(
                "seek(t) is not a pure function of t: frames differ on a second visit at t="
                + ", ".join(f"{t:g}" for t in sorted(impure))
                + ". If the difference is only at text edges, give elements whose opacity or"
                " transform changes `will-change: transform, opacity`; otherwise look for state"
                " kept between calls"
            )
        if len({hashlib.sha1(p).digest() for p in first.values()}) == 1 and len(ts) > 1:
            errors.append("every sampled frame is identical: nothing moves")

        # Typical change between consecutive frames, to judge the loop seam against.
        step = 1 / fps
        probe = [t for t in ts if t + step < info["duration"]]
        pngs = [first[t] for t in probe] + [page.shot(t + step) for t in probe]
        moves = (
            diffs(page.page, pngs, [(i, i + len(probe)) for i in range(len(probe))])
            if probe
            else []
        )
        moving = sorted(m for m in moves if m > 0.01)
        typical = moving[len(moving) // 2] if moving else 0.0
        notes.append(
            f"frame-to-frame change: median {typical:.2f}% over {len(probe)} samples"
        )
        if args.loop:
            # The frame after the last one is the first: seek(DURATION) must draw seek(0).
            seam = diffs(
                page.page, [page.shot(info["duration"]), page.shot(0.0)], [(0, 1)]
            )[0]
            limit = max(0.25 * typical, 0.05)
            notes.append(
                f"loop seam, seek(DURATION) vs seek(0): {seam:.3f}%, limit {limit:.3f}%"
            )
            if seam > limit:
                errors.append(
                    f"the loop jumps: seek({info['duration']:g}) differs from seek(0) by {seam:.2f}%"
                    f" (a typical frame step is {typical:.2f}%)"
                )

    if page.remote:
        warnings.append(
            f"{len(page.remote)} network requests, e.g. {page.remote[0]}: embed assets instead"
        )
    errors += page.errors

    result = {
        "frame": f"{info['width']}x{info['height']}",
        "duration": info["duration"],
        "sampled": ts,
        "errors": errors,
        "warnings": warnings,
        "notes": notes,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"frame {result['frame']}, duration {info['duration']:g}s, sampled {len(ts)} times"
        )
        for label, items in (("error", errors), ("warning", warnings), ("note", notes)):
            for item in items:
                print(f"{label}: {item}")
        print("check: " + ("FAIL" if errors else "pass"))
    return 1 if errors else 0


def encoder(
    out: str, alpha: bool, crf: int | None, dither: str
) -> tuple[list[str], list[str]]:
    """Filters and output options for the container implied by the file name."""
    ext = Path(out).suffix.lower()
    if "%" in out and ext == ".png":
        return [], ["-c:v", "png"]
    if ext == ".mp4":
        if alpha:
            sys.exit(
                "MP4 (H.264) has no alpha channel: use .mov (ProRes 4444) or .webm (VP9)"
            )
        return (
            ["scale=out_color_matrix=bt709:out_range=tv", "format=yuv420p"],
            [
                "-c:v",
                "libx264",
                "-crf",
                str(crf or 17),
                "-preset",
                "slow",
                "-movflags",
                "+faststart",
            ]
            + [
                "-colorspace",
                "bt709",
                "-color_primaries",
                "bt709",
                "-color_trc",
                "bt709",
                "-color_range",
                "tv",
            ],
        )
    if ext == ".webm":
        fmt = "yuva420p" if alpha else "yuv420p"
        return [f"format={fmt}"], [
            "-c:v",
            "libvpx-vp9",
            "-crf",
            str(crf or 30),
            "-b:v",
            "0",
            "-row-mt",
            "1",
        ]
    if ext == ".mov":
        if alpha:
            return ["format=yuva444p10le"], [
                "-c:v",
                "prores_ks",
                "-profile:v",
                "4",
                "-vendor",
                "apl0",
            ]
        return ["format=yuv422p10le"], [
            "-c:v",
            "prores_ks",
            "-profile:v",
            "3",
            "-vendor",
            "apl0",
        ]
    if ext == ".gif":
        use = f"paletteuse=dither={dither}" + (":alpha_threshold=128" if alpha else "")
        return [f"split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]{use}"], [
            "-loop",
            "0",
        ]
    sys.exit(
        f"unsupported output {out!r}: use .mp4, .webm, .mov, .gif or a frames/%05d.png pattern"
    )


def probe(out: str) -> dict:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets"]
        + [
            "-show_entries",
            "stream=codec_name,width,height,pix_fmt,nb_read_packets:format=duration",
        ]
        + ["-of", "json", out],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode:
        sys.exit(f"ffprobe could not read {out}: {res.stderr.strip()}")
    data = json.loads(res.stdout)
    return {**data["streams"][0], **data.get("format", {})}


def cmd_video(page: Page, args) -> int:
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is not on PATH; it is needed to encode video")
    if page.duration <= 0:
        sys.exit("window.DURATION is 0: this page is a still; use `still` instead")
    fps, k = args.fps, max(1, args.blur)
    w, h = (
        round(page.clip["width"] * args.scale),
        round(page.clip["height"] * args.scale),
    )
    ext = Path(args.out).suffix.lower()
    if ext in (".mp4", ".webm", ".mov") and (w % 2 or h % 2):
        sys.exit(f"{w}x{h}: {ext} needs an even width and height; resize #stage")
    frames = round(page.duration * fps)

    chain = ["format=gbrap" if args.alpha else "format=gbrp"]
    if k > 1:
        # k samples across a 180-degree shutter, averaged into one frame.
        chain += [
            f"tmix=frames={k}",
            f"select=eq(mod(n\\,{k})\\,{k - 1})",
            f"setpts=N/({fps})/TB",
        ]
    filters, opts = encoder(args.out, args.alpha, args.crf, args.dither)
    vf = ",".join(chain + filters)
    if Path(args.out).parent:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "image2pipe",
        "-framerate",
        str(fps * k),
        "-c:v",
        "png",
    ]
    cmd += ["-i", "-"]
    if args.audio:
        cmd += ["-i", args.audio]
    cmd += (
        (["-filter_complex", vf] if "[" in vf else ["-vf", vf])
        + ["-r", str(fps)]
        + opts
    )
    if args.audio:
        cmd += ["-c:a", "libopus" if ext == ".webm" else "aac", "-shortest"]
    cmd.append(args.out)

    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    shutter = 0.5 / fps
    try:
        for f in range(frames):
            for s in range(k):
                t = f / fps + (s - (k - 1) / 2) * shutter / k if k > 1 else f / fps
                ff.stdin.write(
                    page.shot(min(max(t, 0.0), page.duration), alpha=args.alpha)
                )
            if f % max(1, frames // 10) == 0:
                print(f"\rframe {f + 1}/{frames}", end="", file=sys.stderr, flush=True)
    except BrokenPipeError:
        pass
    ff.stdin.close()
    if ff.wait():
        return ff.returncode
    print(f"\rframe {frames}/{frames}", file=sys.stderr)

    if "%" in args.out:
        print(f"wrote {frames} frames to {args.out}")
        return report_errors(page)
    got = probe(args.out)
    problems = []
    if (int(got["width"]), int(got["height"])) != (w, h):
        problems.append(f"size {got['width']}x{got['height']}, expected {w}x{h}")
    if abs(float(got.get("duration", 0)) - page.duration) > 1.5 / fps:
        problems.append(f"duration {got.get('duration')}s, expected {page.duration}s")
    if int(got.get("nb_read_packets", frames)) != frames:
        problems.append(f"{got.get('nb_read_packets')} frames, expected {frames}")
    print(
        f"wrote {args.out}: {got['codec_name']} {got['width']}x{got['height']} {got.get('pix_fmt')} "
        f"{float(got.get('duration', 0)):.3f}s {got.get('nb_read_packets')} frames"
    )
    for p in problems:
        print(f"error: {p}")
    return max(1 if problems else 0, report_errors(page))


def report_errors(page: Page) -> int:
    for e in page.errors:
        print(f"error: {e}")
    return 1 if page.errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("html", type=Path)
    common.add_argument("--fps", type=float, default=30)
    common.add_argument(
        "--scale",
        type=float,
        default=1,
        help="device pixel ratio; 2 renders at double resolution",
    )
    common.add_argument(
        "--size", help="viewport WxH when the page has no #stage (default 1920x1080)"
    )
    common.add_argument(
        "--channel", help="browser channel, e.g. chrome, to use an installed browser"
    )
    common.add_argument(
        "--alpha",
        action="store_true",
        help="keep transparency (needs a transparent background)",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser(
        "check", parents=[common], help="sample the page and report defects"
    )
    p.add_argument(
        "--at", help="comma-separated times to sample instead of --n even samples"
    )
    p.add_argument("--n", type=int, default=12)
    p.add_argument(
        "--loop",
        action="store_true",
        help="also check that the last frame flows into the first",
    )
    p.add_argument("--json", action="store_true")

    p = sub.add_parser(
        "sheet", parents=[common], help="write a labelled contact sheet of frames"
    )
    p.add_argument("out")
    p.add_argument("--at", help="comma-separated times, e.g. the brief's beats")
    p.add_argument("--n", type=int, default=9)
    p.add_argument("--cols", type=int, default=3)

    p = sub.add_parser("still", parents=[common], help="write one frame as PNG")
    p.add_argument("out")
    p.add_argument("--at", type=float, default=0.0)

    p = sub.add_parser("video", parents=[common], help="encode every frame with ffmpeg")
    p.add_argument("out", help=".mp4, .webm, .mov, .gif, or a frames/%%05d.png pattern")
    p.add_argument(
        "--blur",
        type=int,
        default=1,
        help="motion-blur samples per frame (1 = off; 4-8 typical)",
    )
    p.add_argument(
        "--crf", type=int, help="quality for mp4 (default 17) and webm (default 30)"
    )
    p.add_argument(
        "--dither",
        default="sierra2_4a",
        help="GIF dither: none for flat colour, sierra2_4a for gradients",
    )
    p.add_argument("--audio", help="audio file to mux into mp4, webm or mov")

    args = ap.parse_args()
    if not args.html.is_file():
        sys.exit(f"no such file: {args.html}")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "playwright is not installed: run this script with `uv run`, or `pip install playwright` in a venv"
        )

    with sync_playwright() as pw:
        page = Page(pw, args, args.html)
        run = {
            "check": cmd_check,
            "sheet": cmd_sheet,
            "still": cmd_still,
            "video": cmd_video,
        }[args.cmd]
        try:
            return run(page, args)
        finally:
            page.close()


if __name__ == "__main__":
    sys.exit(main())
