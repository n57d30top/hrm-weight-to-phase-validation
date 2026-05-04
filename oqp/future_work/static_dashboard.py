"""Static dashboard renderer for generated HRM planning reports."""

from __future__ import annotations

from html import escape
from typing import Any, Dict, Iterable, List


def render_static_dashboard(stage_reports: Iterable[Dict[str, Any]], supplemental_reports: Iterable[Dict[str, Any]]) -> str:
    stages = list(stage_reports)
    supplemental = list(supplemental_reports)
    decision = _by_id(supplemental, "model-to-hrm-decision-report")
    portfolio = _by_id(supplemental, "model-portfolio-ranking")
    design = _by_id(supplemental, "hardware-design-space-analysis")
    best_portfolio = portfolio.get("bestSimulationCandidate", {})
    worst_portfolio = portfolio.get("worstSimulationCandidate", {})
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(report['stage']))}</td>"
        f"<td><a href=\"../reports/future-work/hrm-neural-mapping/{_filename_for_stage(report)}\">{escape(report['id'])}</a></td>"
        f"<td>{escape(report['stageStatus'])}</td>"
        f"<td>{escape(report['evidenceLevel'])}</td>"
        "</tr>"
        for report in sorted(stages, key=lambda row: row["stage"])
    )
    gate_rows = "\n".join(
        "<tr>"
        f"<td>Stage {escape(str(report['stage']))}</td>"
        f"<td>{escape(report['id'])}</td>"
        f"<td>{escape(report['stageStatus'])}</td>"
        f"<td>{escape(', '.join(report.get('blockers', [])) or 'none')}</td>"
        "</tr>"
        for report in sorted((report for report in stages if report["stage"] >= 5), key=lambda row: row["stage"])
    )
    cards = [
        ("Decision", decision.get("decision", "unknown")),
        ("Suitability Score", str(decision.get("suitabilityScore", "n/a"))),
        ("Best Portfolio Candidate", best_portfolio.get("modelId", "n/a")),
        ("Design Pareto Candidates", str(design.get("paretoCandidateCount", "n/a"))),
        ("Hardware Gates Blocked", "3"),
    ]
    card_html = "\n".join(
        f"<section class=\"metric\"><h2>{escape(title)}</h2><p>{escape(value)}</p></section>"
        for title, value in cards
    )
    report_links = [
        ("Validation summary", "validation-ladder-summary.json"),
        ("Decision report", "model-to-hrm-decision-report.json"),
        ("Model portfolio ranking", "model-portfolio-ranking.json"),
        ("Design-space analysis", "hardware-design-space-analysis.json"),
        ("Transfer-matrix sandbox", "transfer-matrix-ingestion-sandbox.json"),
        ("Review pack", "review-pack.md"),
        ("Artifact hashes", "ARTIFACTS.sha256"),
    ]
    link_html = "\n".join(
        f"<li><a href=\"../reports/future-work/hrm-neural-mapping/{escape(filename)}\">{escape(label)}</a></li>"
        for label, filename in report_links
    )
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>HRM Planning Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #172026; background: #f7f8f4; line-height: 1.45; }}
    header {{ max-width: 920px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin: 2rem 0; }}
    section {{ margin: 2rem 0; }}
    .metric, .claim-boundary, .not-box {{ background: #ffffff; border: 1px solid #d5d9ce; border-radius: 8px; padding: 1rem; }}
    .claim-boundary {{ border-color: #a64f35; background: #fff8f4; }}
    .not-box {{ background: #f0f5f8; }}
    h1, h2 {{ margin: 0 0 0.5rem; }}
    table {{ border-collapse: collapse; width: 100%; background: #ffffff; }}
    th, td {{ border: 1px solid #d5d9ce; padding: 0.5rem; text-align: left; }}
    th {{ background: #e9ece2; }}
    a {{ color: #1a5a78; }}
    code {{ background: #ecefe8; padding: 0.1rem 0.25rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>HRM Simulation Planning Dashboard</h1>
    <p>This static dashboard summarizes simulation-only reports. It is not hardware evidence.</p>
  </header>
  <main>
    <section>
      <h2>What This Is</h2>
      <p>A reviewer-facing index for deterministic simulation reports, model-planning outputs, and blocked evidence gates.</p>
    </section>
    <section class=\"not-box\">
      <h2>What This Is Not</h2>
      <p>It is not a hardware result, not foundry calibration, not a measured transfer-matrix package, and not production inference readiness.</p>
    </section>
    <div class=\"grid\">
      {card_html}
    </div>
    <section>
      <h2>Key Reports</h2>
      <ul>{link_html}</ul>
    </section>
    <section>
      <h2>Stage Status</h2>
      <table>
        <thead><tr><th>Stage</th><th>Report</th><th>Status</th><th>Evidence Level</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Model Portfolio Summary</h2>
      <p>Best simulation candidate: <code>{escape(str(best_portfolio.get("modelId", "n/a")))}</code>.</p>
      <p>Worst simulation candidate: <code>{escape(str(worst_portfolio.get("modelId", "n/a")))}</code>.</p>
      <p>These are simulation-only planning labels, not hardware evidence.</p>
    </section>
    <section>
      <h2>Hardware Gate Blockers</h2>
      <table>
        <thead><tr><th>Gate</th><th>Report</th><th>Status</th><th>Blockers</th></tr></thead>
        <tbody>{gate_rows}</tbody>
      </table>
    </section>
    <section class=\"claim-boundary\">
      <h2>Claim Boundary</h2>
      <p>hardwareValidated=false, foundryCalibrated=false, measuredTransferMatrixAvailable=false, productionInferenceReady=false.</p>
      <p>This dashboard does not claim hardware validation, foundry calibration, measured transfer matrices, physical accuracy, production inference readiness, real hardware latency, real hardware energy efficiency, quantum advantage, hardware-native intelligence, or power-free computation.</p>
    </section>
  </main>
</body>
</html>"""


def _by_id(reports: List[Dict[str, Any]], report_id: str) -> Dict[str, Any]:
    for report in reports:
        if report["id"] == report_id:
            return report
    return {}


def _filename_for_stage(report: Dict[str, Any]) -> str:
    return {
        0: "stage-0-specification.json",
        1: "stage-1-svd-demo.json",
        2: "stage-2-mesh-constrained.json",
        3: "stage-3-perturbation-model.json",
        4: "stage-4-simulated-calibration.json",
        5: "stage-5-foundry-calibration-gate.json",
        6: "stage-6-measured-transfer-matrix-gate.json",
        7: "stage-7-hardware-benchmark-gate.json",
    }[int(report["stage"])]
