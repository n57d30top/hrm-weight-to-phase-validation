import json
import math
import unittest
from pathlib import Path

from oqp.future_work.hardware_scenario_estimator import (
    run_hardware_scenario_analysis_report,
    run_hardware_scenario_estimates_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmHardwareScenarioEstimatorTest(unittest.TestCase):
    def test_estimates_are_deterministic_and_parametric_only(self):
        first = run_hardware_scenario_estimates_report()
        second = run_hardware_scenario_estimates_report()
        self.assertEqual(first, second)
        self.assertEqual(first["scenarioCount"], 5)
        self.assertTrue(first["parametricEstimateOnly"])
        self.assertFalse(first["measuredHardwarePerformance"])
        for row in first["scenarios"]:
            self.assertTrue(row["parametricEstimateOnly"])
            self.assertFalse(row["measuredHardwarePerformance"])
            self.assertGreaterEqual(row["estimatedEndToEndLatencyNs"], 0.0)
            self.assertGreaterEqual(row["estimatedEnergyPerInferencePj"], 0.0)
            self.assertTrue(math.isfinite(row["estimatedEndToEndLatencyNs"]))
            self.assertTrue(math.isfinite(row["estimatedEnergyPerInferencePj"]))
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])

    def test_analysis_matches_estimate_extremes(self):
        estimates = run_hardware_scenario_estimates_report()
        analysis = run_hardware_scenario_analysis_report()
        rows = estimates["scenarios"]
        best_latency = min(rows, key=lambda row: row["estimatedEndToEndLatencyNs"])
        worst_latency = max(rows, key=lambda row: row["estimatedEndToEndLatencyNs"])
        best_energy = min(rows, key=lambda row: row["estimatedEnergyPerInferencePj"])
        worst_energy = max(rows, key=lambda row: row["estimatedEnergyPerInferencePj"])
        self.assertEqual(analysis["bestLatencyScenario"]["scenarioId"], best_latency["scenarioId"])
        self.assertEqual(analysis["worstLatencyScenario"]["scenarioId"], worst_latency["scenarioId"])
        self.assertEqual(analysis["bestEnergyScenario"]["scenarioId"], best_energy["scenarioId"])
        self.assertEqual(analysis["worstEnergyScenario"]["scenarioId"], worst_energy["scenarioId"])
        self.assertIn("parametric estimates", analysis["warning"])
        self.assertFalse(analysis["hardwareValidated"])

    def test_generated_reports_are_serializable_and_hash_covered(self):
        for filename in ["hardware-scenario-estimates.json", "hardware-scenario-analysis.json"]:
            path = REPORT_DIR / filename
            report = json.loads(path.read_text(encoding="utf-8"))
            json.dumps(report, sort_keys=True)
            self.assertFalse(report["hardwareValidated"])
            self.assertFalse(report["foundryCalibrated"])
            self.assertFalse(report["measuredTransferMatrixAvailable"])
            self.assertFalse(report["productionInferenceReady"])
            artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
            self.assertIn(f"reports/future-work/hrm-neural-mapping/{filename}", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [
            foundry_calibration_gate(None),
            measured_transfer_matrix_gate(None),
            hardware_benchmark_gate(None),
        ]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
