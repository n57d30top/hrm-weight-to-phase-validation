"""Static dashboard renderer for generated HRM planning reports."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def render_static_dashboard(stage_reports: Iterable[Dict[str, Any]], supplemental_reports: Iterable[Dict[str, Any]]) -> str:
    stages = list(stage_reports)
    supplemental = list(supplemental_reports)
    decision = _by_id(supplemental, "model-to-hrm-decision-report")
    portfolio = _by_id(supplemental, "model-portfolio-ranking")
    design = _by_id(supplemental, "hardware-design-space-analysis")
    rows = "\n".join(
        f"<tr><td>{report['stage']}</td><td>{report['id']}</td><td>{report['stageStatus']}</td><td>{report['evidenceLevel']}</td></tr>"
        for report in sorted(stages, key=lambda row: row["stage"])
    )
    cards = [
        ("Decision", decision.get("decision", "unknown")),
        ("Suitability Score", str(decision.get("suitabilityScore", "n/a"))),
        ("Best Portfolio Candidate", portfolio.get("bestSimulationCandidate", {}).get("modelId", "n/a")),
        ("Design Pareto Candidates", str(design.get("paretoCandidateCount", "n/a"))),
        ("Hardware Gates Blocked", "3"),
    ]
    card_html = "\n".join(f"<section><h2>{title}</h2><p>{value}</p></section>" for title, value in cards)
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>HRM Planning Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #172026; background: #f7f8f4; }}
    header {{ max-width: 920px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin: 2rem 0; }}
    section {{ background: #ffffff; border: 1px solid #d5d9ce; border-radius: 8px; padding: 1rem; }}
    h1, h2 {{ margin: 0 0 0.5rem; }}
    table {{ border-collapse: collapse; width: 100%; background: #ffffff; }}
    th, td {{ border: 1px solid #d5d9ce; padding: 0.5rem; text-align: left; }}
    th {{ background: #e9ece2; }}
    code {{ background: #ecefe8; padding: 0.1rem 0.25rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>HRM Simulation Planning Dashboard</h1>
    <p>This static dashboard summarizes simulation-only reports. It is not hardware evidence.</p>
  </header>
  <main>
    <div class=\"grid\">
      {card_html}
    </div>
    <h2>Stage Status</h2>
    <table>
      <thead><tr><th>Stage</th><th>Report</th><th>Status</th><th>Evidence Level</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p>Claim boundary: hardware validation, foundry calibration, measured transfer matrices, and production inference readiness remain false.</p>
  </main>
</body>
</html>"""


def _by_id(reports: List[Dict[str, Any]], report_id: str) -> Dict[str, Any]:
    for report in reports:
        if report["id"] == report_id:
            return report
    return {}
