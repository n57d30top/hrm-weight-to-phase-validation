import unittest
import json
import math

from oqp.future_work.calibration_loop import (
    CALIBRATION_SWEEP_DEFINITIONS,
    run_calibration_demo,
    run_calibration_sweep_analysis_report,
    run_calibration_sweep_report,
    run_synthetic_calibration_loop,
    synthetic_initial_estimate,
)
from oqp.future_work.mesh_mapping import build_mesh_transfer_model
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


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

    def test_stage_4_sweep_output_is_deterministic_and_serializable(self):
        first = run_calibration_sweep_report()
        second = run_calibration_sweep_report()
        self.assertEqual(first, second)
        json.dumps(first, sort_keys=True)

    def test_stage_4_sweep_rows_have_required_fields_and_false_claims(self):
        report = run_calibration_sweep_report()
        required_fields = {
            "preCalibrationRelativeError",
            "postCalibrationRelativeError",
            "improvementRatio",
            "calibrationIterations",
            "convergenceStatus",
            "calibrationFailureReason",
            "sweepParameter",
            "sweepValue",
            "seed",
            "hardwareValidated",
            "foundryCalibrated",
            "measuredTransferMatrixAvailable",
            "productionInferenceReady",
            "hardwareCalibrationClaimed",
        }
        expected_rows = sum(len(values) for values in CALIBRATION_SWEEP_DEFINITIONS.values())
        self.assertEqual(report["rowCount"], expected_rows)
        self.assertEqual(len(report["rows"]), expected_rows)
        for row in report["rows"]:
            self.assertTrue(required_fields.issubset(row))
            self.assertTrue(math.isfinite(row["preCalibrationRelativeError"]))
            self.assertTrue(math.isfinite(row["postCalibrationRelativeError"]))
            self.assertTrue(math.isfinite(row["improvementRatio"]))
            self.assertLessEqual(row["postCalibrationRelativeError"], row["preCalibrationRelativeError"])
            self.assertIn(row["convergenceStatus"], {"improved", "not_improved"})
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])
            self.assertFalse(row["hardwareCalibrationClaimed"])

    def test_stage_4_sweep_analysis_is_deterministic_and_serializable(self):
        first = run_calibration_sweep_analysis_report()
        second = run_calibration_sweep_analysis_report()
        self.assertEqual(first, second)
        json.dumps(first, sort_keys=True)

    def test_stage_4_sweep_analysis_extremes_and_ranking(self):
        analysis = run_calibration_sweep_analysis_report()
        sweep = run_calibration_sweep_report()
        best = min(sweep["rows"], key=lambda row: (row["postCalibrationRelativeError"], row["sweepParameter"], row["sweepValue"]))
        worst = max(sweep["rows"], key=lambda row: (row["postCalibrationRelativeError"], row["sweepParameter"], row["sweepValue"]))
        ranking = analysis["sensitivityRanking"]
        self.assertEqual(analysis["bestCaseRow"], best)
        self.assertEqual(analysis["worstCaseRow"], worst)
        self.assertEqual(analysis["bestCasePostCalibrationRelativeError"], best["postCalibrationRelativeError"])
        self.assertEqual(analysis["worstCasePostCalibrationRelativeError"], worst["postCalibrationRelativeError"])
        self.assertEqual(ranking, sorted(ranking, key=lambda item: (-item["maxImprovementRatio"], item["sweepParameter"])))
        self.assertEqual(len(ranking), len(CALIBRATION_SWEEP_DEFINITIONS))

    def test_stage_4_sweep_analysis_claim_flags_and_blocked_gates(self):
        analysis = run_calibration_sweep_analysis_report()
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])
        self.assertFalse(analysis["hardwareCalibrationClaimed"])
        self.assertFalse(analysis["calibrationUsesMeasuredData"])
        self.assertTrue(analysis["calibrationUsesSyntheticTarget"])
        self.assertTrue(analysis["oracleTargetAvailableInSimulation"])
        self.assertEqual(foundry_calibration_gate(None)["stageStatus"], "blocked")
        self.assertEqual(measured_transfer_matrix_gate(None)["stageStatus"], "blocked")
        self.assertEqual(hardware_benchmark_gate(None)["stageStatus"], "blocked")


if __name__ == "__main__":
    unittest.main()
