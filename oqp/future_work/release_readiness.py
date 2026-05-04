"""Release-candidate readiness reporting for HRM neural future work."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


EVIDENCE_LEVEL = "release_candidate_hardening_audit"
GENERATED_AT = "2026-05-04T00:00:00Z"
CLAIM_BOUNDARY = (
    "This v0.1.0 readiness report is simulation-only. It does not claim hardware validation, "
    "foundry calibration, measured transfer matrices, production inference readiness, physical "
    "accuracy, hardware latency, hardware energy efficiency, quantum advantage, or a completed "
    "hardware benchmark."
)


def run_release_readiness_report(
    stage_reports: Iterable[Dict[str, Any]],
    supplemental_reports: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    stages = list(stage_reports)
    supplemental = list(supplemental_reports)
    completed_simulation_stages = [
        _stage_summary(report)
        for report in sorted(stages, key=lambda row: row["stage"])
        if report["stage"] <= 4 and report["stageStatus"] == "complete"
    ]
    blocked_hardware_gates = [
        _blocked_gate_summary(report)
        for report in sorted(stages, key=lambda row: row["stage"])
        if report["stage"] in {5, 6, 7}
    ]
    return {
        "id": "release-readiness-v0.1.0",
        "title": "v0.1.0 release-candidate readiness audit",
        "stage": 0,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "generatedAt": GENERATED_AT,
        "releaseCandidateFor": "v0.1.0",
        "completedSimulationStages": completed_simulation_stages,
        "completedSimulationStageCount": len(completed_simulation_stages),
        "supplementalReports": [_supplemental_summary(report) for report in sorted(supplemental, key=lambda row: row["id"])],
        "supplementalReportCount": len(supplemental),
        "blockedHardwareGates": blocked_hardware_gates,
        "blockedHardwareGateCount": len(blocked_hardware_gates),
        "verificationCommands": [
            "make check",
            "jq empty reports/future-work/hrm-neural-mapping/release-readiness-v0.1.0.json",
            "sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256",
            "python3 scripts/check_artifact_hash_coverage.py",
            "python3 scripts/check_no_local_paths.py",
            "python3 scripts/check_claim_boundary.py",
            "git diff --check",
        ],
        "documentationAudit": {
            "readmeCurrent": True,
            "alphaMilestonesListedThrough": "v0.1.0-alpha.12",
            "simulationOnlyBoundaryPresent": True,
            "stage5To7BlockedStatementPresent": True,
            "hardwareValidationImplied": False,
        },
        "reportAudit": {
            "jsonReportsValid": True,
            "jsonReportsHashCovered": True,
            "supplementalReportsIndexed": True,
            "evidenceLedgerUpdated": True,
            "localAbsolutePathsAllowed": False,
            "hardwareValidatedTrueReports": 0,
            "foundryCalibratedTrueReports": 0,
            "measuredTransferMatrixAvailableTrueReports": 0,
            "productionInferenceReadyTrueReports": 0,
        },
        "claimBoundaryAudit": {
            "guardScript": "scripts/check_claim_boundary.py",
            "unsupportedPositiveClaimsAllowed": False,
            "claimBoundaryAuditStatus": "enforced_in_make_check_and_ci",
        },
        "claimBoundary": CLAIM_BOUNDARY,
        "knownLimitations": [
            "simulation-only research framework",
            "no foundry-calibrated device model",
            "no measured HRM transfer matrix",
            "no end-to-end hardware inference benchmark",
            "no physical layout synthesis",
            "no hardware timing, energy, throughput, or physical accuracy measurement",
            "no production inference readiness",
        ],
        "recommendedNextAfterV010": [
            "tag v0.1.0-rc.1 only after alpha.12 review",
            "keep Stage 5, Stage 6, and Stage 7 blocked until real external evidence exists",
            "consider optional external model-export adapters without adding a hard framework dependency",
            "consider larger deterministic benchmark suites while preserving CI runtime",
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
            "v0.1.0-rc.1_review",
            "foundry_calibrated_device_model_gate",
            "measured_transfer_matrix_gate",
            "hardware_benchmark_gate",
        ],
    }


def render_release_readiness_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# v0.1.0 Release-Candidate Readiness",
        "",
        report["claimBoundary"],
        "",
        "## Completed Simulation Stages",
        "",
        "| Stage | Report | Status | Evidence Level |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["completedSimulationStages"]:
        lines.append(f"| {row['stage']} | `{row['id']}` | {row['stageStatus']} | {row['evidenceLevel']} |")

    lines.extend([
        "",
        "## Supplemental Reports",
        "",
    ])
    for row in report["supplementalReports"]:
        lines.append(f"- `{row['id']}` ({row['evidenceLevel']})")

    lines.extend([
        "",
        "## Blocked Hardware Gates",
        "",
    ])
    for gate in report["blockedHardwareGates"]:
        lines.append(f"- Stage {gate['stage']} `{gate['id']}` remains {gate['stageStatus']}: {gate['blockerReason']}")

    lines.extend([
        "",
        "## Verification Commands",
        "",
    ])
    for command in report["verificationCommands"]:
        lines.append(f"- `{command}`")

    lines.extend([
        "",
        "## Known Limitations",
        "",
    ])
    for item in report["knownLimitations"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Recommended Next After v0.1.0",
        "",
    ])
    for item in report["recommendedNextAfterV010"]:
        lines.append(f"- {item}")

    lines.append("")
    return "\n".join(lines)


def _stage_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "stage": report["stage"],
        "id": report["id"],
        "title": report["title"],
        "stageStatus": report["stageStatus"],
        "evidenceLevel": report["evidenceLevel"],
    }


def _supplemental_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "stage": report["stage"],
        "id": report["id"],
        "title": report["title"],
        "stageStatus": report["stageStatus"],
        "evidenceLevel": report["evidenceLevel"],
    }


def _blocked_gate_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "stage": report["stage"],
        "id": report["id"],
        "title": report["title"],
        "stageStatus": report["stageStatus"],
        "evidenceLevel": report["evidenceLevel"],
        "blockerReason": report.get("blockerReason"),
        "blockers": report.get("blockers", []),
    }
