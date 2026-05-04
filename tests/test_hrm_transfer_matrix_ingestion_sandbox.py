import json
import unittest
from pathlib import Path

from oqp.future_work.transfer_matrix_ingestion_sandbox import run_transfer_matrix_ingestion_sandbox_report
from oqp.future_work.validation_gates import foundry_calibration_gate, hardware_benchmark_gate, measured_transfer_matrix_gate


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmTransferMatrixIngestionSandboxTest(unittest.TestCase):
    def test_sandbox_report_is_deterministic_and_synthetic_only(self):
        first = run_transfer_matrix_ingestion_sandbox_report()
        second = run_transfer_matrix_ingestion_sandbox_report()
        self.assertEqual(first, second)
        self.assertEqual(first["stageStatus"], "blocked")
        self.assertTrue(first["syntheticFixtureOnly"])
        self.assertFalse(first["publicMeasuredEvidence"])
        self.assertFalse(first["measurementDataClaimed"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertTrue(first["validationPassed"])

    def test_comparison_is_reported_without_stage_6_evidence(self):
        report = run_transfer_matrix_ingestion_sandbox_report()
        self.assertGreaterEqual(report["comparison"]["targetVsSyntheticRelativeFrobeniusError"], 0.0)
        self.assertTrue(report["comparison"]["comparisonIsSyntheticOnly"])
        self.assertIn("no_measured_hrm_transfer_matrix", report["blockers"])

    def test_generated_report_and_fixture_are_hash_covered(self):
        report = json.loads((REPORT_DIR / "transfer-matrix-ingestion-sandbox.json").read_text(encoding="utf-8"))
        json.dumps(report, sort_keys=True)
        self.assertTrue(report["syntheticFixtureOnly"])
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("reports/future-work/hrm-neural-mapping/transfer-matrix-ingestion-sandbox.json", artifacts)
        self.assertIn("fixtures/transfer-matrix-sandbox/synthetic-transfer-matrix.json", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [foundry_calibration_gate(None), measured_transfer_matrix_gate(None), hardware_benchmark_gate(None)]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
