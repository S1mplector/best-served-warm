"""Normalize generated waist-up characters onto the shared 160x160 pixel canvas."""
import argparse
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--preview', type=Path)
parser.add_argument('--crop-bottom', type=int, help='Crop source at this waist-line pixel before resizing')
args = parser.parse_args()
source = Image.open(args.source).convert('RGBA')
if args.crop_bottom is not None:
    if not 0 < args.crop_bottom <= source.height:
        raise ValueError('Crop bottom must fall inside source image')
    source = source.crop((0, 0, source.width, args.crop_bottom))
# Ignore faint edge pixels when finding the subject. Keep a hard alpha mask.
alpha = source.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
source.putalpha(alpha)
bounds = alpha.getbbox()
if not bounds:
    raise ValueError('Source contains no visible character')
subject = source.crop(bounds)
scale = min(150 / subject.width, 150 / subject.height)
subject = subject.resize((max(1, round(subject.width * scale)),
                          max(1, round(subject.height * scale))), Image.Resampling.NEAREST)
mask = subject.getchannel('A')
# Compact cel-shading palette, no dithering or smoothing.
subject = subject.convert('RGB').quantize(colors=32, dither=Image.Dither.NONE).convert('RGBA')
subject.putalpha(mask)
canvas = Image.new('RGBA', (160, 160))
canvas.alpha_composite(subject, ((160 - subject.width) // 2, 155 - subject.height))
args.output.parent.mkdir(parents=True, exist_ok=True)
canvas.save(args.output)
if args.preview:
    args.preview.parent.mkdir(parents=True, exist_ok=True)
    canvas.resize((640, 640), Image.Resampling.NEAREST).save(args.preview)
