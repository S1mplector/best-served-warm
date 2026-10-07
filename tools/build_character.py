"""Normalize generated waist-up characters onto the shared 160x160 pixel canvas."""
import argparse
from collections import deque
from pathlib import Path
from PIL import Image, ImageFilter

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--preview', type=Path)
parser.add_argument('--crop-bottom', type=int, help='Crop source at this waist-line pixel before resizing')
parser.add_argument('--pixel-clusters', action='store_true', help='Simplify texture and use 16 flat colors on the native 160x160 canvas')
parser.add_argument('--remove-white-background', action='store_true', help='Make near-white background pixels connected to the canvas edge transparent')
args = parser.parse_args()
source = Image.open(args.source).convert('RGBA')
if args.crop_bottom is not None:
    if not 0 < args.crop_bottom <= source.height:
        raise ValueError('Crop bottom must fall inside source image')
    source = source.crop((0, 0, source.width, args.crop_bottom))
if args.remove_white_background:
    pixels = source.load()
    width, height = source.size
    pending = deque((x, y) for x in range(width) for y in (0, height - 1))
    pending.extend((x, y) for y in range(height) for x in (0, width - 1))
    visited: set[tuple[int, int]] = set()
    while pending:
        x, y = pending.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        r, g, b, alpha = pixels[x, y]
        if alpha < 128 or min(r, g, b) < 235 or max(r, g, b) - min(r, g, b) > 24:
            continue
        pixels[x, y] = (r, g, b, 0)
        pending.extend((nx, ny) for nx, ny in
                       ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                       if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited)
    # Some illustrations enclose matte-white gaps (for example, between an
    # arm and the torso). Clear exact near-white pixels there as well; warm
    # cream highlights stay because they are not neutral white.
    for y in range(height):
        for x in range(width):
            r, g, b, alpha = pixels[x, y]
            if alpha and min(r, g, b) >= 245 and max(r, g, b) - min(r, g, b) <= 12:
                pixels[x, y] = (r, g, b, 0)
# Ignore faint edge pixels when finding the subject. Keep a hard alpha mask.
alpha = source.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
source.putalpha(alpha)
bounds = alpha.getbbox()
if not bounds:
    raise ValueError('Source contains no visible character')
subject = source.crop(bounds)
if args.pixel_clusters:
    subject = subject.filter(ImageFilter.MedianFilter(7))
extent = 150
scale = min(extent / subject.width, extent / subject.height)
subject = subject.resize((max(1, round(subject.width * scale)),
                          max(1, round(subject.height * scale))), Image.Resampling.NEAREST)
mask = subject.getchannel('A')
# Compact cel-shading palette, no dithering or smoothing.
subject = subject.convert('RGB').quantize(colors=16 if args.pixel_clusters else 32, dither=Image.Dither.NONE).convert('RGBA')
subject.putalpha(mask)
canvas = Image.new('RGBA', (160, 160))
canvas.alpha_composite(subject, ((160 - subject.width) // 2, 155 - subject.height))
args.output.parent.mkdir(parents=True, exist_ok=True)
canvas.save(args.output)
if args.preview:
    args.preview.parent.mkdir(parents=True, exist_ok=True)
    canvas.resize((640, 640), Image.Resampling.NEAREST).save(args.preview)
