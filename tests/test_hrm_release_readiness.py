import json
import unittest
from pathlib import Path

from oqp.future_work.release_readiness import (
    CLAIM_BOUNDARY,
    render_release_readiness_markdown,
    run_release_readiness_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"
STAGE_FILES = [
    "stage-0-specification.json",
    "stage-1-svd-demo.json",
    "stage-2-mesh-constrained.json",
    "stage-3-perturbation-model.json",
    "stage-4-simulated-calibration.json",
    "stage-5-foundry-calibration-gate.json",
    "stage-6-measured-transfer-matrix-gate.json",
    "stage-7-hardware-benchmark-gate.json",
]


class HrmReleaseReadinessTest(unittest.TestCase):
    def test_release_readiness_report_is_deterministic(self):
        stages, supplemental = _source_reports()
        first = run_release_readiness_report(stages, supplemental)
        second = run_release_readiness_report(stages, supplemental)
        self.assertEqual(first, second)
        self.assertEqual(first["releaseCandidateFor"], "v0.1.0")
        self.assertEqual(first["completedSimulationStageCount"], 5)
        self.assertEqual(first["blockedHardwareGateCount"], 3)
        self.assertFalse(first["hardwareValidated"])
        self.assertFalse(first["foundryCalibrated"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertFalse(first["productionInferenceReady"])

    def test_generated_release_readiness_report_schema_and_flags(self):
        report = _generated_report()
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["id"], "release-readiness-v0.1.0")
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "release_candidate_hardening_audit")
        self.assertEqual(report["releaseCandidateFor"], "v0.1.0")
        self.assertEqual(report["documentationAudit"]["alphaMilestonesListedThrough"], "v0.1.0-alpha.12")
        self.assertTrue(report["reportAudit"]["jsonReportsHashCovered"])
        self.assertEqual(report["reportAudit"]["hardwareValidatedTrueReports"], 0)
        self.assertEqual(report["reportAudit"]["foundryCalibratedTrueReports"], 0)
        self.assertEqual(report["reportAudit"]["measuredTransferMatrixAvailableTrueReports"], 0)
        self.assertEqual(report["reportAudit"]["productionInferenceReadyTrueReports"], 0)
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])

    def test_release_readiness_markdown_contains_boundary_and_blocked_gates(self):
        report = _generated_report()
        markdown = render_release_readiness_markdown(report)
        generated = (REPORT_DIR / "release-readiness-v0.1.0.md").read_text(encoding="utf-8")
        for text in (markdown, generated):
            self.assertIn(CLAIM_BOUNDARY, text)
            self.assertIn("Stage 5", text)
            self.assertIn("Stage 6", text)
            self.assertIn("Stage 7", text)
            self.assertIn("remains blocked", text)

    def test_readme_lists_alpha_milestones_through_alpha_12(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for index in range(1, 13):
            self.assertIn(f"v0.1.0-alpha.{index}", readme)
        self.assertIn("simulation-only", readme)
        self.assertIn("Stage 5, Stage 6, and Stage 7", readme)
        self.assertNotIn("hardware is validated", readme.lower())

    def test_pyproject_version_is_v02_alpha_after_v010_release(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.2.0-alpha.3"', pyproject)

    def test_release_readiness_artifacts_are_hash_listed(self):
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("reports/future-work/hrm-neural-mapping/release-readiness-v0.1.0.json", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/release-readiness-v0.1.0.md", artifacts)

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


def _source_reports():
    stages = [_read_json(filename) for filename in STAGE_FILES]
    supplemental = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(REPORT_DIR.glob("*.json"))
        if path.name not in set(STAGE_FILES)
        and path.name not in {"validation-ladder-summary.json", "release-readiness-v0.1.0.json"}
    ]
    return stages, supplemental


def _generated_report():
    return _read_json("release-readiness-v0.1.0.json")


def _read_json(filename: str):
    return json.loads((REPORT_DIR / filename).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
