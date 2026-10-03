"""Headless, native-resolution pixel art renderer.

JSON projects contain a palette and ordered drawing layers. Every operation
lands on integer pixels; previews use nearest-neighbor enlargement only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw


def render(project: dict, project_dir: Path = Path(".")) -> Image.Image:
    width, height = project["size"]
    if not (1 <= width <= 4096 and 1 <= height <= 4096):
        raise ValueError("size must be between 1 and 4096 pixels per axis")
    palette = {name: ImageColor.getcolor(value, "RGBA") for name, value in project["palette"].items()}
    image = Image.new("RGBA", (width, height), palette.get("background", (0, 0, 0, 0)))
    if "base_image" in project:
        base = Image.open(project_dir / project["base_image"]).convert("RGBA")
        if base.size != image.size:
            raise ValueError(f"base image is {base.size}, expected {image.size}")
        image.alpha_composite(base)
    for layer in project.get("layers", []):
        if not layer.get("visible", True):
            continue
        draw = ImageDraw.Draw(image)
        for item in layer.get("draw", []):
            color = palette[item["color"]]
            kind = item["type"]
            if kind == "pixel":
                draw.point(tuple(item["at"]), fill=color)
            elif kind == "rect":
                x, y, w, h = item["box"]
                if w < 1 or h < 1:
                    raise ValueError("rectangle width and height must be positive")
                draw.rectangle((x, y, x + w - 1, y + h - 1), fill=color)
            elif kind == "line":
                draw.line([tuple(point) for point in item["points"]], fill=color, width=item.get("width", 1))
            elif kind == "ellipse":
                x, y, w, h = item["box"]
                draw.ellipse((x, y, x + w - 1, y + h - 1), fill=color)
            elif kind == "polygon":
                draw.polygon([tuple(point) for point in item["points"]], fill=color)
            else:
                raise ValueError(f"unknown drawing operation: {kind}")
    return image


def main() -> None:
    parser = argparse.ArgumentParser(description="Render editable JSON pixel art headlessly")
    parser.add_argument("project", type=Path, help="source JSON project")
    parser.add_argument("output", type=Path, help="native-resolution PNG output")
    parser.add_argument("--preview", type=Path, help="optional nearest-neighbor enlarged PNG")
    parser.add_argument("--scale", type=int, default=8, help="preview scale (default: 8)")
    args = parser.parse_args()
    if args.scale < 1:
        parser.error("--scale must be positive")
    image = render(json.loads(args.project.read_text(encoding="utf-8")), args.project.parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    if args.preview:
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        image.resize((image.width * args.scale, image.height * args.scale), Image.Resampling.NEAREST).save(args.preview)
    print(f"Rendered {image.width}x{image.height} pixel art: {args.output}")


if __name__ == "__main__":
    main()
