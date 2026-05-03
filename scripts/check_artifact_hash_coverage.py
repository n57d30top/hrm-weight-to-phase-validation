#!/usr/bin/env python3
"""Ensure every generated JSON report is listed in ARTIFACTS.sha256."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"
ARTIFACTS = REPORT_DIR / "ARTIFACTS.sha256"


def main() -> int:
    json_reports = {
        path.relative_to(ROOT).as_posix()
        for path in REPORT_DIR.glob("*.json")
        if path.is_file()
    }
    hashed_reports = _hashed_json_reports()
    missing = sorted(json_reports - hashed_reports)

    if missing:
        print("artifact hash coverage check failed:", file=sys.stderr)
        for path in missing:
            print(f"missing from {ARTIFACTS.relative_to(ROOT)}: {path}", file=sys.stderr)
        return 1
    return 0


def _hashed_json_reports() -> set[str]:
    if not ARTIFACTS.is_file():
        return set()
    reports = set()
    for line in ARTIFACTS.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].endswith(".json"):
            reports.add(parts[1])
    return reports


if __name__ == "__main__":
    raise SystemExit(main())
