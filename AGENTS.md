# Art and handoff direction

## Target look

- Build a cozy, warm neighborhood cafe in deliberate pixel art. Draw the pixels as designed shapes with controlled palettes, outlines, and clusters; do not take smooth artwork and merely downsample or pixelate it.
- Replace the current illustrated background with authored pixel-art cafe interiors/backgrounds. Backgrounds must use the same palette, light direction, and pixel scale as the foreground art.
- Keep provenance, creator credits, license text, source page, and any attribution requirement alongside every imported pack in `ASSET_LICENSES.md`. Prefer free packs whose license allows this project's intended use; do not assume “free download” means commercial use is allowed.

## Game and asset resolution

- The supplied main-menu artwork is **192x108 native pixels**. Draw pixel art at that digital resolution and scale the complete image to fill the window with nearest-neighbor filtering, with no letterbox borders; pointer mapping must use both window axes. Interactive button bounds are recorded in `src/best_served_warm/menu.py`. Keep popup shapes pixel art at native resolution, but render their labels on the higher-resolution transparent text overlay in `src/best_served_warm/app.py` so letters stay readable. Options, no-save feedback, and the introductory dialogue are separate popup renderers in `src/best_served_warm/screens.py`; dialogue state/content lives in `src/best_served_warm/dialogue.py`.
- Use **16x16 px tiles** for room floors, walls, counters, and modular background construction.
- Use **32x32 px native sprites** for everyday cafe props and food: coffee cups, mugs, beans, espresso tools, plates, croissants, pastries, cakes, and small countertop objects. Multi-tile furniture may be assembled from 16x16 tiles or drawn as clean multiples of the grid.
- Use **16x16 px sprites** only for tiny objects, garnish, icons, and inventory markers where readability permits. Do not shrink 32x32 food sprites into blurry miniatures.
- Use **64x64 px character frames** for the barista and customer portraits/standing sprites. Animation frames must share a consistent canvas and pivot.
- Keep pixel edges hard: use nearest-neighbor scaling at every asset resize and final screen upscale. Avoid bilinear/bicubic filtering, soft blur, anti-aliased vector edges, and texture overlays that obscure pixel clusters.
- Author future gameplay backgrounds on the same 16 px tile grid; a full-screen 640x360 background is 40x22.5 tiles, so compose from tiles or use a designed 640x360 scene with edges aligned to the grid.

## Headless pixel-art authoring

- Use `art_sources/*.json` as editable source. Run `python -m best_served_warm.pixel_art art_sources/coffee_cup.json assets/pixel/coffee_cup.png --preview ../outputs/coffee_cup_preview.png --scale 8` with the project environment. This renders hard native pixels and a nearest-neighbor preview without a GUI.
- Supported ordered operations are `pixel`, `rect`, `line`, `ellipse`, and `polygon`, with named palette colors. To edit an existing native-resolution PNG, set `base_image` to its path relative to the JSON file, then add overlay layers (a transparent palette color can erase pixels). Draw at native 16x16 or 32x32 rather than filtering a smooth picture. Source JSON should be committed beside resulting game PNGs.
- The user's girlfriend supplied the new **192x108** pixel-art main menu, now stored as `assets/images/main_menu.png`. Keep it unfiltered and do not draw the old logo, button assets, footer, or cursor over it. The old `assets/images/background.png` is retained only behind the existing options/game screens, whose styling the user allowed to stay.

## Free asset research handoff

Search itch.io for pixel-art cafe/barista/interior packs plus food, drinks, coffee, bakery, croissants, cakes, and countertop items. Record useful listings, native size, what is included, exact free/commercial license scope, credit requirements, and source URLs below. Download only assets whose stated license fits the project; keep unreviewed packs in a candidate list rather than importing them.

### Candidate packs inspected

- [Sprout Lands - Asset Pack](https://cupnooble.itch.io/sprout-lands-asset-pack) by Cup Nooble: name-your-price; includes a free Basic Pack ZIP with farm/plant/animal pixel art (not a cafe pack, but useful food/ingredient props). Page calls it 16-bit pixel art, but does not state sprite dimensions. Free version is **non-commercial only**, requires credit; premium license (paid) permits commercial use. Do not assume the free pack is cleared for a commercial release.
- [Modern Interiors - RPG Tileset [16X16]](https://limezu.itch.io/moderninteriors) by LimeZu: broad set of interior furniture, modular walls/floors, bakery/kitchen themes and many animated objects; offered at name-your-price with a free version. Full pack includes 16x16, 32x32, and 48x48 variants; full license requires credit and forbids resale/redistribution. Page's detailed license says the complete version requires at least $1.50, so review the free version's terms separately before any production use. Strong candidate if its art matches the style.
- The locally downloaded catalog is in `../outputs/itch-free-assets/MANIFEST.md`; it includes source links, native sizes, and license notes. Pack archives are local research material, not assets to ship wholesale.
- [Cozy Starter](https://gegx.itch.io/cozy-starter) by GegX remains available in `assets/ui/cozy_starter/` for options and gameplay UI. The new main menu uses only the user's supplied artwork. The pack allows commercial game use but prohibits standalone asset-pack resale.

These are research leads, not imported assets. Search results did not reliably honor free-price query filtering, so inspect the exact pack page and download terms each time. Add cafe-specific food/coffee candidates here as they are found.
