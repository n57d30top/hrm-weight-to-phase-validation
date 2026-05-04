import json
import math
import unittest
from pathlib import Path

from oqp.future_work.design_space_explorer import (
    render_hardware_design_space_pareto,
    run_hardware_design_space_analysis_report,
    run_hardware_design_space_sweep_report,
)
from oqp.future_work.validation_gates import foundry_calibration_gate, hardware_benchmark_gate, measured_transfer_matrix_gate


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmDesignSpaceExplorerTest(unittest.TestCase):
    def test_design_space_sweep_is_deterministic(self):
        first = run_hardware_design_space_sweep_report()
        second = run_hardware_design_space_sweep_report()
        self.assertEqual(first, second)
        self.assertEqual(first["rowCount"], 108)
        self.assertTrue(first["parametricEstimateOnly"])
        self.assertFalse(first["measuredHardwarePerformance"])
        for row in first["rows"]:
            self.assertTrue(math.isfinite(row["estimatedOutputRelativeError"]))
            self.assertGreaterEqual(row["estimatedOutputRelativeError"], 0.0)
            self.assertTrue(row["parametricEstimateOnly"])
            self.assertFalse(row["hardwareValidated"])

    def test_analysis_has_pareto_candidates_and_bottlenecks(self):
        analysis = run_hardware_design_space_analysis_report()
        self.assertGreater(analysis["paretoCandidateCount"], 0)
        self.assertGreater(len(analysis["bottleneckRanking"]), 0)
        self.assertIn("candidateId", analysis["bestErrorCandidate"])
        markdown = render_hardware_design_space_pareto(analysis)
        self.assertIn("simulation-only design-space report", markdown)

    def test_generated_reports_are_hash_covered(self):
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        for filename in ["hardware-design-space-sweep.json", "hardware-design-space-analysis.json"]:
            report = json.loads((REPORT_DIR / filename).read_text(encoding="utf-8"))
            json.dumps(report, sort_keys=True)
            self.assertFalse(report["hardwareValidated"])
            self.assertIn(f"reports/future-work/hrm-neural-mapping/{filename}", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-design-space-pareto.md", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [foundry_calibration_gate(None), measured_transfer_matrix_gate(None), hardware_benchmark_gate(None)]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
