#!/usr/bin/env python3
"""Validate generated PDFs against PDF/UA-2 with veraPDF."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def validate(tool: str, pdf: str) -> tuple[list[str], list[tuple[str, int, str]]]:
    result = subprocess.run(
        [tool, "--format", "xml", "--flavour", "ua2", pdf],
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or f"veraPDF exited with {result.returncode}")
    if not result.stdout.strip():
        raise RuntimeError(result.stderr.strip() or "veraPDF returned no report")
    root = ET.fromstring(result.stdout)
    errors = []
    reports = root.findall("./jobs/job/validationReport")
    if len(reports) != 1:
        errors.append(f"expected one validation report, found {len(reports)}")
    elif reports[0].get("jobEndStatus") != "normal":
        errors.append(f"job ended with status {reports[0].get('jobEndStatus')!r}")
    elif reports[0].get("isCompliant") != "true":
        errors.append("validation report is not compliant")

    summary = root.find("./batchSummary")
    if summary is None:
        errors.append("batch summary missing")
    else:
        for key in ("failedToParse", "encrypted", "outOfMemory", "veraExceptions"):
            if summary.get(key) != "0":
                errors.append(f"batch summary reports {key}={summary.get(key)!r}")
        for child_name in ("validationReports", "featureReports", "repairReports"):
            child = summary.find(child_name)
            if child is not None and child.get("failedJobs") not in (None, "0"):
                errors.append(f"{child_name} reports failedJobs={child.get('failedJobs')!r}")

    found = []
    for rule in root.iter("rule"):
        if rule.get("status") != "failed":
            continue
        key = f"{rule.get('clause')}-{rule.get('testNumber')}"
        description = (rule.findtext("description") or "").strip().split(".")[0]
        found.append((key, int(rule.get("failedChecks", 0)), description))
    return errors, found


def main() -> int:
    tool = os.environ.get("VERAPDF", "verapdf")
    if not shutil.which(tool):
        print("veraPDF not found; run this gate through `make check-all` in Docker.")
        return 1
    targets = sys.argv[1:] or ["homework.pdf", "showcase.pdf"]
    failed = False
    for target in targets:
        if not Path(target).exists():
            print(f"{target}: missing")
            failed = True
            continue
        try:
            errors, broken = validate(tool, target)
        except (RuntimeError, ET.ParseError) as exc:
            print(f"{target}: validator error -- {exc}")
            failed = True
            continue
        if errors or broken:
            print(f"{target}: FAIL -- {len(broken)} PDF/UA-2 rule(s)")
            for error in errors:
                print(f"  validator: {error}")
            for key, count, description in broken:
                print(f"  {key:>10}  {count:>5} check(s)  {description[:68]}")
            failed = True
        else:
            print(f"{target}: PDF/UA-2 clean")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
