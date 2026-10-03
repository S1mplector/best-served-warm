"""Python renderer for the project's gently animated pencil contours.

The image processing follows the line-boil approach in pikupiku by
S1mplector/pikupiku. This Python implementation uses Pillow and NumPy and
does not invoke the upstream C program, FFmpeg, or another executable.
See third_party/pikupiku/LICENSE for the MIT attribution.
"""

from __future__ import annotations

import argparse
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class RenderSettings:
    width: int = 512
    frames: int = 3
    fps: int = 6
    strength: float = 1.0
    amplitude: float = 0.8
    ink: float = 0.58
    grain: float = 1.5
    simplify: float = 0.32
    threshold: float = 48
    noise_scale: float = 12
    pressure: float = 0.2
    levels: int = 5
    smoothing: int = 2
    palette: int = 128
    seed: int = 0
    pingpong: bool = False


def _noise(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    """Deterministic integer noise matching pikupiku's coordinate hash."""
    mask = np.uint64(0xFFFFFFFF)
    x = np.asarray(x, dtype=np.int64).astype(np.uint64)
    y = np.asarray(y, dtype=np.int64).astype(np.uint64)
    n = (x * np.uint64(0x9E3779B1) ^ y * np.uint64(0x85EBCA77) ^ np.uint64(seed) * np.uint64(0xC2B2AE3D)) & mask
    n = ((n ^ (n >> np.uint64(16))) * np.uint64(0x7FEB352D)) & mask
    n = ((n ^ (n >> np.uint64(15))) * np.uint64(0x846CA68B)) & mask
    n ^= n >> np.uint64(16)
    return (n & np.uint64(65535)).astype(np.float32) / 32767.5 - 1.0


def _smooth_noise(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - ix, y - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = _noise(ix, iy, seed)
    b = _noise(ix + 1, iy, seed)
    c = _noise(ix, iy + 1, seed)
    d = _noise(ix + 1, iy + 1, seed)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def _luminance(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def _base_and_edges(src: np.ndarray, settings: RenderSettings) -> tuple[np.ndarray, np.ndarray]:
    height, width, _ = src.shape
    radius = settings.smoothing
    padded = np.pad(src, ((radius, radius), (radius, radius), (0, 0)), mode="edge")
    center = src
    center_luma = _luminance(center)
    color_sum = np.zeros_like(src, dtype=np.float32)
    weight_sum = np.zeros((height, width), dtype=np.float32)

    for dy in range(2 * radius + 1):
        for dx in range(2 * radius + 1):
            neighbor = padded[dy:dy + height, dx:dx + width]
            weight = 1.0 / (1.0 + np.abs(_luminance(neighbor) - center_luma) * 0.05)
            color_sum += neighbor * weight[..., None]
            weight_sum += weight

    smoothed = color_sum / weight_sum[..., None]
    step = 255.0 / (settings.levels - 1)
    quantized = np.floor(smoothed / step + 0.5) * step
    flat = np.clip((1 - settings.simplify) * smoothed + settings.simplify * quantized, 0, 255)

    flat_luma = _luminance(flat)
    left = np.pad(flat_luma[:, :-1], ((0, 0), (1, 0)), mode="edge")
    right = np.pad(flat_luma[:, 1:], ((0, 0), (0, 1)), mode="edge")
    up = np.pad(flat_luma[:-1, :], ((1, 0), (0, 0)), mode="edge")
    down = np.pad(flat_luma[1:, :], ((0, 1), (0, 0)), mode="edge")
    edges = (np.hypot(right - left, down - up) > settings.threshold).astype(np.float32)
    return flat, edges


def _bilinear(image: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    height, width = image.shape
    x0f, y0f = np.floor(x), np.floor(y)
    x0, y0 = x0f.astype(np.int64), y0f.astype(np.int64)
    fx, fy = x - x0f, y - y0f
    x0c, x1c = np.clip(x0, 0, width - 1), np.clip(x0 + 1, 0, width - 1)
    y0c, y1c = np.clip(y0, 0, height - 1), np.clip(y0 + 1, 0, height - 1)
    return (
        image[y0c, x0c] * (1 - fx) * (1 - fy)
        + image[y0c, x1c] * fx * (1 - fy)
        + image[y1c, x0c] * (1 - fx) * fy
        + image[y1c, x1c] * fx * fy
    )


def _make_frame(
    src: np.ndarray,
    flat: np.ndarray,
    edges: np.ndarray,
    xx: np.ndarray,
    yy: np.ndarray,
    frame_index: int,
    settings: RenderSettings,
) -> np.ndarray:
    seed = settings.seed
    scale = settings.noise_scale
    sx = xx + settings.strength * settings.amplitude * _smooth_noise(xx / scale, yy / scale, 71 + frame_index * 103 + seed)
    sy = yy + settings.strength * settings.amplitude * _smooth_noise(xx / scale, yy / scale, 193 + frame_index * 107 + seed)
    ink = _bilinear(edges, sx, sy)

    pressure_noise = _smooth_noise(xx / 8.0, yy / 8.0, 313 + frame_index * 29 + seed)
    pressure = np.minimum(1.0, settings.strength * settings.ink * (1 + settings.pressure * pressure_noise))
    grain = settings.strength * settings.grain * _noise(xx, yy, 41 + seed)

    base = (1 - settings.strength) * src + settings.strength * flat
    mixed = base * (1 - (ink * pressure)[..., None]) + 28.0 * (ink * pressure)[..., None]
    mixed += grain[..., None]
    return np.clip(np.floor(mixed + 0.5), 0, 255).astype(np.uint8)


def render_frames(image: Image.Image, settings: RenderSettings) -> list[Image.Image]:
    """Render a still into loopable RGB frames with gently boiling contours."""
    if settings.width < 32 or settings.width > 2048:
        raise ValueError("width must be between 32 and 2048")
    if settings.frames < 2 or settings.frames > 120:
        raise ValueError("frames must be between 2 and 120")
    if settings.fps < 1 or settings.fps > 60:
        raise ValueError("fps must be between 1 and 60")
    if not 0 <= settings.strength <= 2 or not 0 <= settings.amplitude <= 20:
        raise ValueError("strength must be 0..2 and amplitude 0..20")
    if not 2 <= settings.levels <= 16 or not 0 <= settings.smoothing <= 5:
        raise ValueError("levels must be 2..16 and smoothing 0..5")
    if not 1 <= settings.threshold <= 255 or not 2 <= settings.noise_scale <= 100:
        raise ValueError("threshold must be 1..255 and noise scale 2..100")

    height = round(image.height * settings.width / image.width)
    if height < 2 or height > 4096:
        raise ValueError("scaled image height must be 2..4096")
    rgba = image.convert("RGBA").resize((settings.width, height), Image.Resampling.LANCZOS)
    # Upstream pikupiku flattens transparent pixels over black before detecting contours.
    black = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    src = np.asarray(Image.alpha_composite(black, rgba).convert("RGB"), dtype=np.float32)
    flat, edges = _base_and_edges(src, settings)
    yy, xx = np.mgrid[0:height, 0:settings.width].astype(np.float32)

    total = settings.frames * 2 - 2 if settings.pingpong else settings.frames
    result = []
    for frame_no in range(total):
        frame_index = frame_no if frame_no < settings.frames else total - frame_no
        pixels = _make_frame(src, flat, edges, xx, yy, frame_index, settings)
        result.append(Image.fromarray(pixels, mode="RGB"))
    return result


def save_gif(frames: list[Image.Image], output: Path, fps: int, palette_size: int = 128, overwrite: bool = False) -> None:
    if not frames:
        raise ValueError("at least one frame is required")
    if fps < 1 or fps > 60:
        raise ValueError("fps must be between 1 and 60")
    if not 4 <= palette_size <= 256:
        raise ValueError("palette size must be between 4 and 256")
    if output.exists() and not overwrite:
        raise FileExistsError(f"{output} already exists; pass --overwrite to replace it")
    output.parent.mkdir(parents=True, exist_ok=True)
    combined = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for index, frame in enumerate(frames):
        combined.paste(frame.convert("RGB"), (0, index * frame.height))
    palette = combined.quantize(colors=palette_size, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{output.stem}-", suffix=".gif", dir=output.parent)
    os.close(fd)
    try:
        quantized[0].save(
            temporary,
            format="GIF",
            save_all=True,
            append_images=quantized[1:],
            duration=max(10, round(1000 / fps / 10) * 10),
            loop=0,
            optimize=False,
            disposal=2,
        )
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def render_file(input_path: Path, output_path: Path, settings: RenderSettings, overwrite: bool = False) -> None:
    if input_path.resolve() == output_path.resolve():
        raise ValueError("input and output paths must differ")
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"{output_path} already exists; pass --overwrite to replace it")
    with Image.open(input_path) as image:
        frames = render_frames(image, settings)
    save_gif(frames, output_path, settings.fps, settings.palette, overwrite)
    print(f"Created {output_path} ({frames[0].width}x{frames[0].height}, {len(frames)} frames at {settings.fps} fps)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a gentle Python line-boil GIF for game artwork.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--frames", type=int, default=3)
    parser.add_argument("--fps", type=int, default=6)
    parser.add_argument("--strength", type=float, default=1.0)
    parser.add_argument("--amplitude", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--pingpong", action="store_true")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing output file")
    args = parser.parse_args()
    settings = RenderSettings(
        width=args.width,
        frames=args.frames,
        fps=args.fps,
        strength=args.strength,
        amplitude=args.amplitude,
        seed=args.seed,
        pingpong=args.pingpong,
    )
    render_file(args.input, args.output, settings, args.overwrite)


if __name__ == "__main__":
    main()
