# Best Served Warm

A cozy cafe game prototype in Python. New Game opens a minimal cat loading scene, then a customer enters the bakery and orders a mug latte with a croissant. Reply to the customer to take the order, choose one of nine cups at the cup station, and place it on the counter to continue to the working barista stations. The later station layout is a temporary visual prototype; its cup and tool mechanics can move into future cafe scenes. Load Game restores the conversation, cup selection, or drink mid-preparation.

## Run

Python 3.11+:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
python -m best_served_warm
```

The `best-served-warm-render-gif` command creates gentle line-boil GIFs with Pillow and NumPy, without the upstream C++ executable or FFmpeg:

```sh
best-served-warm-render-gif assets/buttons/new-game.png /tmp/new-game.gif --width 700 --strength 0.45 --amplitude 0.55 --frames 3 --fps 5 --pingpong
```

On Windows activate with `.venv\Scripts\activate` and use `python` as usual. At the cup station, click a cup on the rack, click the counter to place it, then choose Next Station. At the temporary barista stations, click a tool to pick it up and click a station to place it. Hold the controls to grind, tamp, brew, and steam milk; release to stop. Move the cup to the milk and finishing stations to add ingredients, then to Serve. Bring used tools to the sink to rinse them. Press Escape to pause and save at any point. Save files live under the platform's user application data directory.

The preparation rules are in `src/best_served_warm/stations.py`: each cup and tool has its own location and contents, allowing more than one drink in progress and preparation in different orders. Dose, tamp pressure, shot yield, and milk temperature affect the result. `station_view.py` is only the current clickable stand-in for future station art.

## Build

```sh
python -m pip install -e '.[build,test]'
pytest -q
pyinstaller --noconfirm BestServedWarm.spec
```

PyInstaller must run **on each target OS**. The GitHub Actions workflow runs headless tests and packaging on Linux, macOS, and Windows; download the artifacts from a successful run. These are unsigned development builds and may trigger OS warnings. The playable Linux build is also locally verified during development; other OS builds are checked in CI.

## Layout

- `src/best_served_warm/app.py`: event loop and scenes
- `art.py`: still images, pikupiku button GIFs, and cursor GIF frames
- `music.py`: music playback, with optional spectrum analysis for future visuals
- `visualizer.py`: dormant bar renderer retained for later
- `stations.py`: station, item, preparation, cleaning, and order rules
- `station_view.py`: temporary station scene and input
- `loading_cats.py`: animated cats and spinner
- `storage.py`: save and options data
- `assets/`: original menu art, animated buttons, one bar sprite, music

## Credits

Menu images were provided by the project owner, generated in ChatGPT. `assets/buttons/new-game.png` and `assets/images/bar.png` were generated for this project. The in-project Python GIF renderer follows the line-boil approach in [pikupiku](https://github.com/S1mplector/pikupiku); its MIT license is included in `third_party/pikupiku/LICENSE`. The upstream executable is not bundled or required.

“Moon Unit (Lofi, Reflection, Dreamy)” by [HoliznaCC0](https://freemusicarchive.org/music/holiznacc0/public-domain-lofi/moon-unit-lofi-reflection-dreamy/) is [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). The WAV is a format conversion of the original MP3. Attribution is included voluntarily in the game menu.
# Headless pixel-art workflow

Edit a palette and integer-pixel drawing operations in `art_sources/coffee_cup.json`, then render a native PNG and an enlarged nearest-neighbor preview without opening an editor:

```sh
python -m best_served_warm.pixel_art art_sources/coffee_cup.json assets/pixel/coffee_cup.png --preview ../outputs/coffee_cup_preview.png --scale 8
```

The supplied main menu and the cat loading screen draw at 192x108 native resolution; the temporary station scene draws at 640x360. Both scale with nearest-neighbor filtering. The menu's four built-in buttons receive a slight warm fill on hover without replacing their lettering or shadows. Options and load feedback use pixel-art popups. Asset research is recorded in `docs/itch-assets.md`, with licensing in `ASSET_LICENSES.md`.
