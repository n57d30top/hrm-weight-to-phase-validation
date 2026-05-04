import json
import unittest
from pathlib import Path

from oqp.future_work.rc_readiness import CLAIM_BOUNDARY, render_rc1_readiness_markdown
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmRcReadinessTest(unittest.TestCase):
    def test_generated_rc1_readiness_report_schema_and_flags(self):
        report = _generated_report()
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["id"], "v0.1.0-rc1-readiness")
        self.assertEqual(report["releaseCandidateFor"], "v0.1.0")
        self.assertEqual(report["stageStatus"], "complete")
        self.assertGreaterEqual(report["includedCapabilityCount"], 10)
        self.assertGreaterEqual(report["decisionReportCapabilityCount"], 6)
        self.assertEqual(report["blockedHardwareGateCount"], 3)
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])

    def test_markdown_and_roadmap_are_generated(self):
        report = _generated_report()
        markdown = render_rc1_readiness_markdown(report)
        generated = (REPORT_DIR / "v0.1.0-rc1-readiness.md").read_text(encoding="utf-8")
        for text in (markdown, generated):
            self.assertIn(CLAIM_BOUNDARY, text)
            self.assertIn("v0.2 Recommended Work", text)
            self.assertIn("Stage 5", text)
            self.assertIn("Stage 6", text)
            self.assertIn("Stage 7", text)
        roadmap = (ROOT / "docs" / "ROADMAP-v0.2.md").read_text(encoding="utf-8")
        self.assertIn("v0.2 Roadmap", roadmap)
        self.assertIn("optional PyTorch export adapter", roadmap)
        self.assertIn("Stage 5, Stage 6, and Stage 7 remain blocked", roadmap)

    def test_rc_artifacts_are_hash_covered(self):
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("reports/future-work/hrm-neural-mapping/v0.1.0-rc1-readiness.json", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/v0.1.0-rc1-readiness.md", artifacts)
        self.assertIn("docs/ROADMAP-v0.2.md", artifacts)

    def test_pyproject_version_is_rc1(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.1.0-rc.1"', pyproject)

    def test_hardware_gates_remain_blocked(self):
        reports = [
            foundry_calibration_gate(None),
            measured_transfer_matrix_gate(None),
            hardware_benchmark_gate(None),
        ]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


def _generated_report():
    return json.loads((REPORT_DIR / "v0.1.0-rc1-readiness.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
