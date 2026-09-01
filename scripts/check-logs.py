#!/usr/bin/env python3
"""Fail on LaTeX errors, unresolved references, or layout overflow."""

from __future__ import annotations

import re
import sys
from pathlib import Path

FAILURES = {
    "LaTeX error": re.compile(r"^! |^.+:\d+: .*Error:", re.MULTILINE),
    "undefined reference": re.compile(r"(?:Reference .+ undefined|There were undefined references)"),
    "undefined citation": re.compile(r"(?:Citation .+ undefined|There were undefined citations)"),
    "rerun requested": re.compile(r"(?:Rerun to get|Label\(s\) may have changed|Please rerun)"),
    "overfull box": re.compile(r"Overfull \\[hv]box"),
    "missing glyph": re.compile(r"Missing character:"),
    "missing image": re.compile(r"Package ricardo-homework Warning: Image .+ not found"),
    "duplicate label": re.compile(r"(?:Label .+ multiply defined|There were multiply-defined labels)"),
}


def main() -> int:
    paths = [Path(value) for value in sys.argv[1:]]
    if not paths:
        print("usage: check-logs.py FILE.log [FILE.log ...]", file=sys.stderr)
        return 2
    failed = False
    for path in paths:
        if not path.exists():
            print(f"{path}: missing")
            failed = True
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        found = [name for name, pattern in FAILURES.items() if pattern.search(source)]
        if found:
            print(f"{path}: FAIL -- {', '.join(found)}")
            failed = True
        else:
            print(f"{path}: clean")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
