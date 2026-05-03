import json
import math
import unittest

from oqp.future_work.mesh_mapping import build_mesh_transfer_model
from oqp.future_work.perturbation_model import (
    SWEEP_DEFINITIONS,
    PerturbationConfig,
    apply_perturbations,
    run_perturbation_demo,
    run_perturbation_sweep_analysis_report,
    run_perturbation_sweep_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


class HrmPerturbationModelTest(unittest.TestCase):
    def test_seeded_perturbations_are_deterministic(self):
        model = build_mesh_transfer_model()
        config = PerturbationConfig(seed=17)
        first = apply_perturbations(model, config)
        second = apply_perturbations(model, config)
        self.assertEqual(first.transfer_matrix, second.transfer_matrix)
        self.assertEqual(first.perturbed_error, second.perturbed_error)

    def test_insertion_loss_does_not_improve_error_under_controlled_config(self):
        model = build_mesh_transfer_model()
        no_loss = apply_perturbations(model, PerturbationConfig(
            phase_quantization_levels=64,
            phase_noise_std_rad=0.0,
            insertion_loss_db=0.0,
            coupler_imbalance=0.0,
            thermal_drift_rad_per_stage=0.0,
            detector_noise_std=0.0,
        ))
        with_loss = apply_perturbations(model, PerturbationConfig(
            phase_quantization_levels=64,
            phase_noise_std_rad=0.0,
            insertion_loss_db=1.0,
            coupler_imbalance=0.0,
            thermal_drift_rad_per_stage=0.0,
            detector_noise_std=0.0,
        ))
        self.assertGreaterEqual(with_loss.perturbed_error, no_loss.perturbed_error)

    def test_stage_3_report_schema_and_claim_flags(self):
        report = run_perturbation_demo()
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "uncalibrated_perturbation_simulation")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertFalse(report["physicalAccuracyClaimed"])

    def test_stage_3_sweep_output_is_deterministic_and_serializable(self):
        first = run_perturbation_sweep_report()
        second = run_perturbation_sweep_report()
        self.assertEqual(first, second)
        json.dumps(first, sort_keys=True)

    def test_stage_3_sweep_rows_have_required_fields_and_finite_errors(self):
        report = run_perturbation_sweep_report()
        required_fields = {
            "baselineMeshRelativeError",
            "perturbedRelativeError",
            "errorDelta",
            "sweepParameter",
            "sweepValue",
            "seed",
            "evidenceLevel",
            "hardwareValidated",
            "foundryCalibrated",
            "measuredTransferMatrixAvailable",
            "productionInferenceReady",
        }
        expected_rows = sum(len(values) for values in SWEEP_DEFINITIONS.values())
        self.assertEqual(report["rowCount"], expected_rows)
        self.assertEqual(len(report["rows"]), expected_rows)
        for row in report["rows"]:
            self.assertTrue(required_fields.issubset(row))
            self.assertTrue(math.isfinite(row["baselineMeshRelativeError"]))
            self.assertTrue(math.isfinite(row["perturbedRelativeError"]))
            self.assertTrue(math.isfinite(row["errorDelta"]))
            self.assertEqual(row["evidenceLevel"], "uncalibrated_perturbation_simulation")
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])

    def test_stage_3_sweep_keeps_hardware_gates_blocked(self):
        self.assertEqual(foundry_calibration_gate(None)["stageStatus"], "blocked")
        self.assertEqual(measured_transfer_matrix_gate(None)["stageStatus"], "blocked")
        self.assertEqual(hardware_benchmark_gate(None)["stageStatus"], "blocked")

    def test_stage_3_sweep_analysis_is_deterministic_and_serializable(self):
        first = run_perturbation_sweep_analysis_report()
        second = run_perturbation_sweep_analysis_report()
        self.assertEqual(first, second)
        json.dumps(first, sort_keys=True)

    def test_stage_3_sweep_analysis_ranking_and_extremes(self):
        analysis = run_perturbation_sweep_analysis_report()
        sweep = run_perturbation_sweep_report()
        worst = max(sweep["rows"], key=lambda row: (row["errorDelta"], row["sweepParameter"], row["sweepValue"]))
        best = min(sweep["rows"], key=lambda row: (row["perturbedRelativeError"], row["sweepParameter"], row["sweepValue"]))
        ranking = analysis["sensitivityRanking"]
        self.assertEqual(analysis["worstCaseRow"], worst)
        self.assertEqual(analysis["bestCaseRow"], best)
        self.assertEqual(analysis["worstCaseErrorDelta"], worst["errorDelta"])
        self.assertEqual(analysis["bestCasePerturbedRelativeError"], best["perturbedRelativeError"])
        self.assertEqual(ranking, sorted(ranking, key=lambda item: (-item["maxErrorDelta"], item["sweepParameter"])))
        self.assertEqual(len(ranking), len(SWEEP_DEFINITIONS))

    def test_stage_3_sweep_analysis_control_and_claim_flags(self):
        analysis = run_perturbation_sweep_analysis_report()
        control = analysis["controlSummary"]
        self.assertEqual(control["id"], "control_all_perturbations_disabled")
        self.assertTrue(control["controlMatchesBaselineWithinTolerance"])
        self.assertAlmostEqual(control["baselineMeshRelativeError"], control["controlRelativeError"], places=12)
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])
        self.assertFalse(analysis["physicalAccuracyClaimed"])
        self.assertFalse(control["hardwareValidated"])
        self.assertFalse(control["foundryCalibrated"])
        self.assertFalse(control["measuredTransferMatrixAvailable"])
        self.assertFalse(control["productionInferenceReady"])


if __name__ == "__main__":
    unittest.main()
