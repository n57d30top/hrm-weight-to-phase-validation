import tempfile
import unittest
from pathlib import Path

from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
    stage_0_specification_gate,
)


class HrmValidationGatesTest(unittest.TestCase):
    def test_foundry_gate_blocks_without_foundry_data(self):
        report = foundry_calibration_gate(None)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertFalse(report["foundryCalibrated"])
        self.assertEqual(report["blockerReason"], "no_foundry_calibrated_device_model")

    def test_measured_transfer_matrix_gate_blocks_without_measured_data(self):
        report = measured_transfer_matrix_gate(None)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertEqual(report["blockerReason"], "no_measured_hrm_transfer_matrix")

    def test_hardware_benchmark_gate_blocks_without_required_evidence(self):
        report = hardware_benchmark_gate(None)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertFalse(report["productionInferenceReady"])
        self.assertEqual(report["blockerReason"], "no_end_to_end_hardware_benchmark")

    def test_stage_0_gate_requires_claim_boundaries_and_forbidden_phrase_absence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "spec.md"
            path.write_text(
                "\n".join([
                    "Do not claim hardware-native intelligence",
                    "Do not claim autonomous cognition",
                    "Do not claim quantum consciousness",
                    "Do not claim power-free computation",
                    "Do not claim quantum advantage",
                    "Do not claim production inference readiness",
                    "Do not claim hardware validation unless measured hardware data is present",
                    "Do not claim foundry calibration unless foundry-calibrated S-parameters or equivalent foundry device models are present",
                    "Do not claim measured transfer matrices unless real measured transfer-matrix artifacts are present",
                    "Do not promote this future-work track into the main hardware readiness score",
                ]),
                encoding="utf-8",
            )
            report = stage_0_specification_gate(path)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertFalse(report["forbiddenHardwareCompilationPhrasePresent"])
        self.assertFalse(report["hardwareValidated"])


if __name__ == "__main__":
    unittest.main()
