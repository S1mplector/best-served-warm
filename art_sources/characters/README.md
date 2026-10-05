# Waist-up characters

All runtime characters use a transparent 160×160 RGBA canvas. Fit the complete hair, shoulders, hands and waist inside a 150×150 area, horizontally centered, with the waist baseline at y=155 and bottom-center anchor (80, 155). Keep this canvas and anchor for every future character and expression. Display only with nearest-neighbor scaling. Always regenerate from the original source, never upscale the previous smaller sprites.

Spiky guy: energetic young adult with chestnut spikes, welcoming wave, mustard overshirt and cream tee. Hybrid anime / stylized indie game art, warm bakery palette. Source created with the built-in imagegen tool on 2026-10-05. At the user's request, Python performs nearest-neighbor reduction, hard alpha thresholding and 32-color quantization without dithering. The original source is preserved.

Regenerate from the repository root:

```sh
.venv/bin/python tools/build_character.py art_sources/characters/spiky_guy_source.png assets/characters/spiky_guy.png --preview /tmp/spiky-guy-preview.png
```

## Saved poses

- Greeting: `spiky_guy_source.png`, runtime `../../assets/characters/spiky_guy.png`, enlarged reference `previews/spiky_guy_greeting.png`.
- Relaxed standing, closed-mouth smile: `spiky_guy_idle_source.png`, runtime `../../assets/characters/spiky_guy_idle.png`, enlarged reference `previews/spiky_guy_idle.png`.
- Both runtime sprites are 160×160; previews are 640×640 nearest-neighbor enlargements. Sources and previews are retained in Git for future edits.

Regenerate idle:

```sh
.venv/bin/python tools/build_character.py art_sources/characters/spiky_guy_idle_source.png assets/characters/spiky_guy_idle.png --preview art_sources/characters/previews/spiky_guy_idle.png
```

Idle edit prompt (built-in imagegen, source: original greeting illustration):

Edit this exact character into a neutral standing idle pose for the same game. Preserve his identity exactly: same chestnut spiky hairstyle and hair silhouette, warm brown eyes, face shape, youthful adult proportions, mustard rolled-sleeve overshirt, cream T-shirt, cocoa outlines, warm cel-shaded palette, hybrid anime/stylized indie-game art. Change only pose and mouth expression: lower the waving arm, both arms now hanging naturally relaxed beside his torso, shoulders relaxed, no greeting gesture, no hand on hip. Friendly subtle CLOSED-MOUTH smile, lips together, no teeth visible. Keep waist-up framing, same head scale and slight three-quarter viewing angle, full hair and shoulders contained, waist cutoff, same square canvas and transparent background. One character only. No text, props, background, floor, or shadows outside the silhouette. This is an alternate pose of the supplied character, not a redesign.

Original generation prompt (historical; final runtime standard is now 160×160):

Use case: stylized-concept. Create a single game character asset for Best Served Warm, a cozy autumn neighborhood bakery. An energetic young adult man with thick chestnut spiky hair, warm amber-brown eyes, lively raised eyebrows and a friendly broad grin. Hybrid art direction halfway between expressive anime and Western stylized indie game character art, grounded adult proportions, not chibi. Waist-up only, complete hair silhouette, both shoulders and elbows inside frame, simple mustard overshirt with rolled sleeves over a cream T-shirt. Relaxed animated posture, one hand raised in a casual greeting near shoulder, other hand at waist. Facing the player with slight three-quarter turn. Strong cocoa brown outline, very simplified large clean cel-shaded shapes with just two shadow levels, muted ochre, terracotta, cream and dark warm brown palette, warm upper-left light. Designed to survive nearest-neighbor reduction to a 64x64 game sprite: large expressive face and hair tufts, no tiny texture or intricate detail. Square canvas, character centered and occupying about 88 percent of height, clean flat waist cutoff, generous transparent padding around full silhouette, genuinely transparent background, no scenery, no ground shadow, no text, no border. One character, one pose.
