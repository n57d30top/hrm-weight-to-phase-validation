import json
import math
import unittest
from pathlib import Path

from oqp.future_work.error_budget import render_error_budget_markdown, run_error_budget_report
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmErrorBudgetTest(unittest.TestCase):
    def test_error_budget_is_deterministic(self):
        first = run_error_budget_report()
        second = run_error_budget_report()
        self.assertEqual(first, second)
        self.assertTrue(first["simulationOnly"])
        self.assertFalse(first["physicalAccuracyClaimed"])
        self.assertEqual(len(first["componentErrors"]), 7)
        self.assertTrue(first["additiveModelUsed"])
        self.assertTrue(first["rssModelUsed"])
        self.assertTrue(first["conservativeMaxModelUsed"])
        for value in first["combinedErrorEnvelope"].values():
            self.assertGreaterEqual(value, 0.0)
            self.assertTrue(math.isfinite(value))

    def test_dominant_contributor_matches_component_data(self):
        report = run_error_budget_report()
        dominant = max(report["componentErrors"], key=lambda row: row["errorValue"])
        self.assertEqual(report["dominantErrorContributor"], dominant)
        markdown = render_error_budget_markdown(report)
        self.assertIn("simulation-only error budget", markdown)
        self.assertIn("not a hardware accuracy claim", markdown)

    def test_generated_report_and_markdown_are_hash_covered(self):
        report = json.loads((REPORT_DIR / "error-budget-report.json").read_text(encoding="utf-8"))
        json.dumps(report, sort_keys=True)
        self.assertTrue(report["simulationOnly"])
        self.assertFalse(report["physicalAccuracyClaimed"])
        self.assertFalse(report["hardwareValidated"])
        markdown = (REPORT_DIR / "error-budget-analysis.md").read_text(encoding="utf-8")
        self.assertIn("not a hardware accuracy claim", markdown)
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("reports/future-work/hrm-neural-mapping/error-budget-report.json", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/error-budget-analysis.md", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [
            foundry_calibration_gate(None),
            measured_transfer_matrix_gate(None),
            hardware_benchmark_gate(None),
        ]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
