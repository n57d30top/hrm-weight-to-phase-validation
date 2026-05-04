import json
import unittest
from pathlib import Path

from oqp.future_work.model_portfolio import (
    render_model_portfolio_decision_summary,
    run_model_portfolio_benchmark_report,
    run_model_portfolio_ranking_report,
)
from oqp.future_work.validation_gates import foundry_calibration_gate, hardware_benchmark_gate, measured_transfer_matrix_gate


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmModelPortfolioTest(unittest.TestCase):
    def test_portfolio_benchmark_is_deterministic(self):
        first = run_model_portfolio_benchmark_report()
        second = run_model_portfolio_benchmark_report()
        self.assertEqual(first, second)
        self.assertEqual(first["modelCount"], 5)
        ids = {row["modelId"] for row in first["models"]}
        self.assertEqual(ids, {
            "tiny_mlp",
            "projection_chain",
            "low_rank_adapter_demo",
            "sparse_linear_demo",
            "transformer_block_manifest_only",
        })
        for row in first["models"]:
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])

    def test_ranking_best_and_worst_are_stable(self):
        ranking = run_model_portfolio_ranking_report()
        self.assertEqual(ranking["bestSimulationCandidate"]["modelId"], "low_rank_adapter_demo")
        self.assertEqual(ranking["worstSimulationCandidate"]["modelId"], "transformer_block_manifest_only")
        self.assertEqual(ranking["ranking"][0]["rank"], 1)
        markdown = render_model_portfolio_decision_summary(ranking)
        self.assertIn("simulation-only portfolio summary", markdown)

    def test_generated_reports_are_hash_covered(self):
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        for filename in ["model-portfolio-benchmark.json", "model-portfolio-ranking.json"]:
            report = json.loads((REPORT_DIR / filename).read_text(encoding="utf-8"))
            json.dumps(report, sort_keys=True)
            self.assertFalse(report["hardwareValidated"])
            self.assertIn(f"reports/future-work/hrm-neural-mapping/{filename}", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-portfolio-decision-summary.md", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [foundry_calibration_gate(None), measured_transfer_matrix_gate(None), hardware_benchmark_gate(None)]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
