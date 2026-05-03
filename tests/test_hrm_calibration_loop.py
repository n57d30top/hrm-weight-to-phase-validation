import unittest

from oqp.future_work.calibration_loop import run_calibration_demo, run_synthetic_calibration_loop, synthetic_initial_estimate
from oqp.future_work.mesh_mapping import build_mesh_transfer_model


class HrmCalibrationLoopTest(unittest.TestCase):
    def test_synthetic_calibration_improves_or_does_not_worsen_error(self):
        model = build_mesh_transfer_model()
        initial = synthetic_initial_estimate(model.target_matrix, seed=23, noise_std=0.04)
        result = run_synthetic_calibration_loop(model.target_matrix, initial)
        self.assertLessEqual(result.post_calibration_error, result.pre_calibration_error)
        self.assertEqual(result.calibration_mode, "synthetic_simulation")
        self.assertFalse(result.measured_transfer_matrix_available)

    def test_stage_4_report_schema_and_claim_flags(self):
        report = run_calibration_demo()
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["calibrationMode"], "synthetic_simulation")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertFalse(report["calibrationUsesMeasuredData"])
        self.assertTrue(report["calibrationUsesSyntheticTarget"])
        self.assertTrue(report["oracleTargetAvailableInSimulation"])
        self.assertFalse(report["hardwareCalibrationClaimed"])
        self.assertLessEqual(report["postCalibrationRelativeError"], report["preCalibrationRelativeError"])


if __name__ == "__main__":
    unittest.main()
