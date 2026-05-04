import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmPartnerReviewTest(unittest.TestCase):
    def test_partner_readiness_report_exists_and_flags_are_false(self):
        report = json.loads((REPORT_DIR / "partner-readiness-report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["readinessForExternalReview"])
        self.assertFalse(report["readinessForHardwareClaim"])
        self.assertFalse(report["readinessForFoundryClaim"])
        self.assertFalse(report["readinessForMeasuredTransferMatrixClaim"])
        self.assertFalse(report["readinessForProductionInferenceClaim"])
        self.assertIn("foundry calibrated device model", report["missingEvidence"])
        self.assertIn("integrated photonics reviewer", report["recommendedNextPartnerType"])
        self.assert_false_claim_flags(report)

    def test_external_review_checklist_exists_without_implying_review(self):
        report = json.loads((REPORT_DIR / "external-review-checklist.json").read_text(encoding="utf-8"))
        self.assertFalse(report["reviewHasOccurred"])
        self.assertIn("pass", report["allowedReviewerStatuses"])
        self.assertIn("needs clarification", report["allowedReviewerStatuses"])
        self.assertIn("blocked by missing evidence", report["allowedReviewerStatuses"])
        self.assertGreaterEqual(len(report["checklistSections"]), 8)
        self.assert_false_claim_flags(report)

    def test_model_cards_and_portfolio_explainer_are_generated(self):
        card_dir = REPORT_DIR / "model-cards"
        expected = {
            "tiny_mlp.md",
            "projection_chain.md",
            "low_rank_adapter_demo.md",
            "sparse_linear_demo.md",
            "transformer_block_manifest_only.md",
        }
        self.assertEqual({path.name for path in card_dir.glob("*.md")}, expected)
        card = (card_dir / "low_rank_adapter_demo.md").read_text(encoding="utf-8")
        self.assertIn("Model Card: low_rank_adapter_demo", card)
        self.assertIn("simulation-only", card)
        explainer = (REPORT_DIR / "model-portfolio-explainer.md").read_text(encoding="utf-8")
        self.assertIn("Best model: `low_rank_adapter_demo`", explainer)
        self.assertIn("Worst model: `transformer_block_manifest_only`", explainer)

    def test_reproducibility_capsule_contains_expected_commands(self):
        report = json.loads((REPORT_DIR / "reproducibility-capsule.json").read_text(encoding="utf-8"))
        commands = report["exactCommandsToReproduce"]
        self.assertIn("make check", commands)
        self.assertIn("python3 scripts/hrmwtp.py doctor", commands)
        self.assertIn("python3 scripts/check_claim_boundary.py", commands)
        self.assertEqual(report["expectedTestCount"], 186)
        self.assertEqual(report["expectedReportCount"], 48)
        self.assert_false_claim_flags(report)

    def test_solo_completion_audit_keeps_hardware_validation_zero(self):
        report = json.loads((REPORT_DIR / "solo-completion-audit.json").read_text(encoding="utf-8"))
        self.assertGreater(report["softwareCompletenessEstimate"], 0.9)
        self.assertGreater(report["planningToolkitCompletenessEstimate"], 0.9)
        self.assertEqual(report["hardwareValidationCompletenessEstimate"], 0.0)
        self.assertLessEqual(report["chipReadinessEstimate"], 0.05)
        self.assertFalse(report["readyForHardwareClaims"])
        self.assert_false_claim_flags(report)

    def test_alpha3_readiness_report_exists(self):
        report = json.loads((REPORT_DIR / "v0.2.0-alpha3-readiness.json").read_text(encoding="utf-8"))
        self.assertEqual(report["releaseCandidateFor"], "v0.2.0-alpha.3")
        self.assertEqual(report["partnerReadinessPackStatus"], "complete")
        self.assertEqual(report["externalReviewChecklistStatus"], "complete_not_reviewed")
        self.assertEqual(len(report["blockedHardwareGates"]), 3)
        self.assertTrue(report["readyToTagIfVerificationPasses"])
        self.assert_false_claim_flags(report)

    def test_summary_and_ledger_index_partner_review_reports(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        ledger = json.loads((ROOT / "docs" / "future-work" / "evidence-ledger.json").read_text(encoding="utf-8"))
        summary_ids = {report["id"] for report in summary["supplementalReports"]}
        ledger_ids = {report["id"] for report in ledger["entries"]}
        expected = {
            "partner-readiness-report",
            "external-review-checklist",
            "reproducibility-capsule",
            "solo-completion-audit",
            "v0.2.0-alpha3-readiness",
        }
        self.assertTrue(expected.issubset(summary_ids))
        self.assertTrue(expected.issubset(ledger_ids))

    def test_hardware_gates_remain_blocked_in_public_summary(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        stages = {stage["stage"]: stage for stage in summary["stages"]}
        self.assertEqual(stages[5]["stageStatus"], "blocked")
        self.assertEqual(stages[6]["stageStatus"], "blocked")
        self.assertEqual(stages[7]["stageStatus"], "blocked")
        self.assert_false_claim_flags(summary)

    def assert_false_claim_flags(self, report):
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])


if __name__ == "__main__":
    unittest.main()
