# Best Served Warm

A cozy cafe game prototype in Python. The menu uses the supplied ChatGPT artwork, animated buttons, and a custom animated cursor rendered with [pikupiku](https://github.com/S1mplector/pikupiku). Buttons have clear hover and click states. The music and menu fade in together. New Game starts a small drink-serving loop; Load Game restores it; Options controls music and fullscreen. The bar visualizer is saved in the codebase for later, but is currently hidden.

## Run

Python 3.11+:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
python -m best_served_warm
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

Menu images were provided by the project owner, generated in ChatGPT. `assets/buttons/new-game.png` and `assets/images/bar.png` were generated for this project. `pikupiku` is an MIT-licensed local tool used to render the button GIFs; its executable is not bundled.

“Moon Unit (Lofi, Reflection, Dreamy)” by [HoliznaCC0](https://freemusicarchive.org/music/holiznacc0/public-domain-lofi/moon-unit-lofi-reflection-dreamy/) is [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). The WAV is a format conversion of the original MP3. Attribution is included voluntarily in the game menu.
