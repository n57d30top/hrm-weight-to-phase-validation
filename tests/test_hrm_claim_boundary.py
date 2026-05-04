import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from scripts.check_claim_boundary import (
    check_json_flags,
    check_text_for_forbidden_claims,
    main as claim_boundary_main,
)


ROOT = Path(__file__).resolve().parents[1]


class HrmClaimBoundaryGuardTest(unittest.TestCase):
    def test_guard_catches_forbidden_positive_claim_phrase(self):
        findings = check_text_for_forbidden_claims(Path("sample.md"), "This project has quantum advantage.\n")
        self.assertTrue(findings)
        self.assertIn("quantum advantage", findings[0])

    def test_guard_allows_explicit_negative_claim_boundary_context(self):
        text = "Claim boundary: this project does not claim quantum advantage.\n"
        findings = check_text_for_forbidden_claims(Path("sample.md"), text)
        self.assertEqual(findings, [])

    def test_guard_catches_strict_true_flags_in_json(self):
        text = json.dumps({
            "hardwareValidated": True,
            "foundryCalibrated": False,
            "measuredTransferMatrixAvailable": False,
            "productionInferenceReady": False,
        })
        findings = check_json_flags(Path("sample.json"), text)
        self.assertEqual(len(findings), 1)
        self.assertIn("hardwareValidated=true", findings[0])

    def test_guard_passes_current_public_docs_and_reports(self):
        self.assertEqual(claim_boundary_main(), 0)

    def test_guard_main_fails_on_temp_public_file_with_positive_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.md"
            path.write_text("This review says the system is production inference ready.\n", encoding="utf-8")
            with redirect_stderr(StringIO()):
                self.assertEqual(claim_boundary_main([path]), 1)


if __name__ == "__main__":
    unittest.main()
