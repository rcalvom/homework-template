#!/usr/bin/env python3
"""Verify that every icon the theme declares exists in the bundled font.

    python3 scripts/check-glyphs.py

Nerd Font icons live in the Private Use Area, and a codepoint that is not in
the font does not fail the build -- it prints a blank, or the .notdef box, and
the document compiles happily around the hole. So the codepoints are declared
once in theme/ricardo-icons.sty and checked here against the actual .ttf.

Needs fontTools. It is in the container image; locally, `pip install fonttools`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts" / "UbuntuMonoNerdFont-Regular.ttf"
ICONS = ROOT / "theme" / "ricardo-icons.sty"


def declared() -> list[tuple[str, int]]:
    """Every \\rz@glyph{"XXXX} in the icon package, with the macro it names."""
    src = ICONS.read_text()
    found = re.findall(r"\\newcommand\{\\(\w+)\}\{\\rz@glyph\{\"([0-9A-Fa-f]+)\}",
                       src)
    return [(name, int(code, 16)) for name, code in found]


def main() -> int:
    if not FONT.exists():
        print(f"{FONT.relative_to(ROOT)}: missing -- run `make fonts'")
        return 1
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        print("fontTools not installed; skipping the glyph check")
        print("  pip install fonttools, or run this in the container")
        return 0

    font = TTFont(FONT)
    cmap: set[int] = set()
    for table in font["cmap"].tables:
        cmap |= set(table.cmap.keys())

    icons = declared()
    missing = [(n, c) for n, c in icons if c not in cmap]
    for name, code in missing:
        print(f"  MISSING  \\{name}  U+{code:04X} is not in the font")
    if missing:
        print(f"\n{len(missing)} of {len(icons)} declared glyph(s) missing; "
              f"they would render blank.")
        return 1
    print(f"all {len(icons)} declared glyphs present in "
          f"{FONT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
