import json
import unittest

from oqp.future_work.rectangular_mapping import (
    build_rectangular_mesh_transfer_model,
    deterministic_rectangular_matrices,
    run_rectangular_matrix_support_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


class HrmRectangularMappingTest(unittest.TestCase):
    def test_tall_matrix_rectangular_model(self):
        matrix = deterministic_rectangular_matrices()["tall_6x4"]
        model = build_rectangular_mesh_transfer_model(matrix, case_id="tall_6x4")
        self.assertEqual(len(model.transfer_matrix), 6)
        self.assertEqual(len(model.transfer_matrix[0]), 4)
        self.assertEqual(model.matrix_rank, 4)
        self.assertEqual(model.effective_rank, 4)
        self.assertTrue(model.padding_applied)
        self.assertFalse(model.truncation_applied)
        self.assertLess(model.ideal_error, 1e-10)
        self.assertLess(model.mesh_error, 0.2)

    def test_wide_matrix_rectangular_model(self):
        matrix = deterministic_rectangular_matrices()["wide_4x6"]
        model = build_rectangular_mesh_transfer_model(matrix, case_id="wide_4x6")
        self.assertEqual(len(model.transfer_matrix), 4)
        self.assertEqual(len(model.transfer_matrix[0]), 6)
        self.assertEqual(model.matrix_rank, 4)
        self.assertEqual(model.effective_rank, 4)
        self.assertTrue(model.padding_applied)
        self.assertFalse(model.truncation_applied)
        self.assertLess(model.ideal_error, 1e-10)
        self.assertLess(model.mesh_error, 0.2)

    def test_rank_deficient_rectangular_model(self):
        matrix = deterministic_rectangular_matrices()["rank_deficient_5x3"]
        model = build_rectangular_mesh_transfer_model(matrix, case_id="rank_deficient_5x3")
        self.assertEqual(len(model.transfer_matrix), 5)
        self.assertEqual(len(model.transfer_matrix[0]), 3)
        self.assertEqual(model.matrix_rank, 2)
        self.assertEqual(model.effective_rank, 2)
        self.assertTrue(model.padding_applied)
        self.assertFalse(model.truncation_applied)
        self.assertLess(model.ideal_error, 1e-10)
        self.assertLess(model.mesh_error, 0.2)

    def test_rectangular_model_is_deterministic(self):
        matrix = deterministic_rectangular_matrices()["tall_6x4"]
        first = build_rectangular_mesh_transfer_model(matrix, case_id="tall_6x4", phase_levels=64)
        second = build_rectangular_mesh_transfer_model(matrix, case_id="tall_6x4", phase_levels=64)
        self.assertEqual(first.transfer_matrix, second.transfer_matrix)
        self.assertEqual(first.left_mesh.phase_settings, second.left_mesh.phase_settings)
        self.assertEqual(first.right_mesh.coupler_settings, second.right_mesh.coupler_settings)

    def test_rectangular_report_schema_and_claim_flags(self):
        report = run_rectangular_matrix_support_report(phase_levels=64)
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["id"], "rectangular-matrix-support")
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_rectangular_mesh_simulation")
        self.assertTrue(report["rectangularLayerSupportImplemented"])
        self.assertEqual(report["caseCount"], 3)
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        for row in report["cases"]:
            self.assertIn("inputShape", row)
            self.assertIn("outputShape", row)
            self.assertIn("matrixRank", row)
            self.assertIn("effectiveRank", row)
            self.assertEqual(row["rectangularMode"], report["rectangularMode"])
            self.assertTrue(row["paddingApplied"])
            self.assertFalse(row["truncationApplied"])
            self.assertLess(row["idealReconstructionError"], 1e-10)
            self.assertGreaterEqual(row["meshConstrainedReconstructionError"], row["idealReconstructionError"])
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])

    def test_hardware_evidence_gates_remain_blocked(self):
        self.assertEqual(foundry_calibration_gate(None)["stageStatus"], "blocked")
        self.assertEqual(measured_transfer_matrix_gate(None)["stageStatus"], "blocked")
        self.assertEqual(hardware_benchmark_gate(None)["stageStatus"], "blocked")


if __name__ == "__main__":
    unittest.main()
