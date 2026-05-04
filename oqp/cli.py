"""Command-line interface for HRM weight-to-phase planning reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hrmwtp", description="HRM simulation planning report utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="run make check")
    subparsers.add_parser("regenerate", help="regenerate reports")
    subparsers.add_parser("summary", help="print validation summary JSON")
    subparsers.add_parser("decision", help="print model-to-HRM decision JSON")
    subparsers.add_parser("list-reports", help="list generated report files")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "check":
        return subprocess.run(["make", "check"], cwd=ROOT).returncode
    if args.command == "regenerate":
        return subprocess.run(["python3", "scripts/run_hrm_neural_validation_ladder.py"], cwd=ROOT).returncode
    if args.command == "summary":
        print(_read_json("validation-ladder-summary.json"))
        return 0
    if args.command == "decision":
        print(_read_json("model-to-hrm-decision-report.json"))
        return 0
    if args.command == "list-reports":
        for path in sorted(REPORT_DIR.glob("*")):
            if path.is_file():
                print(path.relative_to(ROOT).as_posix())
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


def _read_json(filename: str) -> str:
    path = REPORT_DIR / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(data, indent=2, sort_keys=True)


if __name__ == "__main__":
    raise SystemExit(main())
