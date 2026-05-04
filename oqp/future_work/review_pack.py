"""Reviewer-facing report pack for HRM neural future work.

This module summarizes existing simulation reports into deterministic JSON,
Markdown, and CSV review artifacts. It does not introduce new physical models
or hardware evidence.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, Iterable, List


EVIDENCE_LEVEL = "simulation_review_pack"
GENERATED_AT = "2026-05-04T00:00:00Z"
CLAIM_BOUNDARY_SENTENCE = "This is a simulation-only review pack. It is not hardware evidence."
CLAIM_BOUNDARY = (
    CLAIM_BOUNDARY_SENTENCE
    + " It does not claim hardware validation, foundry calibration, measured transfer matrices, "
    "production inference readiness, optical nonlinearities, quantum advantage, or a hardware benchmark."
)
CLAIM_BOUNDARY_NOTE = "simulation-only; not hardware evidence"


def run_review_pack_summary_report(
    stage_reports: Iterable[Dict[str, Any]],
    supplemental_reports: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    stages = list(stage_reports)
    supplemental = list(supplemental_reports)
    stage_status_table = [_stage_status_row(report) for report in sorted(stages, key=lambda row: row["stage"])]
    supplemental_index = [_supplemental_row(report) for report in sorted(supplemental, key=lambda row: row["id"])]
    blocked_gates = [
        {
            "stage": report["stage"],
            "id": report["id"],
            "stageStatus": report["stageStatus"],
            "blockerReason": report.get("blockerReason"),
            "blockers": report.get("blockers", []),
        }
        for report in sorted(stages, key=lambda row: row["stage"])
        if report["stage"] in {5, 6, 7}
    ]
    key_metrics = _collect_key_metrics(stages, supplemental)
    metric_rows = _metric_rows(stages, supplemental, key_metrics)
    return {
        "id": "review-pack-summary",
        "title": "Reviewer-facing simulation evidence pack summary",
        "stage": 0,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "generatedAt": GENERATED_AT,
        "reportCount": len(stages) + len(supplemental) + 1,
        "blockedHardwareGateCount": len(blocked_gates),
        "stageStatusTable": stage_status_table,
        "supplementalReportIndex": supplemental_index,
        "keyMetrics": key_metrics,
        "metricRows": metric_rows,
        "claimBoundary": CLAIM_BOUNDARY,
        "blockedGates": blocked_gates,
        "limitations": [
            "review pack summarizes generated simulation reports only",
            "no foundry-calibrated device model is included",
            "no measured HRM transfer matrix is included",
            "no end-to-end hardware benchmark is included",
            "no hardware timing, throughput, energy, or physical accuracy claim is made",
            "Stage 5, Stage 6, and Stage 7 remain blocked",
        ],
        "reviewerChecklist": [
            "Run make check to reproduce generated reports.",
            "Inspect reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256.",
            "Inspect stage reports for Stage 0 through Stage 7.",
            "Inspect blocked hardware gates for Stage 5, Stage 6, and Stage 7.",
            "Inspect report limitations before interpreting numeric metrics.",
            "Confirm Stage 5, Stage 6, and Stage 7 remain blocked.",
        ],
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": [
            "no_foundry_calibrated_device_model",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": [
            "release_candidate_hardening",
            "foundry_calibrated_device_model_gate",
            "measured_transfer_matrix_gate",
            "hardware_benchmark_gate",
        ],
    }


def render_review_pack_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# HRM Weight-to-Phase Review Pack",
        "",
        CLAIM_BOUNDARY_SENTENCE,
        "",
        "## Stage Status",
        "",
        "| Stage | Report | Status | Evidence Level |",
        "| --- | --- | --- | --- |",
    ]
    for row in summary["stageStatusTable"]:
        lines.append(
            f"| {row['stage']} | `{row['id']}` | {row['stageStatus']} | {row['evidenceLevel']} |"
        )

    lines.extend([
        "",
        "## Supplemental Reports",
        "",
    ])
    for report in summary["supplementalReportIndex"]:
        lines.append(
            f"- `{report['id']}`: {report['title']} ({report['evidenceLevel']})"
        )

    lines.extend([
        "",
        "## Key Metrics",
        "",
    ])
    for row in summary["metricRows"]:
        lines.append(
            f"- `{row['reportId']}` `{row['metricName']}`: {row['metricValue']}"
        )

    lines.extend([
        "",
        "## Blocked Hardware Gates",
        "",
    ])
    for gate in summary["blockedGates"]:
        lines.append(
            f"- Stage {gate['stage']} `{gate['id']}` remains {gate['stageStatus']} "
            f"({gate.get('blockerReason')})."
        )

    lines.extend([
        "",
        "## Limitations",
        "",
    ])
    for item in summary["limitations"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Reviewer Checklist",
        "",
    ])
    for item in summary["reviewerChecklist"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Claim Boundary",
        "",
        summary["claimBoundary"],
        "",
    ])
    return "\n".join(lines)


def render_review_pack_stage_table_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Review Pack Stage Table",
        "",
        CLAIM_BOUNDARY_SENTENCE,
        "",
        "| Stage | Report | Title | Status | Evidence Level |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in summary["stageStatusTable"]:
        lines.append(
            f"| {row['stage']} | `{row['id']}` | {row['title']} | {row['stageStatus']} | {row['evidenceLevel']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_review_pack_limitations_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Review Pack Limitations",
        "",
        CLAIM_BOUNDARY_SENTENCE,
        "",
    ]
    for item in summary["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def render_review_pack_metrics_csv(summary: Dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "reportId",
            "metricName",
            "metricValue",
            "evidenceLevel",
            "claimBoundaryNote",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    for row in summary["metricRows"]:
        writer.writerow(row)
    return output.getvalue()


def _stage_status_row(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "stage": report["stage"],
        "id": report["id"],
        "title": report["title"],
        "stageStatus": report["stageStatus"],
        "evidenceLevel": report["evidenceLevel"],
        "hardwareValidated": report["hardwareValidated"],
        "foundryCalibrated": report["foundryCalibrated"],
        "measuredTransferMatrixAvailable": report["measuredTransferMatrixAvailable"],
        "productionInferenceReady": report["productionInferenceReady"],
    }


def _supplemental_row(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "stage": report["stage"],
        "id": report["id"],
        "title": report["title"],
        "stageStatus": report["stageStatus"],
        "evidenceLevel": report["evidenceLevel"],
        "hardwareValidated": report["hardwareValidated"],
        "foundryCalibrated": report["foundryCalibrated"],
        "measuredTransferMatrixAvailable": report["measuredTransferMatrixAvailable"],
        "productionInferenceReady": report["productionInferenceReady"],
    }


def _collect_key_metrics(stages: List[Dict[str, Any]], supplemental: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_id = {report["id"]: report for report in stages + supplemental}
    stage_2 = by_id.get("stage-2-mesh-constrained", {})
    stage_3_analysis = by_id.get("stage-3-sweep-analysis", {})
    stage_4 = by_id.get("stage-4-simulated-calibration", {})
    stage_4_analysis = by_id.get("stage-4-calibration-analysis", {})
    matrix_family = by_id.get("matrix-family-analysis", {})
    layer_stack = by_id.get("layer-stack-inference-demo", {})
    scaling = by_id.get("scaling-analysis", {})
    return {
        "stage2MeshConstrainedRelativeError": stage_2.get("meshConstrainedRelativeError"),
        "stage2MeshErrorDelta": stage_2.get("meshErrorDelta"),
        "matrixFamilyBestCase": matrix_family.get("bestCase"),
        "matrixFamilyWorstCase": matrix_family.get("worstCase"),
        "matrixFamilyAverageMeshConstrainedError": matrix_family.get("averageMeshConstrainedError"),
        "matrixFamilyMaxErrorDelta": matrix_family.get("maxErrorDelta"),
        "layerStackPrimaryOutputRelativeError": layer_stack.get("outputRelativeError"),
        "layerStackMaxOutputRelativeError": layer_stack.get("outputRelativeErrorMax"),
        "scalingAverageMeshConstrainedError": scaling.get("averageMeshConstrainedError"),
        "scalingMaxMeshConstrainedError": scaling.get("maxMeshConstrainedError"),
        "scalingBestCase": scaling.get("bestCase"),
        "scalingWorstCase": scaling.get("worstCase"),
        "perturbationTopSensitivity": _first(stage_3_analysis.get("sensitivityRanking", [])),
        "calibrationPreRelativeError": stage_4.get("preCalibrationRelativeError"),
        "calibrationPostRelativeError": stage_4.get("postCalibrationRelativeError"),
        "calibrationBestPostRelativeError": stage_4_analysis.get("bestCasePostCalibrationRelativeError"),
        "calibrationWorstPostRelativeError": stage_4_analysis.get("worstCasePostCalibrationRelativeError"),
        "calibrationFailureCaseCount": stage_4_analysis.get("failureCaseCount"),
        "blockedHardwareGateCount": sum(
            1 for report in stages if report.get("stage") in {5, 6, 7} and report.get("stageStatus") == "blocked"
        ),
    }


def _metric_rows(
    stages: List[Dict[str, Any]],
    supplemental: List[Dict[str, Any]],
    key_metrics: Dict[str, Any],
) -> List[Dict[str, str]]:
    by_id = {report["id"]: report for report in stages + supplemental}
    metric_sources = {
        "stage2MeshConstrainedRelativeError": "stage-2-mesh-constrained",
        "stage2MeshErrorDelta": "stage-2-mesh-constrained",
        "matrixFamilyBestCase": "matrix-family-analysis",
        "matrixFamilyWorstCase": "matrix-family-analysis",
        "matrixFamilyAverageMeshConstrainedError": "matrix-family-analysis",
        "matrixFamilyMaxErrorDelta": "matrix-family-analysis",
        "layerStackPrimaryOutputRelativeError": "layer-stack-inference-demo",
        "layerStackMaxOutputRelativeError": "layer-stack-inference-demo",
        "scalingAverageMeshConstrainedError": "scaling-analysis",
        "scalingMaxMeshConstrainedError": "scaling-analysis",
        "scalingBestCase": "scaling-analysis",
        "scalingWorstCase": "scaling-analysis",
        "perturbationTopSensitivity": "stage-3-sweep-analysis",
        "calibrationPreRelativeError": "stage-4-simulated-calibration",
        "calibrationPostRelativeError": "stage-4-simulated-calibration",
        "calibrationBestPostRelativeError": "stage-4-calibration-analysis",
        "calibrationWorstPostRelativeError": "stage-4-calibration-analysis",
        "calibrationFailureCaseCount": "stage-4-calibration-analysis",
        "blockedHardwareGateCount": "review-pack-summary",
    }
    rows = []
    for metric_name, value in key_metrics.items():
        if value is None:
            continue
        report_id = metric_sources[metric_name]
        evidence_level = by_id.get(report_id, {}).get("evidenceLevel", EVIDENCE_LEVEL)
        rows.append({
            "reportId": report_id,
            "metricName": metric_name,
            "metricValue": _metric_value(value),
            "evidenceLevel": evidence_level,
            "claimBoundaryNote": CLAIM_BOUNDARY_NOTE,
        })
    return rows


def _first(rows: List[Any]) -> Any:
    if not rows:
        return None
    return rows[0]


def _metric_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)
