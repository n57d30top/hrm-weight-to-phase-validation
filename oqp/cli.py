"""Command-line interface for HRM weight-to-phase planning reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"
DISCLAIMER = (
    "This is simulation-only output. It is not hardware evidence."
)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hrmwtp",
        description="HRM simulation planning report utilities",
        epilog=DISCLAIMER,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check", help="run make check")
    check_parser.add_argument("--dry-run", action="store_true", help="print the delegated check command without running it")
    subparsers.add_parser("regenerate", help="regenerate reports")
    subparsers.add_parser("summary", help="print validation summary JSON")
    subparsers.add_parser("decision", help="print model-to-HRM decision JSON")
    subparsers.add_parser("portfolio", help="print model portfolio ranking JSON")
    card_parser = subparsers.add_parser("model-card", help="print a model card markdown artifact")
    card_parser.add_argument("model_id", help="model id, for example low_rank_adapter_demo")
    subparsers.add_parser("list-reports", help="list generated report files")
    subparsers.add_parser("doctor", help="print a quick repository health JSON summary")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "check":
        _print_disclaimer()
        if args.dry_run:
            print("Would run: make check")
            return 0
        return subprocess.run(["make", "check"], cwd=ROOT).returncode
    if args.command == "regenerate":
        _print_disclaimer()
        return subprocess.run(["python3", "scripts/run_hrm_neural_validation_ladder.py"], cwd=ROOT).returncode
    if args.command == "summary":
        _print_disclaimer()
        print(_read_json("validation-ladder-summary.json"))
        return 0
    if args.command == "decision":
        _print_disclaimer()
        print(_read_json("model-to-hrm-decision-report.json"))
        return 0
    if args.command == "portfolio":
        _print_disclaimer()
        print(_read_json("model-portfolio-ranking.json"))
        return 0
    if args.command == "model-card":
        _print_disclaimer()
        print(_read_text(Path("model-cards") / f"{args.model_id}.md"))
        return 0
    if args.command == "list-reports":
        _print_disclaimer()
        for path in sorted(REPORT_DIR.rglob("*")):
            if path.is_file():
                print(path.relative_to(ROOT).as_posix())
        return 0
    if args.command == "doctor":
        _print_disclaimer()
        print(json.dumps(_doctor(), indent=2, sort_keys=True))
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


def _read_json(filename: str) -> str:
    path = REPORT_DIR / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(data, indent=2, sort_keys=True)


def _read_text(relative_path: Path) -> str:
    path = REPORT_DIR / relative_path
    if not path.is_file():
        available = sorted(path.stem for path in (REPORT_DIR / "model-cards").glob("*.md"))
        raise SystemExit(f"model card not found: {relative_path.stem}; available: {', '.join(available)}")
    return path.read_text(encoding="utf-8").rstrip()


def _doctor() -> dict[str, object]:
    summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
    stages = {
        stage["stage"]: {
            "stageStatus": stage["stageStatus"],
            "blockers": stage.get("blockers", []),
        }
        for stage in summary["stages"]
    }
    return {
        "ok": True,
        "simulationOnly": True,
        "hardwareValidated": summary["hardwareValidated"],
        "foundryCalibrated": summary["foundryCalibrated"],
        "measuredTransferMatrixAvailable": summary["measuredTransferMatrixAvailable"],
        "productionInferenceReady": summary["productionInferenceReady"],
        "stage5": stages[5],
        "stage6": stages[6],
        "stage7": stages[7],
        "artifactHashesListed": (REPORT_DIR / "ARTIFACTS.sha256").is_file(),
        "dashboardExists": (ROOT / "dashboard" / "index.html").is_file(),
        "reviewerGuideExists": (ROOT / "docs" / "REVIEWER_GUIDE.md").is_file(),
        "quickstartExists": (ROOT / "docs" / "QUICKSTART.md").is_file(),
        "claimBoundary": DISCLAIMER,
    }


def _print_disclaimer() -> None:
    print(DISCLAIMER, file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
