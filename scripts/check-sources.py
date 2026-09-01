#!/usr/bin/env python3
"""Check source-level invariants that do not require a PDF build."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMAND = re.compile(r"\\Homework(?:Figure|Diagram)\b")
DIRECT_GRAPHIC = re.compile(r"\\includegraphics\b")


def skip_space(source: str, offset: int) -> int:
    while offset < len(source) and source[offset].isspace():
        offset += 1
    return offset


def group(source: str, offset: int, opening: str, closing: str) -> tuple[str, int]:
    offset = skip_space(source, offset)
    if offset >= len(source) or source[offset] != opening:
        raise ValueError(f"expected {opening!r}")
    depth = 1
    start = offset + 1
    offset += 1
    while offset < len(source) and depth:
        if source[offset] == opening and source[offset - 1] != "\\":
            depth += 1
        elif source[offset] == closing and source[offset - 1] != "\\":
            depth -= 1
        offset += 1
    if depth:
        raise ValueError(f"unclosed {opening!r}")
    return source[start : offset - 1], offset


def strip_comments(source: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", source)


def strip_verbatim(source: str) -> str:
    pattern = re.compile(
        r"\\begin\{(?:codebox|minted|verbatim|Verbatim)\}.*?"
        r"\\end\{(?:codebox|minted|verbatim|Verbatim)\}",
        re.DOTALL,
    )
    return pattern.sub(lambda match: "\n" * match.group(0).count("\n"), source)


def check_media(path: Path) -> list[str]:
    source = strip_verbatim(strip_comments(path.read_text(encoding="utf-8")))
    errors: list[str] = []
    for match in COMMAND.finditer(source):
        offset = skip_space(source, match.end())
        try:
            if offset < len(source) and source[offset] == "[":
                _, offset = group(source, offset, "[", "]")
            args = []
            for _ in range(4):
                value, offset = group(source, offset, "{", "}")
                args.append(value.strip())
        except ValueError as exc:
            line = source.count("\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(ROOT)}:{line}: malformed media command: {exc}")
            continue
        if not args[0]:
            line = source.count("\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(ROOT)}:{line}: empty media path")
        if not args[1]:
            line = source.count("\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(ROOT)}:{line}: empty caption")
        if not args[2]:
            line = source.count("\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(ROOT)}:{line}: empty alt text")
        if not args[3]:
            line = source.count("\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(ROOT)}:{line}: empty figure label")
    for match in DIRECT_GRAPHIC.finditer(source):
        line = source.count("\n", 0, match.start()) + 1
        errors.append(
            f"{path.relative_to(ROOT)}:{line}: use \\HomeworkFigure or "
            "\\HomeworkDiagram instead of \\includegraphics"
        )
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.tex")):
        errors.extend(check_media(path))
    if errors:
        print("Source checks failed:")
        for error in errors:
            print(f"  {error}")
        return 1
    print("sources: media descriptions and labels present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
