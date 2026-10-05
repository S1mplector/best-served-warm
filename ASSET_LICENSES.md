# Asset credits and terms

- `assets/audio/moon-unit.wav`: “Moon Unit (Lofi, Reflection, Dreamy)” by HoliznaCC0. Source: https://freemusicarchive.org/music/holiznacc0/public-domain-lofi/moon-unit-lofi-reflection-dreamy/ . Licensed CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/ . Converted from the source MP3 to mono 22.05 kHz WAV for playback and visualizer analysis.
- `assets/images/background.png`, `assets/images/logo.png`, and the original `assets/buttons/load-game.png`, `options.png`, `exit-game.png`: ChatGPT-generated artwork provided by the project owner.
- `assets/buttons/new-game.png` and `assets/images/bar.png`: ChatGPT-generated artwork made for this project, matching the supplied art. The dormant visualizer repeats the one plain parchment rectangle sprite.
- `assets/cursor/cursor.png`: ChatGPT-generated parchment cursor made for this project. `cursor.gif` was rendered from it with the in-project Python renderer and retains its alpha mask in the game.
- Button and logo GIFs were derived from their respective PNGs using the in-project Python line-boil renderer. The rendering approach follows pikupiku (MIT): https://github.com/S1mplector/pikupiku . Its license is included in `third_party/pikupiku/LICENSE`.

The root MIT license covers the project code. Asset rights are described above.
# Cozy Starter UI

- Creator: GegX; source: https://gegx.itch.io/cozy-starter
- Local game files: `assets/ui/cozy_starter/` (selected UI PNGs from the free starter pack).
- The listing permits use in paid and free games and prohibits resale of the assets themselves as an asset pack. No attribution requirement is stated; credit GegX in game credits as a courtesy.
- Button backgrounds are displayed at integer 2x scale with nearest-neighbor filtering. Original artwork is 64x24 px.
# New main-menu artwork

- Source: `IMG_6443.PNG`, supplied directly by the user on 2026-10-03 as artwork made by his girlfriend.
- In-game copy: `assets/images/main_menu.png`, original 192x108 RGBA PNG preserved without resampling. The runtime makes transient hover tints only within the baked-in button interiors.

# Menu cursor and cat

- `assets/cursor/megabyte/cursor-pointer-1.png` and `cursor-pointer-5.png`: cursor sprites from Megabyte Games, [Mouse Cursor Pack](https://megabyte-games.itch.io/mouse-cursor-pack), CC0. The pack ZIP is retained in `../outputs/itch-free-assets/` for research.
- `assets/cat/grey-walk.png`: four 16x16 walking frames selected from the grey sheet in Pop Shop Packs, [Cat || Pixel Asset Pack](https://pop-shop-packs.itch.io/tiny-cat-pixel-asset-pack). Listing permits personal/commercial projects and modifications; it prohibits redistributing the source pack as a standalone asset. Credit is appreciated. The full source ZIP is retained in `../outputs/itch-free-assets/` for research.

# Current music and UI audio

- `assets/audio/chill-lofi.mp3`: “Chill lofi inspired” by omfgdude, https://opengameart.org/node/74097 . CC0: https://creativecommons.org/publicdomain/zero/1.0/ . Downloaded the creator's low-pass-filtered MP3 version; replaces Moon Unit in runtime playback, with reduced music gain.
- `assets/audio/ui/*.ogg`: selected tick, click, back, switch, and select sounds from Kenney Interface Sounds, https://kenney.nl/assets/interface-sounds . CC0; original license included at `assets/audio/ui/LICENSE.txt`. Hover feedback is entry-triggered; all cues are reduced in volume.

- `assets/cursor/cozy-source.png`: generated with the built-in imagegen tool for this project. Prompt: single northwest arrow for a cozy cafe pixel-art game, cocoa outline, cream fill, caramel highlight, chunky stepped edges, transparent background, no text or extra objects. `cozy.png` is the cropped runtime source; `cozy-wiggle.png` contains four frames from the in-project Python line-boil renderer with original alpha restored.
- `assets/audio/ui/type.wav`: original synthesized soft retro typing tone generated in Python for this project.

- `assets/cursor/cozy-smooth.png`: generated with the built-in imagegen tool. Prompt: a conventional northwest arrow for a cozy cafe game, smooth anti-aliased silhouette, cocoa outline, cream fill, caramel accent, transparent background; no pixel art or text. Current runtime cursor, displayed at window resolution with smooth filtering and no animation.

- `assets/fonts/PixelifySans.ttf`: Pixelify Sans by the Pixelify Sans Project Authors, https://github.com/eifetx/Pixelify-Sans ; downloaded from Google Fonts. SIL Open Font License 1.1 included in `assets/fonts/OFL.txt`. Used for all runtime menu and dialogue text.

- `assets/cat/grey-rest.png`: four side-view sitting/rest poses from the same Pop Shop Packs grey cat sheet, under the cat pack terms above. Used for settling down, naps, and waking up.

- `assets/cat/white-sleep.png`: white side-view crouch pose adapted from Pop Shop Packs Tiny Cat with a closed eyelid. Same cat-pack terms apply. Permanently perched on the Served title; independent from wandering-cat AI.

- Current font: `assets/fonts/Jersey20-Regular.ttf`, Jersey 20 by Sarah Cadigan-Fried / Soft Type Project Authors, from https://github.com/google/fonts/tree/main/ofl/jersey20 . SIL OFL 1.1, included as `Jersey20-OFL.txt`. Replaces Pixelify Sans in runtime menus and dialogue.

- Current font: `assets/fonts/m5x7.ttf`, m5x7 by Daniel Linssen, downloaded from https://managore.itch.io/m5x7 . Listing declares CC0; attribution appreciated. Use only the creator’s specified sizes 16, 32, 48, etc. Runtime uses 16 for dialogue and 32 for menu text, followed only by integer scaling.
# User-provided artwork

- `assets/characters/redhead_woman_retro.png`: revised layered retro design of the female character, generated with built-in imagegen on 2026-10-05 and converted with the existing 160×160 Python pipeline. Source, prompt and preview are in `art_sources/characters/redhead_woman_retro*` and its `previews/` directory.

- `assets/characters/redhead_woman_neutral.png`: original female character generated with built-in imagegen on 2026-10-05, using the existing standing character as the style reference. Converted through the same 160×160 nearest-neighbor pipeline. Original, exact prompt, and preview are in `art_sources/characters/`, documented in `redhead_woman.md`.

- `assets/characters/spiky_guy_{neutral,talking,confused,happy,surprised,concerned}.png`: facial-expression edits of the generated standing character, made with built-in imagegen on 2026-10-05 and converted with the same Python nearest-neighbor workflow. Full sources, exact prompts, and previews are retained in `art_sources/characters/`.

- `assets/characters/spiky_guy.png` and `spiky_guy_idle.png`: original greeting character and standing closed-mouth smile variant generated for this project with the built-in imagegen tool on 2026-10-05, then reduced to 160×160 in Python with nearest-neighbor filtering at the user's request. Both full-resolution sources, prompts, and enlarged previews are preserved in `art_sources/characters/`.

- `assets/images/new_game_background.png`: `Bakery_PixelArt_MASTER_320x180.png`, supplied by the user on 2026-10-04 for the New Game scene background. No external license or attribution requirement was provided.
- `assets/images/coffee_cup_station.png`: `Cozy Pixel Café Cup Station.png`, supplied by the user on 2026-10-04 for the coffee-making scene. Original 1672x940 image preserved; no external license or attribution requirement was provided.
- `assets/images/coffee_cup_station_master.png`: `Coffee_Cup_Station_FINAL_MASTER_320x180.png`, supplied by Yağmur Ali by email on 2026-10-04. The nine `assets/cups/*.png` sprites are lossless alpha crops of this sheet. No external license or attribution requirement was provided.

## Shared itch.io research packs

These source files are kept intact under `assets/hoarded/` for project reference. They are not yet integrated into gameplay.

- `assets/hoarded/bakery-sweetz-cc0.png`: Crumpaloo, [Free Bakery Sweet's Pack](https://crumpaloo.itch.io/free-bakery-sweets-pack), CC0 1.0. Nine 32x32 bakery sprites. Credit is optional.
- `assets/hoarded/dessert-icons-cc-by-4.0.zip`: Lumin / Ellie Jerram, [Free Dessert Icons](https://luminleveret.itch.io/desserts), CC BY 4.0. Credit “Ellielza” and/or “Ellie Jerram” and link to the pack.
- `assets/hoarded/pixel-art-bar-and-cafe-cc0.zip`: Karsiori Studio, [Free Pixel Art Bar and Cafe Items Pack](https://karsiori.itch.io/free-pixel-art-bar-and-cafe-items-pack), CC0. Credit is appreciated but not required.
- `assets/hoarded/pixel-food-16x16-cc-by-4.0.zip`: alexkovacsart, [100 Free Pixel Art Foods](https://alexkovacsart.itch.io/free-pixel-art-foods), CC BY 4.0. Credit the creator and link to the pack.
- `assets/hoarded/megabyte-mouse-cursors-cc0.zip`: Megabyte Games, [Mouse Cursor Pack](https://megabyte-games.itch.io/mouse-cursor-pack), CC0 1.0. Credit is optional.
- `assets/hoarded/karsiori-food-cc0.zip` and selected `assets/barista/{croissant,doughnut,cake}.png`: Karsiori Studio, [FREE Pixel Art - Food Pack](https://karsiori.itch.io/free-pixel-art-food-pack), CC0 1.0. Credit is appreciated but optional. The source pack is retained intact; selected sprites keep their native dimensions.
- `assets/barista/{espresso_machine,coffee_pot}.png` are unmodified sprites from the Karsiori Studio [Bar and Cafe Items Pack](https://karsiori.itch.io/free-pixel-art-bar-and-cafe-items-pack) above, CC0.
- `assets/barista/beans_{light,medium,dark}.png` are native 16x16 icons from alexkovacsart's [100 Free Pixel Art Foods](https://alexkovacsart.itch.io/free-pixel-art-foods), CC BY 4.0. Credit alexkovacsart and link the pack when distributing the game.
- The remaining `assets/barista/*.png` are original 32x32 pixel sprites authored for this project. Editable operation layers are in `art_sources/barista/*.json`; `tools/build_barista_art.py` regenerates them.

Other downloaded candidates remain in the local research folder, not this repository: the Yanin coffee sample, Food & Ingredients, Ghostpixxells Pixel Food, Neko Cafe, Cozy Starter, and Tiny Cat packs. Their listings restrict redistribution of the raw files or leave the scope unclear. Existing selected game assets already imported under their project-use terms are documented above.

New itch.io research downloads and terms are recorded in `docs/itch-assets.md`. Packs whose licenses prohibit raw-file redistribution stay outside this repository.
