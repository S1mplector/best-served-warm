# Red-haired woman — neutral

Woman around 28 with dark burgundy hair, a subtly tired neutral expression, and a retro Y2K striped sweater. Generated with built-in imagegen using `spiky_guy_idle_source.png` as the visual style reference on 2026-10-05.

- Original: `redhead_woman_neutral_source.png`
- Runtime: `../../assets/characters/redhead_woman_neutral.png` (160×160 transparent RGBA)
- Enlarged reference: `previews/redhead_woman_neutral.png` (640×640)
- Same pipeline as the existing cast: nearest-neighbor reduction, hard alpha, 32 colors, shared (80, 155) bottom-center anchor.

```sh
.venv/bin/python tools/build_character.py art_sources/characters/redhead_woman_neutral_source.png assets/characters/redhead_woman_neutral.png --preview art_sources/characters/previews/redhead_woman_neutral.png
```

## Generation prompt

Use case: stylized-concept. Create ONE NEW female character for the SAME visual novel/cafe game as the supplied male character. Input image is a STYLE, framing and rendering reference only, not a subject to copy. Absolutely match its hybrid anime / Western stylized indie game look: identical cocoa outline weight, cel-shading treatment, simplified angular color shapes, warm restrained palette, lighting from upper left, face detail level, adult stylized proportions and waist-up framing. Woman around 28 years old, visibly adult, dark red burgundy hair in a slightly tousled shoulder-length layered cut with soft side bangs. A subtly tired look: softly lowered upper eyelids and faint understated under-eye shadows, relaxed brows; neutral expression with closed relaxed mouth, neither smiling nor sad. Retro Y2K striped knit sweater, muted burgundy, dusty cream and charcoal horizontal stripes, crew neckline, slightly loose fit, long sleeves, broad simple stripes that survive pixel reduction, no intricate knitted texture. Natural standing pose, arms down beside torso, same slight three-quarter orientation and portrait scale as reference. Full hair and shoulders inside canvas, clean waist cutoff. Square 1254x1254 canvas if possible, genuinely transparent background. This will be reduced using nearest-neighbor to 160x160 so use readable large color shapes and crisp features. No scenery, props, text, symbols, frame, extra characters, or cast shadow. Do not drift into photorealism, painterly brushwork, glossy 3D, chibi or high-detail anime.
