#!/usr/bin/env python3
"""Validate paper size, tagging, embedded fonts, and CM-Super usage."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

LETTER = (612.0, 792.0)
TOLERANCE = 0.5


def run(*command: str) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        detail = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
        raise RuntimeError(detail or "command failed")
    return result.stdout


def dimensions(info: str) -> tuple[float, float] | None:
    match = re.search(r"(?:Page(?:\s+\d+)? size):\s+([\d.]+) x ([\d.]+) pts", info)
    if not match:
        return None
    return float(match.group(1)), float(match.group(2))


def check_pdf(path: Path) -> list[str]:
    errors: list[str] = []
    run("qpdf", "--check", str(path))
    info = run("pdfinfo", str(path))
    pages_match = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    pages = int(pages_match.group(1)) if pages_match else 0
    if not pages:
        errors.append("could not determine page count")
    if not re.search(r"^Tagged:\s+yes$", info, re.MULTILINE | re.IGNORECASE):
        errors.append("PDF is not tagged")
    for page in range(1, pages + 1):
        page_info = run("pdfinfo", "-f", str(page), "-l", str(page), str(path))
        size = dimensions(page_info)
        if size is None:
            errors.append(f"page {page}: size not reported")
            continue
        if any(abs(actual - expected) > TOLERANCE for actual, expected in zip(size, LETTER)):
            errors.append(f"page {page}: expected 612 x 792 pt, got {size[0]:g} x {size[1]:g} pt")

    fonts = run("pdffonts", str(path)).splitlines()
    rows = [line.split() for line in fonts[2:] if line.strip()]
    if not rows:
        errors.append("no fonts found")
    if rows and any(len(row) < 6 or row[-5].lower() != "yes" for row in rows):
        errors.append("one or more fonts are not embedded")
    if rows and not any(row[0].split("+")[-1].startswith("SF") for row in rows):
        errors.append("CM-Super text font not found")
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check-pdf.py FILE.pdf [FILE.pdf ...]", file=sys.stderr)
        return 2
    failed = False
    for value in sys.argv[1:]:
        path = Path(value)
        if not path.exists():
            print(f"{path}: missing")
            failed = True
            continue
        try:
            errors = check_pdf(path)
        except (OSError, RuntimeError) as exc:
            errors = [str(exc)]
        if errors:
            print(f"{path}: FAIL")
            for error in errors:
                print(f"  {error}")
            failed = True
        else:
            print(f"{path}: US Letter, tagged, CM-Super fonts embedded")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
