import json
import unittest

from oqp.future_work.matrix_family_benchmark import (
    deterministic_matrix_family_cases,
    run_matrix_family_analysis_report,
    run_matrix_family_benchmark_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


EXPECTED_CASES = {
    "identity_4x4",
    "diagonal_dynamic_range_4x4",
    "low_rank_6x4",
    "rank_deficient_5x3",
    "ill_conditioned_4x4",
    "sparse_like_6x6",
    "dense_seeded_4x4",
    "rectangular_tall_8x4",
    "rectangular_wide_4x8",
    "complex_phase_dominant_4x4",
    "unitary_like_4x4",
}


class HrmMatrixFamilyBenchmarkTest(unittest.TestCase):
    def test_case_definitions_are_complete(self):
        cases = deterministic_matrix_family_cases()
        self.assertEqual({case.case_id for case in cases}, EXPECTED_CASES)
        self.assertEqual(len(cases), 11)

    def test_benchmark_report_schema_and_claim_flags(self):
        report = run_matrix_family_benchmark_report(phase_levels=64)
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["id"], "matrix-family-benchmark")
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_matrix_family_benchmark_simulation")
        self.assertEqual(report["caseCount"], 11)
        self.assertEqual({row["caseId"] for row in report["cases"]}, EXPECTED_CASES)
        self.assertEqual(report["realCaseCount"], 9)
        self.assertEqual(report["complexCaseCount"], 2)
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        for row in report["cases"]:
            self.assertIn("matrixFamily", row)
            self.assertIn("shape", row)
            self.assertIn("rank", row)
            self.assertIn("conditionNumber", row)
            self.assertIn("realOrComplex", row)
            self.assertIn("idealReconstructionError", row)
            self.assertIn("meshConstrainedReconstructionError", row)
            self.assertIn("errorDelta", row)
            self.assertIn("limitations", row)
            self.assertTrue(row["limitations"])
            self.assertGreaterEqual(row["meshConstrainedReconstructionError"], row["idealReconstructionError"])
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])

    def test_benchmark_report_is_deterministic(self):
        first = run_matrix_family_benchmark_report(phase_levels=64)
        second = run_matrix_family_benchmark_report(phase_levels=64)
        self.assertEqual(first, second)

    def test_analysis_matches_benchmark_rows(self):
        benchmark = run_matrix_family_benchmark_report(phase_levels=64)
        analysis = run_matrix_family_analysis_report(phase_levels=64)
        rows = benchmark["cases"]
        best = min(rows, key=lambda row: row["meshConstrainedReconstructionError"])
        worst = max(rows, key=lambda row: row["meshConstrainedReconstructionError"])
        max_delta = max(rows, key=lambda row: row["errorDelta"])
        self.assertEqual(analysis["id"], "matrix-family-analysis")
        self.assertEqual(analysis["caseCount"], benchmark["caseCount"])
        self.assertEqual(analysis["bestCase"]["caseId"], best["caseId"])
        self.assertEqual(analysis["worstCase"]["caseId"], worst["caseId"])
        self.assertEqual(analysis["maxErrorDeltaCase"]["caseId"], max_delta["caseId"])
        self.assertEqual(analysis["maxErrorDelta"], max_delta["errorDelta"])
        self.assertEqual(analysis["familyRankingByError"][0]["caseId"], worst["caseId"])
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])

    def test_complex_cases_have_phase_and_amplitude_metrics(self):
        report = run_matrix_family_benchmark_report(phase_levels=64)
        complex_rows = [row for row in report["cases"] if row["realOrComplex"] == "complex"]
        self.assertEqual(len(complex_rows), 2)
        for row in complex_rows:
            self.assertIsNotNone(row["phaseAwareError"])
            self.assertIsNotNone(row["amplitudeError"])
            self.assertIsNone(row["conditionNumber"])

    def test_hardware_evidence_gates_remain_blocked(self):
        self.assertEqual(foundry_calibration_gate(None)["stageStatus"], "blocked")
        self.assertEqual(measured_transfer_matrix_gate(None)["stageStatus"], "blocked")
        self.assertEqual(hardware_benchmark_gate(None)["stageStatus"], "blocked")


if __name__ == "__main__":
    unittest.main()
