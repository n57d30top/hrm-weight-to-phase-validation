import unittest

from oqp.future_work.mesh_mapping import build_mesh_transfer_model, run_mesh_constrained_demo
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


class HrmMeshMappingTest(unittest.TestCase):
    def test_mesh_constrained_error_is_reported_against_ideal_error(self):
        model = build_mesh_transfer_model(phase_levels=64)
        self.assertLess(model.ideal_error, 1e-10)
        self.assertGreaterEqual(model.mesh_error, model.ideal_error)
        self.assertLess(model.mesh_error, 0.25)

    def test_fixed_input_matrix_produces_deterministic_output(self):
        matrix = [
            [0.33, -0.11, 0.27],
            [0.08, 0.49, -0.21],
            [-0.40, 0.22, 0.57],
        ]
        first = build_mesh_transfer_model(matrix, phase_levels=64)
        second = build_mesh_transfer_model(matrix, phase_levels=64)
        self.assertEqual(first.transfer_matrix, second.transfer_matrix)
        self.assertEqual(first.left_mesh.phase_settings, second.left_mesh.phase_settings)
        self.assertEqual(first.right_mesh.coupler_settings, second.right_mesh.coupler_settings)

    def test_stage_2_report_has_complete_abstract_mesh_schema(self):
        report = run_mesh_constrained_demo(phase_levels=64)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["meshModel"], "abstract_hrm_mesh_simulation")
        self.assertFalse(report["realChipMesh"])
        self.assertEqual(report["meshParameterizationStatus"], "deterministic_abstract_phase_coupler_parameterization")
        self.assertTrue(report["abstractRotationParameterizationImplemented"])
        self.assertTrue(report["abstractPhaseParameterizationImplemented"])
        self.assertTrue(report["abstractCouplerParameterizationImplemented"])
        self.assertNotIn("phaseSynthesisImplemented", report)
        self.assertNotIn("couplerSynthesisImplemented", report)
        self.assertFalse(report["physicalPhaseSynthesisImplemented"])
        self.assertFalse(report["physicalCouplerSynthesisImplemented"])
        self.assertFalse(report["foundryLayoutSynthesisImplemented"])
        self.assertFalse(report["complexUnitaryMeshImplemented"])
        self.assertTrue(report["rectangularLayerSupportImplemented"])
        self.assertEqual(report["rectangularSupportReport"], "rectangular-matrix-support.json")
        self.assertFalse(report["clementsReckPhysicalLayoutImplemented"])
        self.assertFalse(report["squareMatrixOnly"])
        self.assertTrue(report["mainDemoMatrixIsSquare"])
        self.assertTrue(report["realValuedOrthogonalApproximation"])
        self.assertIn("no complex unitary mesh", report["currentDemoScope"])
        self.assertIn(
            "rectangular neural layer support is reported separately as a supplemental simulation artifact",
            report["currentDemoScope"],
        )
        self.assertGreater(report["phaseCount"], 0)
        self.assertGreater(report["couplerCount"], 0)
        self.assertIn("abstractMeshParameterization", report)
        self.assertIn("meshLimitations", report)
        self.assertIn("left", report["abstractMeshParameterization"])
        self.assertIn("right", report["abstractMeshParameterization"])
        self.assertLess(report["idealSvdRelativeError"], 1e-10)
        self.assertTrue(report["meshConstrainedRelativeError"] < float("inf"))
        self.assertIn("meshErrorDelta", report)
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertNotIn("no_deterministic_hrm_phase_coupler_synthesis", report["blockers"])
        self.assertIn("no_foundry_calibrated_mesh_model", report["blockers"])

    def test_hardware_evidence_gates_remain_blocked(self):
        self.assertEqual(foundry_calibration_gate(None)["stageStatus"], "blocked")
        self.assertEqual(measured_transfer_matrix_gate(None)["stageStatus"], "blocked")
        self.assertEqual(hardware_benchmark_gate(None)["stageStatus"], "blocked")


if __name__ == "__main__":
    unittest.main()
