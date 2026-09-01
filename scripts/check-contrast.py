#!/usr/bin/env python3
"""Check the text colour pairs used by the light theme against WCAG AA."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PALETTE = Path(__file__).resolve().parent.parent / "theme" / "ricardo-palette.sty"
TEXT = 4.5
GRAPHIC = 3.0
PAIRS = [
    ("rzink", "white", TEXT, "body text"),
    ("rzmuted", "white", TEXT, "secondary text"),
    ("rzaccent", "white", TEXT, "headings and links"),
    ("white", "rzaccent", TEXT, "problem titles"),
    ("white", "rzline", TEXT, "solution and code titles"),
    ("white", "rzsuccess", TEXT, "answer titles"),
    ("rzsuccess", "white", TEXT, "answer title"),
    ("rzwarning", "white", TEXT, "warning text"),
    ("rzerror", "white", TEXT, "error text"),
    ("rzline", "white", GRAPHIC, "borders"),
    ("rzink", "rzaccentsoft", TEXT, "solution text"),
]


def linear(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[int, int, int]) -> float:
    red, green, blue = (linear(value / 255) for value in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def ratio(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    bright, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (bright + 0.05) / (dark + 0.05)


def main() -> int:
    source = PALETTE.read_text(encoding="utf-8")
    colors = {"white": (255, 255, 255), "black": (0, 0, 0)}
    for name, value in re.findall(r"\\definecolor\{([^}]+)\}\{HTML\}\{([0-9A-Fa-f]{6})\}", source):
        colors[name] = tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))
    failed = False
    for foreground, background, minimum, use in PAIRS:
        actual = ratio(colors[foreground], colors[background])
        if actual < minimum:
            print(f"{use}: {actual:.2f}:1, expected at least {minimum:.1f}:1")
            failed = True
    if not failed:
        print(f"contrast: {len(PAIRS)} colour pairs meet WCAG AA")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
