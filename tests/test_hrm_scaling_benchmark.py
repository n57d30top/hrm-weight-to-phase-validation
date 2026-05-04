import json
import math
import unittest

from oqp.future_work.scaling_benchmark import (
    deterministic_scaling_cases,
    run_scaling_analysis_report,
    run_scaling_benchmark_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


EXPECTED_CASES = {
    "square_4x4",
    "square_8x8",
    "square_16x16",
    "rectangular_tall_8x4",
    "rectangular_tall_16x8",
    "rectangular_wide_4x8",
    "rectangular_wide_8x16",
    "low_rank_16x8",
    "rank_deficient_12x6",
    "dense_seeded_16x16",
    "phase_dominant_complex_8x8",
}


class HrmScalingBenchmarkTest(unittest.TestCase):
    def test_scaling_cases_are_complete(self):
        cases = deterministic_scaling_cases()
        self.assertEqual({case.case_id for case in cases}, EXPECTED_CASES)
        self.assertEqual(len(cases), 11)

    def test_scaling_benchmark_report_schema_and_claim_flags(self):
        report = run_scaling_benchmark_report(phase_levels=64)
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["id"], "scaling-benchmark")
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_scaling_benchmark_simulation")
        self.assertEqual(report["caseCount"], 11)
        self.assertEqual({row["caseId"] for row in report["cases"]}, EXPECTED_CASES)
        self.assertTrue(report["noHardwarePerformanceClaim"])
        self.assertFalse(report["localSoftwareRuntimeMeasured"])
        self.assertIsNone(report["hardwareLatency"])
        self.assertIsNone(report["hardwareThroughput"])
        self.assertIsNone(report["hardwareEnergy"])
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        for row in report["cases"]:
            self.assertIn("parameterCount", row)
            self.assertIn("estimatedOperationScale", row)
            self.assertFalse(row["estimatedOperationScale"]["isHardwarePerformanceClaim"])
            self.assertTrue(math.isfinite(row["idealReconstructionError"]))
            self.assertTrue(math.isfinite(row["meshConstrainedReconstructionError"]))
            self.assertTrue(math.isfinite(row["errorDelta"]))
            self.assertIsNone(row["localSoftwareRuntime"])
            self.assertIsNone(row["hardwareLatency"])
            self.assertIsNone(row["hardwareThroughput"])
            self.assertIsNone(row["hardwareEnergy"])
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])

    def test_scaling_benchmark_is_deterministic(self):
        first = run_scaling_benchmark_report(phase_levels=64)
        second = run_scaling_benchmark_report(phase_levels=64)
        self.assertEqual(first, second)

    def test_scaling_analysis_matches_benchmark_rows(self):
        benchmark = run_scaling_benchmark_report(phase_levels=64)
        analysis = run_scaling_analysis_report(phase_levels=64)
        rows = benchmark["cases"]
        best = min(rows, key=lambda row: row["meshConstrainedReconstructionError"])
        worst = max(rows, key=lambda row: row["meshConstrainedReconstructionError"])
        self.assertEqual(analysis["id"], "scaling-analysis")
        self.assertEqual(analysis["caseCount"], benchmark["caseCount"])
        self.assertEqual(analysis["bestCase"]["caseId"], best["caseId"])
        self.assertEqual(analysis["worstCase"]["caseId"], worst["caseId"])
        self.assertEqual(analysis["maxMeshConstrainedError"], worst["meshConstrainedReconstructionError"])
        self.assertTrue(analysis["noHardwarePerformanceClaim"])
        self.assertIsNone(analysis["hardwareLatency"])
        self.assertIsNone(analysis["hardwareEnergy"])
        self.assertIn("errorByShapeFamily", analysis)
        self.assertIn("errorByMatrixSize", analysis)
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])

    def test_complex_scaling_case_has_phase_and_amplitude_metrics(self):
        report = run_scaling_benchmark_report(phase_levels=64)
        row = next(case for case in report["cases"] if case["caseId"] == "phase_dominant_complex_8x8")
        self.assertEqual(row["realOrComplex"], "complex")
        self.assertIsNotNone(row["phaseAwareError"])
        self.assertIsNotNone(row["amplitudeError"])
        self.assertIsNone(row["abstractPhaseCount"])
        self.assertIsNone(row["abstractCouplerCount"])

    def test_hardware_evidence_gates_remain_blocked(self):
        self.assertEqual(foundry_calibration_gate(None)["stageStatus"], "blocked")
        self.assertEqual(measured_transfer_matrix_gate(None)["stageStatus"], "blocked")
        self.assertEqual(hardware_benchmark_gate(None)["stageStatus"], "blocked")


if __name__ == "__main__":
    unittest.main()
