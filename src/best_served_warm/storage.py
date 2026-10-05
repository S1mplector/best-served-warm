"""Small, validated save files with atomic replacement."""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
from .paths import data_dir
from .coffee import Coffee
from .stations import Kitchen

DEFAULT_OPTIONS = {"volume": 0.55, "visualizer": True, "fullscreen": False}
DEFAULT_GAME = {"day": 1, "score": 0, "served": 0, "selected": "Tea"}
DRINKS = ("Tea", "Coffee", "Cocoa")


def _read(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(value, out, indent=2)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def load_options() -> dict:
    raw = _read(data_dir() / "options.json") or {}
    try:
        volume = float(raw.get("volume", DEFAULT_OPTIONS["volume"]))
    except (TypeError, ValueError):
        volume = DEFAULT_OPTIONS["volume"]
    try:
        typing_volume = max(0.0, min(1.0, float(raw.get("typing_volume", 0.5))))
    except (TypeError, ValueError):
        typing_volume = 0.5
    return {
        "typing_volume": typing_volume,
        "volume": max(0.0, min(1.0, volume)),
        "visualizer": raw.get("visualizer") is not False,
        "fullscreen": raw.get("fullscreen") is True,
    }


def save_options(options: dict) -> None:
    _write(data_dir() / "options.json", options)


def new_game() -> dict:
    game = DEFAULT_GAME.copy()
    save_game(game)
    return game


def load_game() -> dict | None:
    raw = _read(data_dir() / "save.json")
    if not raw:
        return None
    try:
        game = {"day": max(1, int(raw["day"])), "score": max(0, int(raw["score"])), "served": max(0, int(raw["served"])), "selected": raw["selected"]}
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    if game["selected"] not in DRINKS:
        return None
    if "scene" in raw:
        if raw["scene"] not in ("intro_scene", "dialogue", "customer", "cup_station", "coffee"):
            return None
        try:
            page = int(raw["page"])
            revealed = float(raw["revealed"])
        except (KeyError, TypeError, ValueError, OverflowError):
            return None
        if page < 0 or revealed < 0 or not revealed < float("inf"):
            return None
        game.update(scene=raw["scene"], page=page, revealed=revealed)
        if raw['scene'] == 'coffee':
            try:
                if 'kitchen' in raw:
                    game['kitchen'] = Kitchen.from_dict(raw['kitchen']).to_dict()
                else:
                    game['coffee'] = Coffee.from_dict(raw['coffee']).to_dict()
            except (KeyError, TypeError, ValueError):
                return None
        elif raw['scene'] == 'customer':
            step = raw.get('customer_step', 0)
            if type(step) is not int or step not in (0, 1):
                return None
            game['customer_step'] = step
        elif raw['scene'] == 'cup_station':
            try:
                # Validate the structure without loading Pygame surfaces in storage.
                raw_cups = raw['cup_station']
                if not isinstance(raw_cups, dict) or not isinstance(raw_cups.get('placed'), list):
                    return None
                game['cup_station'] = raw_cups
            except (KeyError, TypeError):
                return None
    return game


def save_game(game: dict) -> None:
    _write(data_dir() / "save.json", game)
