# Best Served Warm

A cozy cafe game prototype in Python. The menu uses the supplied ChatGPT artwork, animated buttons, and a custom animated cursor. Buttons have clear hover and click states. The music and menu fade in together. New Game starts a small drink-serving loop; Load Game restores it; Options controls music and fullscreen. The bar visualizer is saved in the codebase for later, but is currently hidden.

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

On Windows activate with `.venv\Scripts\activate` and use `python` as usual. Click the buttons. Escape saves and returns to the menu; Escape from the menu exits. Save files live under the platform's user application data directory.

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

All screens now draw at the supplied main menu's native 192x108 resolution, enlarged with nearest-neighbor scaling to fill the window. Its four built-in buttons receive a slight warm fill on hover without replacing their lettering or shadows. Options, load feedback, and play controls appear as simple pixel-art popups over the artwork; the custom cursor appears throughout. The free [GegX Cozy Starter](https://gegx.itch.io/cozy-starter) pack and other cafe/food research downloads are cataloged in `../outputs/itch-free-assets/MANIFEST.md` on this machine. The art direction and native sprite sizes are in `AGENTS.md`.
