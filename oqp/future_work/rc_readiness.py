"""v0.1.0-rc.1 readiness reporting for simulation-only planning work."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


EVIDENCE_LEVEL = "v0.1.0_rc1_readiness_audit"
GENERATED_AT = "2026-05-04T00:00:00Z"
CLAIM_BOUNDARY = (
    "This v0.1.0-rc.1 readiness report is simulation-only. It does not claim hardware validation, "
    "foundry calibration, measured transfer matrices, production inference readiness, real hardware "
    "latency, real hardware energy efficiency, quantum advantage, hardware-native intelligence, or "
    "power-free computation."
)


def run_rc1_readiness_report(
    stage_reports: Iterable[Dict[str, Any]],
    supplemental_reports: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    stages = list(stage_reports)
    supplemental = list(supplemental_reports)
    blocked_gates = [
        _blocked_gate_summary(report)
        for report in sorted(stages, key=lambda row: row["stage"])
        if report["stage"] in {5, 6, 7}
    ]
    included_capabilities = _included_capabilities(supplemental)
    decision_capabilities = [
        "model suitability profiling",
        "parametric hardware scenario estimates",
        "simulation-derived hardware requirements envelopes",
        "simulation-only error budget",
        "calibration and transfer-matrix assimilation planning",
        "model-to-HRM decision reporting",
    ]
    roadmap = _v02_recommended_work()
    return {
        "id": "v0.1.0-rc1-readiness",
        "title": "v0.1.0-rc.1 readiness report",
        "stage": 0,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "generatedAt": GENERATED_AT,
        "releaseCandidateFor": "v0.1.0",
        "includedCapabilities": included_capabilities,
        "includedCapabilityCount": len(included_capabilities),
        "simulationOnlyScope": [
            "mapping simulations",
            "deterministic benchmark reports",
            "manifest validation and eligibility analysis",
            "planning estimates labeled as parametric or simulation-derived",
            "blocked evidence gates for external hardware artifacts",
        ],
        "decisionReportCapabilities": decision_capabilities,
        "decisionReportCapabilityCount": len(decision_capabilities),
        "hardwareGatesBlocked": blocked_gates,
        "blockedHardwareGateCount": len(blocked_gates),
        "verificationCommands": [
            "make check",
            "jq empty reports/future-work/hrm-neural-mapping/v0.1.0-rc1-readiness.json",
            "sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256",
            "python3 scripts/check_artifact_hash_coverage.py",
            "python3 scripts/check_no_local_paths.py",
            "python3 scripts/check_claim_boundary.py",
            "git diff --check",
        ],
        "knownLimitations": [
            "simulation-only planning framework",
            "no foundry-calibrated device model",
            "no measured HRM transfer matrix",
            "no end-to-end hardware inference benchmark",
            "no measured hardware latency or energy",
            "no physical layout synthesis",
            "decision reports are not hardware evidence",
        ],
        "v0.2RecommendedWork": roadmap,
        "v02RoadmapItemCount": len(roadmap),
        "claimBoundary": CLAIM_BOUNDARY,
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
            "v0.2_planning",
            "foundry_calibrated_device_model_gate",
            "measured_transfer_matrix_gate",
            "hardware_benchmark_gate",
        ],
    }


def render_rc1_readiness_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# v0.1.0-rc.1 Readiness",
        "",
        report["claimBoundary"],
        "",
        "## Included Capabilities",
        "",
    ]
    for item in report["includedCapabilities"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Decision Report Capabilities",
        "",
    ])
    for item in report["decisionReportCapabilities"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Blocked Hardware Gates",
        "",
    ])
    for gate in report["hardwareGatesBlocked"]:
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
        "## v0.2 Recommended Work",
        "",
    ])
    for item in report["v0.2RecommendedWork"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _included_capabilities(supplemental: List[Dict[str, Any]]) -> List[str]:
    by_id = {report["id"] for report in supplemental}
    candidates = [
        ("rectangular-matrix-support", "rectangular matrix support"),
        ("complex-unitary-mesh-support", "complex/unitary factor simulation"),
        ("matrix-family-benchmark", "matrix-family benchmark suite"),
        ("layer-stack-inference-demo", "multi-layer toy inference"),
        ("model-weight-import-demo", "model-weight manifest import"),
        ("scaling-benchmark", "scaling and larger-layer benchmark"),
        ("model-suitability-profile", "model suitability profiler"),
        ("hardware-scenario-estimates", "parametric hardware scenario estimator"),
        ("hardware-requirements-envelope", "hardware requirements envelope"),
        ("error-budget-report", "simulation-only error budget"),
        ("calibration-plan", "calibration and assimilation planning"),
        ("model-to-hrm-decision-report", "model-to-HRM decision report"),
        ("model-portfolio-benchmark", "model portfolio benchmark"),
        ("model-export-adapter-demo", "optional export adapter protocol"),
        ("hardware-design-space-sweep", "hardware design-space explorer"),
        ("transfer-matrix-ingestion-sandbox", "synthetic transfer-matrix ingestion sandbox"),
    ]
    return [label for report_id, label in candidates if report_id in by_id]


def _v02_recommended_work() -> List[str]:
    return [
        "optional PyTorch export adapter that writes the existing model-weight manifest format",
        "larger deterministic model manifest fixtures",
        "richer model suitability scoring",
        "transfer-matrix measured-data ingestion once real data exists",
        "optional visualization dashboard for generated reports",
        "stronger synthetic calibration models",
        "foundry or PDK integration only with real external evidence",
    ]


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
