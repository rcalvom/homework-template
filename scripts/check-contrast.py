#!/usr/bin/env python3
"""Check the text colour pairs used by the light theme against WCAG AA."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PALETTE = Path(__file__).resolve().parent.parent / "theme" / "ricardo-palette.sty"
TEXT = 4.5
GRAPHIC = 3.0
# The Pygments style the code plate uses; see theme/ricardo-code.sty.
STYLE = "rzstyle-light"


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
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


def check_code_style() -> int:
    """Every colour the code plate emits, against the plate it sits on.

    Code is the one part of the page whose colours never pass through
    ricardo-palette.sty. They come from a Pygments style, resolved by name at
    build time, so the discipline that keeps everything above accessible does
    not reach them and nothing here would notice if they drifted.

    That is not hypothetical. Measured against this plate, the best style
    Pygments ships is xcode at 4.49:1 -- close enough to look right and not
    close enough to be AA, in a way no build reports.
    """
    try:
        from pygments.styles import get_style_by_name
    except ImportError:
        print("Pygments not importable -- cannot check the code style")
        return 1
    try:
        style = get_style_by_name(STYLE)
    except Exception:
        print(f"Pygments style {STYLE!r} is not registered")
        print("  pip install --user -e theme/pygments")
        return 1

    background = rgb(style.background_color)
    seen: dict[str, str] = {}
    for token, spec in style.styles.items():
        for part in str(spec).split():
            if part.startswith("#") and len(part) == 7:
                seen.setdefault(part.upper(), str(token))
    for extra in ("line_number_color", "line_number_special_color"):
        value = getattr(style, extra, None)
        if value and value.startswith("#"):
            seen.setdefault(value.upper(), extra)

    failed = 0
    for colour, token in sorted(seen.items()):
        actual = ratio(rgb(colour), background)
        if actual < TEXT:
            print(f"code {token}: {colour} on {style.background_color} "
                  f"is {actual:.2f}:1, expected at least {TEXT:.1f}:1")
            failed += 1
    if not failed:
        print(f"contrast: {len(seen)} colours in Pygments style {STYLE!r} "
              f"meet WCAG AA")
    return failed


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
    return 1 if (failed or check_code_style()) else 0


if __name__ == "__main__":
    sys.exit(main())
