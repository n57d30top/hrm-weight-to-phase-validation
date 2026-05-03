import json
import math
import unittest

from oqp.future_work.complex_unitary_mapping import (
    amplitude_relative_error,
    build_complex_unitary_model,
    complex_matmul,
    complex_qr_factorization,
    deterministic_complex_matrices,
    phase_aware_error,
    relative_complex_frobenius_error,
    run_complex_unitary_mesh_support_report,
    unitarity_deviation,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


class HrmComplexUnitaryMappingTest(unittest.TestCase):
    def test_complex_qr_reconstructs_deterministic_matrix(self):
        matrix = deterministic_complex_matrices()["complex_4x4"]
        unitary, residual = complex_qr_factorization(matrix)
        reconstruction = complex_matmul(unitary, residual)
        self.assertLess(relative_complex_frobenius_error(matrix, reconstruction), 1e-10)
        self.assertLess(unitarity_deviation(unitary), 1e-10)

    def test_unitary_like_matrix_reconstruction(self):
        matrix = deterministic_complex_matrices()["unitary_like_2x2"]
        model = build_complex_unitary_model(matrix, case_id="unitary_like_2x2")
        self.assertLess(model.ideal_error, 1e-10)
        self.assertLess(model.mesh_error, 0.05)
        self.assertLess(model.exact_unitarity_deviation, 1e-10)
        self.assertLess(model.approximated_unitarity_deviation, 1e-10)

    def test_phase_and_amplitude_error_metrics(self):
        target = [[1.0 + 0.0j]]
        phase_shifted = [[0.0 + 1.0j]]
        amplitude_shifted = [[2.0 + 0.0j]]
        self.assertAlmostEqual(phase_aware_error(target, phase_shifted), math.pi / 2.0)
        self.assertAlmostEqual(amplitude_relative_error(target, phase_shifted), 0.0)
        self.assertAlmostEqual(phase_aware_error(target, amplitude_shifted), 0.0)
        self.assertAlmostEqual(amplitude_relative_error(target, amplitude_shifted), 1.0)

    def test_complex_unitary_model_is_deterministic(self):
        matrix = deterministic_complex_matrices()["phase_dominant_4x4"]
        first = build_complex_unitary_model(matrix, case_id="phase_dominant_4x4", phase_levels=64)
        second = build_complex_unitary_model(matrix, case_id="phase_dominant_4x4", phase_levels=64)
        self.assertEqual(first.approximated_reconstruction, second.approximated_reconstruction)
        self.assertEqual(first.approximated_unitary_factor, second.approximated_unitary_factor)

    def test_complex_unitary_report_schema_and_claim_flags(self):
        report = run_complex_unitary_mesh_support_report(phase_levels=64)
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["id"], "complex-unitary-mesh-support")
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_complex_unitary_mesh_simulation")
        self.assertTrue(report["complexValuedSupportImplemented"])
        self.assertTrue(report["unitaryFactorSupportImplemented"])
        self.assertFalse(report["complexSvdImplemented"])
        self.assertFalse(report["physicalPhaseSynthesisImplemented"])
        self.assertFalse(report["physicalCouplerSynthesisImplemented"])
        self.assertFalse(report["foundryLayoutSynthesisImplemented"])
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertEqual(report["caseCount"], 3)
        for row in report["cases"]:
            self.assertIn("phaseAwareError", row)
            self.assertIn("amplitudeError", row)
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
