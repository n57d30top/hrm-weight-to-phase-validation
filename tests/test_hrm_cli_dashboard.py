import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmCliDashboardTest(unittest.TestCase):
    def test_cli_list_reports_outputs_known_reports(self):
        result = subprocess.run(
            ["python3", "-m", "oqp.cli", "list-reports"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        self.assertIn("reports/future-work/hrm-neural-mapping/model-to-hrm-decision-report.json", result.stdout)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-design-space-analysis.json", result.stdout)

    def test_cli_summary_and_decision_emit_json(self):
        summary = subprocess.run(
            ["python3", "-m", "oqp.cli", "summary"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        decision = subprocess.run(
            ["python3", "-m", "oqp.cli", "decision"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(json.loads(summary.stdout)["id"], "validation-ladder-summary")
        self.assertEqual(json.loads(decision.stdout)["decision"], "blocked_by_missing_hardware_evidence")

    def test_dashboard_is_static_and_hash_covered(self):
        dashboard = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertIn("HRM Simulation Planning Dashboard", dashboard)
        self.assertIn("not hardware evidence", dashboard)
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("dashboard/index.html", artifacts)

    def test_pyproject_exposes_cli_entrypoint_and_v02_alpha_version(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.2.0-alpha.1"', pyproject)
        self.assertIn('hrmwtp = "oqp.cli:main"', pyproject)


if __name__ == "__main__":
    unittest.main()
