import unittest

from oqp.future_work.mesh_mapping import build_mesh_transfer_model
from oqp.future_work.perturbation_model import PerturbationConfig, apply_perturbations, run_perturbation_demo


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


if __name__ == "__main__":
    unittest.main()
