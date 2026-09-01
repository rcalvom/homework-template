# Licences for the bundled fonts

This repository redistributes font files, and all three licences require their text to travel with them.
Here it is.

| File in `assets/fonts/` | Original | Licence |
|---|---|---|
| `UbuntuMonoNerdFont-*.ttf` | Ubuntu Mono, patched by Nerd Fonts | `UbuntuFontLicence-1.0.txt` (the design) + `NerdFonts-LICENSE.md` (the added glyphs) |
| `rz-prompt-arrow.ttf` | Adwaita Mono, reduced to U+279C | `AdwaitaMono-OFL.txt` (SIL OFL 1.1) |

`rz-prompt-arrow.ttf` is a **subset**: Adwaita Mono with one glyph, the `➜` from the zsh prompt.
Regenerate it with `make prompt-font`.
The OFL allows modifying and redistributing provided the reserved font name is not used, which is why the file is called `rz-prompt-arrow` and not `AdwaitaMono`.

The texts were copied from the installed system packages (`ttf-ubuntu-font-family`, `adwaita-fonts`, `ttf-nerd-fonts-symbols`), not transcribed by hand.
