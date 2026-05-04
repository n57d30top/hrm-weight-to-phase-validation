import json
import unittest
from pathlib import Path

from oqp.future_work.decision_report import (
    ALLOWED_DECISIONS,
    DISCLAIMER,
    render_model_to_hrm_decision_markdown,
    run_model_to_hrm_decision_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmDecisionReportTest(unittest.TestCase):
    def test_decision_report_is_deterministic(self):
        first = run_model_to_hrm_decision_report()
        second = run_model_to_hrm_decision_report()
        self.assertEqual(first, second)
        self.assertIn(first["decision"], ALLOWED_DECISIONS)
        self.assertEqual(first["decision"], "blocked_by_missing_hardware_evidence")
        self.assertTrue(first["simulationOnly"])
        self.assertTrue(first["decisionIsNotHardwareValidation"])
        self.assertFalse(first["hardwareValidated"])
        self.assertFalse(first["foundryCalibrated"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertFalse(first["productionInferenceReady"])

    def test_markdown_starts_with_simulation_only_disclaimer(self):
        report = run_model_to_hrm_decision_report()
        markdown = render_model_to_hrm_decision_markdown(report)
        self.assertTrue(markdown.startswith(DISCLAIMER))
        generated = (REPORT_DIR / "model-to-hrm-decision-report.md").read_text(encoding="utf-8")
        self.assertTrue(generated.startswith(DISCLAIMER))

    def test_missing_hardware_evidence_is_listed(self):
        report = run_model_to_hrm_decision_report()
        self.assertIn("foundry-calibrated device model", report["missingEvidence"])
        self.assertIn("measured transfer matrix", report["missingEvidence"])
        self.assertIn("hardware benchmark", report["missingEvidence"])
        self.assertGreater(report["suitabilityScore"], 0.0)

    def test_generated_report_is_serializable_and_hash_covered(self):
        report = json.loads((REPORT_DIR / "model-to-hrm-decision-report.json").read_text(encoding="utf-8"))
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["decision"], "blocked_by_missing_hardware_evidence")
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("reports/future-work/hrm-neural-mapping/model-to-hrm-decision-report.json", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-to-hrm-decision-report.md", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [
            foundry_calibration_gate(None),
            measured_transfer_matrix_gate(None),
            hardware_benchmark_gate(None),
        ]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
