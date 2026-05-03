import unittest

from oqp.future_work.neural_mapping import (
    passive_normalize_singular_values,
    reconstruct_from_svd,
    relative_frobenius_error,
    run_svd_mapping_demo,
    svd_decompose,
)


class HrmNeuralMappingTest(unittest.TestCase):
    def test_svd_reconstructs_deterministic_matrix(self):
        matrix = [
            [0.42, -0.25, 0.31],
            [0.10, 0.56, -0.44],
            [-0.35, 0.18, 0.62],
        ]
        result = svd_decompose(matrix)
        reconstruction = reconstruct_from_svd(result)
        self.assertLess(relative_frobenius_error(matrix, reconstruction), 1e-10)

    def test_zero_matrix_handling(self):
        matrix = [[0.0, 0.0], [0.0, 0.0]]
        result = svd_decompose(matrix)
        reconstruction = reconstruct_from_svd(result)
        self.assertEqual(passive_normalize_singular_values(result.singular_values), [0.0, 0.0])
        self.assertEqual(relative_frobenius_error(matrix, reconstruction), 0.0)

    def test_passive_normalization_range(self):
        normalized = passive_normalize_singular_values([4.0, 2.0, 0.0])
        self.assertEqual(max(normalized), 1.0)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in normalized))

    def test_stage_1_report_schema_and_flags(self):
        report = run_svd_mapping_demo()
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "numerical_simulation")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertFalse(report["activeGainImplemented"])
        self.assertFalse(report["phaseSynthesisImplemented"])
        self.assertLess(report["relativeFrobeniusReconstructionError"], 1e-10)


if __name__ == "__main__":
    unittest.main()
