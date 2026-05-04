import csv
import json
import unittest
from pathlib import Path

from oqp.future_work.review_pack import (
    CLAIM_BOUNDARY_SENTENCE,
    render_review_pack_markdown,
    render_review_pack_metrics_csv,
    run_review_pack_summary_report,
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


class HrmReviewPackTest(unittest.TestCase):
    def test_review_pack_summary_is_deterministic(self):
        stages, supplemental = _source_reports()
        first = run_review_pack_summary_report(stages, supplemental)
        second = run_review_pack_summary_report(stages, supplemental)
        self.assertEqual(first, second)
        self.assertEqual(first["id"], "review-pack-summary")
        self.assertEqual(first["evidenceLevel"], "simulation_review_pack")
        self.assertEqual(first["stageStatus"], "complete")
        self.assertEqual(first["reportCount"], len(stages) + len(supplemental) + 1)
        self.assertFalse(first["hardwareValidated"])
        self.assertFalse(first["foundryCalibrated"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertFalse(first["productionInferenceReady"])

    def test_review_pack_includes_all_stage_statuses_and_blocked_gates(self):
        summary = _generated_summary()
        status_by_stage = {row["stage"]: row["stageStatus"] for row in summary["stageStatusTable"]}
        self.assertEqual(status_by_stage, {
            0: "complete",
            1: "complete",
            2: "complete",
            3: "complete",
            4: "complete",
            5: "blocked",
            6: "blocked",
            7: "blocked",
        })
        blocked = {gate["stage"]: gate for gate in summary["blockedGates"]}
        self.assertEqual(set(blocked), {5, 6, 7})
        self.assertEqual(blocked[5]["blockerReason"], "no_foundry_calibrated_device_model")
        self.assertEqual(blocked[6]["blockerReason"], "no_measured_hrm_transfer_matrix")
        self.assertEqual(blocked[7]["blockerReason"], "no_end_to_end_hardware_benchmark")

    def test_review_pack_markdown_contains_claim_boundary(self):
        summary = _generated_summary()
        markdown = render_review_pack_markdown(summary)
        generated = (REPORT_DIR / "review-pack.md").read_text(encoding="utf-8")
        for text in (markdown, generated):
            self.assertIn(CLAIM_BOUNDARY_SENTENCE, text)
            self.assertIn("Stage 5", text)
            self.assertIn("Stage 6", text)
            self.assertIn("Stage 7", text)
            self.assertIn("remains blocked", text)

    def test_review_pack_metrics_csv_is_valid(self):
        summary = _generated_summary()
        rendered_rows = list(csv.DictReader(render_review_pack_metrics_csv(summary).splitlines()))
        generated_rows = list(csv.DictReader((REPORT_DIR / "review-pack-metrics.csv").read_text(encoding="utf-8").splitlines()))
        self.assertEqual(rendered_rows, generated_rows)
        self.assertGreater(len(generated_rows), 5)
        self.assertEqual(
            set(generated_rows[0]),
            {"reportId", "metricName", "metricValue", "evidenceLevel", "claimBoundaryNote"},
        )
        for row in generated_rows:
            self.assertEqual(row["claimBoundaryNote"], "simulation-only; not hardware evidence")

    def test_review_pack_supplemental_reports_include_expected_alpha_artifacts(self):
        summary = _generated_summary()
        reports = {report["id"] for report in summary["supplementalReportIndex"]}
        expected = {
            "rectangular-matrix-support",
            "complex-unitary-mesh-support",
            "matrix-family-benchmark",
            "matrix-family-analysis",
            "layer-stack-inference-demo",
            "layer-stack-error-analysis",
            "model-weight-import-demo",
            "model-weight-eligibility-analysis",
            "scaling-benchmark",
            "scaling-analysis",
        }
        self.assertTrue(expected.issubset(reports))

    def test_review_pack_artifacts_are_hash_listed(self):
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("reports/future-work/hrm-neural-mapping/review-pack-summary.json", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/review-pack.md", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/review-pack-metrics.csv", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/review-pack-stage-table.md", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/review-pack-limitations.md", artifacts)

    def test_review_pack_artifacts_have_no_local_path_fragments(self):
        bad_tokens = [
            "/" + "Users" + "/",
            "/" + "home" + "/",
            "Desktop" + "/",
            "file:" + "//",
        ]
        for filename in [
            "review-pack-summary.json",
            "review-pack.md",
            "review-pack-metrics.csv",
            "review-pack-stage-table.md",
            "review-pack-limitations.md",
        ]:
            text = (REPORT_DIR / filename).read_text(encoding="utf-8")
            for token in bad_tokens:
                self.assertNotIn(token, text)

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
        and path.name not in {"validation-ladder-summary.json", "review-pack-summary.json"}
    ]
    return stages, supplemental


def _generated_summary():
    return _read_json("review-pack-summary.json")


def _read_json(filename: str):
    return json.loads((REPORT_DIR / filename).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
