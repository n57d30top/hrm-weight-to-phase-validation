#!/usr/bin/env python3
"""Generate the stage 1 SVD demo report."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from oqp.future_work.neural_mapping import run_svd_mapping_demo  # noqa: E402


REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = run_svd_mapping_demo()
    path = REPORT_DIR / "stage-1-svd-demo.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "report": str(path), "stageStatus": report["stageStatus"]}, sort_keys=True))


if __name__ == "__main__":
    main()
