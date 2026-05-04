import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmCliDashboardTest(unittest.TestCase):
    def test_cli_help_outputs_disclaimer(self):
        result = subprocess.run(
            ["python3", "scripts/hrmwtp.py", "--help"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        self.assertIn("This is simulation-only output. It is not hardware evidence.", result.stdout)
        self.assertIn("summary", result.stdout)
        self.assertIn("decision", result.stdout)
        self.assertIn("portfolio", result.stdout)
        self.assertIn("model-card", result.stdout)
        self.assertIn("doctor", result.stdout)

    def test_cli_list_reports_outputs_known_reports(self):
        result = subprocess.run(
            ["python3", "scripts/hrmwtp.py", "list-reports"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertIn("This is simulation-only output. It is not hardware evidence.", result.stderr)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-to-hrm-decision-report.json", result.stdout)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-design-space-analysis.json", result.stdout)

    def test_cli_summary_and_decision_emit_json(self):
        summary = subprocess.run(
            ["python3", "scripts/hrmwtp.py", "summary"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        decision = subprocess.run(
            ["python3", "scripts/hrmwtp.py", "decision"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertIn("This is simulation-only output. It is not hardware evidence.", summary.stderr)
        self.assertIn("This is simulation-only output. It is not hardware evidence.", decision.stderr)
        self.assertEqual(json.loads(summary.stdout)["id"], "validation-ladder-summary")
        self.assertEqual(json.loads(decision.stdout)["decision"], "blocked_by_missing_hardware_evidence")

    def test_cli_check_dry_run_delegates_safely(self):
        result = subprocess.run(
            ["python3", "scripts/hrmwtp.py", "check", "--dry-run"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertIn("This is simulation-only output. It is not hardware evidence.", result.stderr)
        self.assertIn("Would run: make check", result.stdout)

    def test_cli_portfolio_model_card_and_doctor_work(self):
        portfolio = subprocess.run(
            ["python3", "scripts/hrmwtp.py", "portfolio"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        card = subprocess.run(
            ["python3", "scripts/hrmwtp.py", "model-card", "low_rank_adapter_demo"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        doctor = subprocess.run(
            ["python3", "scripts/hrmwtp.py", "doctor"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(json.loads(portfolio.stdout)["id"], "model-portfolio-ranking")
        self.assertIn("Model Card: low_rank_adapter_demo", card.stdout)
        self.assertTrue(json.loads(doctor.stdout)["ok"])
        self.assertIn("This is simulation-only output. It is not hardware evidence.", portfolio.stderr)
        self.assertIn("This is simulation-only output. It is not hardware evidence.", card.stderr)
        self.assertIn("This is simulation-only output. It is not hardware evidence.", doctor.stderr)

    def test_dashboard_is_static_and_hash_covered(self):
        dashboard = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertIn("HRM Simulation Planning Dashboard", dashboard)
        self.assertIn("not hardware evidence", dashboard)
        self.assertIn("What This Is", dashboard)
        self.assertIn("What This Is Not", dashboard)
        self.assertIn("Claim Boundary", dashboard)
        self.assertIn("Hardware Gate Blockers", dashboard)
        self.assertIn("Partner Readiness Status", dashboard)
        self.assertIn("External review checklist", dashboard)
        self.assertIn("This dashboard summarizes simulation-only artifacts. It is not hardware evidence.", dashboard)
        self.assertIn("model-portfolio-ranking.json", dashboard)
        self.assertIn("model-cards/low_rank_adapter_demo.md", dashboard)
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("dashboard/index.html", artifacts)

    def test_reviewer_guide_and_quickstart_exist_and_are_hash_covered(self):
        reviewer = ROOT / "docs" / "REVIEWER_GUIDE.md"
        quickstart = ROOT / "docs" / "QUICKSTART.md"
        self.assertIn("simulation-only", reviewer.read_text(encoding="utf-8"))
        self.assertIn("make check", quickstart.read_text(encoding="utf-8"))
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("docs/REVIEWER_GUIDE.md", artifacts)
        self.assertIn("docs/QUICKSTART.md", artifacts)
        self.assertIn("docs/PARTNER_READINESS.md", artifacts)
        self.assertIn("docs/REPRODUCIBILITY.md", artifacts)

    def test_pyproject_exposes_cli_entrypoint_and_v02_alpha_version(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.2.0-alpha.3"', pyproject)
        self.assertIn('hrmwtp = "oqp.cli:main"', pyproject)


if __name__ == "__main__":
    unittest.main()
