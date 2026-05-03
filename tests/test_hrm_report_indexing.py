import json
import unittest
from pathlib import Path

from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmReportIndexingTest(unittest.TestCase):
    def test_validation_summary_includes_rectangular_support(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("rectangular-matrix-support", reports)
        report = reports["rectangular-matrix-support"]
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_rectangular_mesh_simulation")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertEqual(report["keyMetrics"]["caseCount"], 3)
        self.assertEqual(report["keyMetrics"]["matrixShapes"], [[6, 4], [4, 6], [5, 3]])
        self.assertIn("meshConstrainedReconstructionErrorMax", report["keyMetrics"])
        self.assertIn("errorDeltaMax", report["keyMetrics"])
        self.assertTrue(report["keyMetrics"]["rectangularLayerSupportImplemented"])
        self.assertEqual(report["keyMetrics"]["rectangularMode"], "orthogonal_completion_rectangular_sigma")

    def test_evidence_ledger_includes_rectangular_support(self):
        ledger = json.loads((ROOT / "docs" / "future-work" / "evidence-ledger.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in ledger["entries"]
        }
        self.assertIn("rectangular-matrix-support", reports)
        report = reports["rectangular-matrix-support"]
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_rectangular_mesh_simulation")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])

    def test_artifacts_sha256_covers_all_generated_json_reports(self):
        json_reports = {
            path.relative_to(ROOT).as_posix()
            for path in REPORT_DIR.glob("*.json")
            if path.is_file()
        }
        hashed_reports = set()
        for line in (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].endswith(".json"):
                hashed_reports.add(parts[1])
        self.assertEqual(json_reports - hashed_reports, set())
        self.assertIn("reports/future-work/hrm-neural-mapping/rectangular-matrix-support.json", hashed_reports)

    def test_readme_rectangular_support_is_current(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(readme.split())
        self.assertIn("rectangular-matrix-support.json", normalized)
        self.assertIn("supplemental rectangular support exists", normalized)
        self.assertIn("still no complex/unitary mesh", normalized)
        self.assertIn("still no hardware validation", normalized)
        self.assertNotIn("no rectangular neural layer support", normalized)
        self.assertNotIn("square matrix only", normalized)

    def test_hardware_evidence_gates_remain_blocked(self):
        reports = [
            foundry_calibration_gate(None),
            measured_transfer_matrix_gate(None),
            hardware_benchmark_gate(None),
        ]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])
        for report in reports:
            self.assertFalse(report["hardwareValidated"])
            self.assertFalse(report["foundryCalibrated"])
            self.assertFalse(report["measuredTransferMatrixAvailable"])
            self.assertFalse(report["productionInferenceReady"])


if __name__ == "__main__":
    unittest.main()
