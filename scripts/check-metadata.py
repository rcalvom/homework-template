#!/usr/bin/env python3
"""Reject the public template's default metadata before submission."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = {
    "TemplateStatus": "final",
    "CommentsMode": None,
    "HomeworkTitle": "Homework 01",
    "HomeworkSubtitle": "Template assignment",
    "StudentName": "Student Name",
    "StudentId": "Student ID",
    "CourseCode": "COURSE 101",
    "CourseName": "Course Name",
    "InstructorName": "Instructor Name",
    "SubmissionDate": "Month DD, YYYY",
}


def strip_comments(source: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", source)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check-metadata.py homework.tex", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    source = strip_comments(path.read_text(encoding="utf-8"))
    values = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^{}]*)\}", source))
    errors = []
    for name, placeholder in REQUIRED.items():
        if name not in values:
            errors.append(f"missing \\{name}")
        elif not values[name].strip():
            errors.append(f"empty \\{name}")
        elif name == "TemplateStatus" and values[name].strip() != "final":
            errors.append("set \\TemplateStatus to final")
        elif name == "CommentsMode" and values[name].strip() not in {"auto", "hide"}:
            errors.append("set \\CommentsMode to auto or hide")
        elif placeholder is not None and values[name].strip() == placeholder:
            errors.append(f"replace \\{name} ({placeholder})")

    for example in ("A recurrence and its closed form", "Complexity analysis"):
        if example in source:
            errors.append(f"replace example problem `{example}`")

    if errors:
        print(f"{path}: not ready for submission:")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"{path}: submission metadata finalized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
