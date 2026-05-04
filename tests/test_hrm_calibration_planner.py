import json
import unittest
from pathlib import Path

from oqp.future_work.calibration_planner import (
    render_transfer_matrix_assimilation_protocol,
    run_calibration_plan_report,
    run_transfer_matrix_assimilation_plan_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmCalibrationPlannerTest(unittest.TestCase):
    def test_calibration_plan_is_deterministic_and_plan_only(self):
        first = run_calibration_plan_report()
        second = run_calibration_plan_report()
        self.assertEqual(first, second)
        self.assertTrue(first["calibrationPlanOnly"])
        self.assertFalse(first["assimilationPlanOnly"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertEqual(first["stageStatus"], "blocked")
        self.assertGreater(first["measurementVectorCount"], 0)
        self.assertGreater(first["acceptanceCriteriaCount"], 0)

    def test_assimilation_plan_is_deterministic_and_plan_only(self):
        first = run_transfer_matrix_assimilation_plan_report()
        second = run_transfer_matrix_assimilation_plan_report()
        self.assertEqual(first, second)
        self.assertFalse(first["calibrationPlanOnly"])
        self.assertTrue(first["assimilationPlanOnly"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertEqual(first["stageStatus"], "blocked")
        self.assertIn("no measured matrix is included", first["limitations"])

    def test_protocol_contains_required_sections_without_measured_matrix(self):
        protocol = render_transfer_matrix_assimilation_protocol()
        self.assertIn("Calibration Sequence", protocol)
        self.assertIn("Assimilation Steps", protocol)
        self.assertIn("Pass/Fail Criteria", protocol)
        self.assertIn("no measured transfer matrix is available", protocol)

    def test_generated_reports_are_hash_covered_and_flags_false(self):
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        for filename in ["calibration-plan.json", "transfer-matrix-assimilation-plan.json"]:
            report = json.loads((REPORT_DIR / filename).read_text(encoding="utf-8"))
            json.dumps(report, sort_keys=True)
            self.assertFalse(report["hardwareValidated"])
            self.assertFalse(report["foundryCalibrated"])
            self.assertFalse(report["measuredTransferMatrixAvailable"])
            self.assertFalse(report["productionInferenceReady"])
            self.assertIn(f"reports/future-work/hrm-neural-mapping/{filename}", artifacts)
        self.assertIn("docs/future-work/transfer-matrix-assimilation-protocol.md", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [
            foundry_calibration_gate(None),
            measured_transfer_matrix_gate(None),
            hardware_benchmark_gate(None),
        ]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
