import json
import unittest
from pathlib import Path

from oqp.future_work.hardware_requirements import (
    run_hardware_requirements_analysis_report,
    run_hardware_requirements_envelope_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmHardwareRequirementsTest(unittest.TestCase):
    def test_requirements_are_deterministic_and_simulation_derived(self):
        first = run_hardware_requirements_envelope_report()
        second = run_hardware_requirements_envelope_report()
        self.assertEqual(first, second)
        self.assertTrue(first["simulationDerivedOnly"])
        self.assertEqual(first["targetOutputRelativeErrorValues"], [0.10, 0.05, 0.02])
        self.assertEqual(first["rowCount"], 12)
        self.assertTrue(any(row["requirementStatus"] == "not_met_in_simulated_sweep" for row in first["requirements"]))
        for row in first["requirements"]:
            self.assertTrue(row["simulationDerivedOnly"])
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])

    def test_stricter_targets_do_not_loosen_requirements_for_met_rows(self):
        envelope = run_hardware_requirements_envelope_report()
        identity_rows = [
            row for row in envelope["requirements"]
            if row["caseId"] == "identity_4x4" and row["requirementStatus"] == "met_in_simulated_envelope"
        ]
        by_target = {row["targetError"]: row for row in identity_rows}
        self.assertGreaterEqual(by_target[0.02]["requiredPhaseResolutionBits"], by_target[0.05]["requiredPhaseResolutionBits"])
        self.assertGreaterEqual(by_target[0.05]["requiredPhaseResolutionBits"], by_target[0.10]["requiredPhaseResolutionBits"])
        self.assertLessEqual(by_target[0.02]["maxPhaseNoiseSigmaRad"], by_target[0.05]["maxPhaseNoiseSigmaRad"])
        self.assertLessEqual(by_target[0.05]["maxPhaseNoiseSigmaRad"], by_target[0.10]["maxPhaseNoiseSigmaRad"])

    def test_analysis_counts_match_envelope(self):
        envelope = run_hardware_requirements_envelope_report()
        analysis = run_hardware_requirements_analysis_report()
        met = sum(1 for row in envelope["requirements"] if row["requirementStatus"] == "met_in_simulated_envelope")
        unmet = sum(1 for row in envelope["requirements"] if row["requirementStatus"] != "met_in_simulated_envelope")
        self.assertEqual(analysis["metRequirementCount"], met)
        self.assertEqual(analysis["unmetRequirementCount"], unmet)
        self.assertGreater(analysis["unmetRequirementCount"], 0)
        self.assertTrue(analysis["simulationDerivedOnly"])

    def test_generated_reports_are_serializable_and_hash_covered(self):
        for filename in ["hardware-requirements-envelope.json", "hardware-requirements-analysis.json"]:
            path = REPORT_DIR / filename
            report = json.loads(path.read_text(encoding="utf-8"))
            json.dumps(report, sort_keys=True)
            self.assertFalse(report["hardwareValidated"])
            self.assertFalse(report["foundryCalibrated"])
            self.assertFalse(report["measuredTransferMatrixAvailable"])
            self.assertFalse(report["productionInferenceReady"])
            artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
            self.assertIn(f"reports/future-work/hrm-neural-mapping/{filename}", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [
            foundry_calibration_gate(None),
            measured_transfer_matrix_gate(None),
            hardware_benchmark_gate(None),
        ]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
