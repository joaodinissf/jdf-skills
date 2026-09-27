# Output

## Choosing a format

| Destination | Format | `render.py` | Notes |
|---|---|---|---|
| Sharing, social, slides, the web | MP4 (H.264) | `video out.mp4` | CRF 17, `yuv420p`, BT.709, `+faststart`. The frame needs an even width and height. |
| Web with transparency | WebM (VP9) | `video out.webm --alpha` | Plays in browsers; ffprobe reports `yuv420p` with an `alpha_mode=1` tag. |
| Compositing in an editor | MOV (ProRes 4444) | `video out.mov --alpha` | Large, lossless in practice; opens in video editors. Without `--alpha` it is ProRes 422 HQ. |
| README, docs, chat, email | GIF | `video out.gif --fps 15` | See below. |
| Further processing | PNG sequence | `video 'frames/%05d.png'` | One PNG per frame. |
| Still image | PNG | `still out.png --at T --scale 2` | Twice the resolution makes it sharp on high-density screens. |
| Vector image | SVG | — | Write the SVG itself. Render it with `still` to look at it. |

`--alpha` needs a transparent `#stage` and page background. Check the
result against both a light and a dark background: a `sheet` shows alpha
over a checkerboard.

## Frame sizes

| Use | Size | Safe area for text |
|---|---|---|
| Landscape video, slides | 1920×1080 | 120 px sides, 100 px top and bottom |
| Square post | 1080×1080 | 80 px all round |
| Portrait post | 1080×1350 | 80 px all round |
| Vertical story, reel, short | 1080×1920 | about 250 px top, 400 px bottom and 120 px right, for platform controls |
| Open Graph / link preview | 1200×630 | 60 px; the centre must survive a square crop |
| README or docs GIF | 800–1200 wide | small text becomes unreadable once it is downscaled |

Frame rate: 30 fps by default. Use 60 fps for fast interface motion or
screen recordings at 60, 24 fps for a film feel, and 12–20 fps for GIFs.

## GIF

- A GIF has 256 colours per frame and 1-bit transparency, and its file size
  grows with the area that changes. The renderer builds one palette from
  the whole clip (`palettegen=stats_mode=diff`) and applies it.
- `--dither none` suits flat colour and interface work: files are smaller,
  there is no crawling noise, and gradients band.
- `--dither sierra2_4a` (the default) suits gradients and photographs. It
  is noisier and makes larger files.
- To keep files small, use:
  - 12–15 fps;
  - a smaller frame;
  - flat backgrounds, with no grain or large gradients;
  - short loops.
- Many viewers show the first frame as the still. Make it a finished,
  readable picture.
- If the size budget matters, check it (`ls -l`) and trade fps and frame
  size before cutting the content.

## Motion blur

`--blur K` renders K samples per frame spread over half the frame's
interval, which is a 180° shutter, and averages them in ffmpeg (`tmix`).
- It costs K times the render time.
- 4 samples is enough for moderate speed and 8 for fast movement.
- It adds nothing to still frames, text holds and slow drift. Leave it off
  for GIFs, where it multiplies the number of colours.

## Audio

`--audio track.m4a` muxes a track into MP4, WebM or MOV, and trims it to the
video (`-shortest`). The method does not compose or time audio: time beats
to the track by choosing `t` values from its known cue points.

## Compositing over footage

Render the graphics with `--alpha` to MOV, then overlay:

```sh
ffmpeg -i footage.mp4 -itsoffset 2 -i graphics.mov \
  -filter_complex "[0][1]overlay=eof_action=pass" \
  -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a copy out.mp4
```

`-itsoffset 2` starts the graphics 2 s into the footage. `eof_action=pass`
shows the footage alone once the graphics end, and the output keeps the
footage's length. For frame-accurate footage inside the page itself, see
[`determinism.md`](determinism.md).

## The gate after encoding

`video` reads the file back with ffprobe. It fails when the width, height,
duration (within 1.5 frames) or frame count differs from what the page
declared. That catches:
- a truncated encode;
- odd dimensions;
- a frame rate that was misapplied.

When a platform requires a particular format, check it with ffprobe too:

```sh
ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,color_space \
  -show_entries format=duration,size -of default=nw=1 out.mp4
```
