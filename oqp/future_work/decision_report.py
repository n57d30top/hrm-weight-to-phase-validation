"""Model-to-HRM decision report for simulation-only planning."""

from __future__ import annotations

from typing import Any, Dict, List

from .error_budget import run_error_budget_report
from .hardware_requirements import run_hardware_requirements_analysis_report
from .hardware_scenario_estimator import run_hardware_scenario_analysis_report
from .model_suitability import run_model_suitability_profile_report
from .validation_gates import foundry_calibration_gate, hardware_benchmark_gate, measured_transfer_matrix_gate


EVIDENCE_LEVEL = "simulation_only_model_to_hrm_decision"
DISCLAIMER = "This is a simulation-only decision report. It is not hardware evidence."
CLAIM_BOUNDARY = (
    DISCLAIMER
    + " It does not claim hardware validation, foundry calibration, measured transfer matrices, "
    "production inference readiness, real hardware latency, real hardware energy efficiency, quantum "
    "advantage, hardware-native intelligence, or power-free computation."
)
ALLOWED_DECISIONS = {
    "simulation_compatible",
    "partially_simulation_compatible",
    "poor_simulation_candidate",
    "blocked_by_missing_hardware_evidence",
}


def run_model_to_hrm_decision_report() -> Dict[str, Any]:
    suitability = run_model_suitability_profile_report()
    error_budget = run_error_budget_report()
    scenario = run_hardware_scenario_analysis_report()
    requirements = run_hardware_requirements_analysis_report()
    stage_5 = foundry_calibration_gate(None)
    stage_6 = measured_transfer_matrix_gate(None)
    stage_7 = hardware_benchmark_gate(None)
    decision = _decision(suitability, [stage_5, stage_6, stage_7])
    return {
        "id": "model-to-hrm-decision-report",
        "title": "Model-to-HRM simulation-only decision report",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "modelId": suitability["modelId"],
        "suitabilityScore": suitability["modelSuitabilityScore"],
        "suitabilityClass": suitability["suitabilityClass"],
        "mappableLayerSummary": {
            "mappableLayerCount": suitability["mappableLayerCount"],
            "mappableParameterShare": suitability["mappableParameterShare"],
            "rectangularLayerShare": suitability["rectangularLayerShare"],
            "complexLayerShare": suitability["complexLayerShare"],
        },
        "classicalLayerSummary": {
            "classicalLayerCount": suitability["classicalLayerCount"],
            "classicalComponents": [
                row["componentId"]
                for row in suitability["layerClassification"]
                if row["classification"].startswith("classical")
            ],
        },
        "unsupportedLayerSummary": {
            "unsupportedLayerCount": suitability["unsupportedLayerCount"],
            "unsupportedReasonCounts": suitability["unsupportedReasonCounts"],
        },
        "keyMappingErrors": {
            "dominantErrorContributor": error_budget["dominantErrorContributor"],
            "combinedErrorEnvelope": error_budget["combinedErrorEnvelope"],
        },
        "errorBudgetSummary": {
            "dominantErrorContributor": error_budget["dominantErrorContributor"]["component"],
            "secondaryErrorContributor": error_budget["secondaryErrorContributor"]["component"],
            "rss": error_budget["combinedErrorEnvelope"]["rss"],
            "conservativeMax": error_budget["combinedErrorEnvelope"]["conservativeMax"],
        },
        "hardwareScenarioSummary": {
            "bestLatencyScenario": scenario["bestLatencyScenario"],
            "bestEnergyScenario": scenario["bestEnergyScenario"],
            "warning": scenario["warning"],
        },
        "requirementsSummary": {
            "metRequirementCount": requirements["metRequirementCount"],
            "unmetRequirementCount": requirements["unmetRequirementCount"],
            "commonBottlenecks": requirements["commonBottlenecks"],
        },
        "missingEvidence": [
            "foundry-calibrated device model",
            "measured transfer matrix",
            "hardware benchmark",
        ],
        "decision": decision,
        "recommendedNextActions": [
            "keep model linear weights in the manifest path for simulation planning",
            "measure transfer matrices before considering Stage 6 complete",
            "collect hardware benchmark packages before considering Stage 7 complete",
            "use the requirements envelope to prioritize phase, drift, and loss measurements",
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "simulationOnly": True,
        "decisionIsNotHardwareValidation": True,
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
            "v0.1.0_rc1_readiness",
            "foundry_calibrated_device_model_gate",
            "measured_transfer_matrix_gate",
            "hardware_benchmark_gate",
        ],
    }


def render_model_to_hrm_decision_markdown(report: Dict[str, Any]) -> str:
    lines = [
        DISCLAIMER,
        "",
        "# Model-to-HRM Decision Report",
        "",
        f"Model: `{report['modelId']}`",
        "",
        "## Decision",
        "",
        f"- Decision class: `{report['decision']}`",
        f"- Suitability score: {report['suitabilityScore']}",
        f"- Suitability class: `{report['suitabilityClass']}`",
        "",
        "## Layer Summary",
        "",
        f"- Mappable layers: {report['mappableLayerSummary']['mappableLayerCount']}",
        f"- Classical components: {report['classicalLayerSummary']['classicalLayerCount']}",
        f"- Unsupported components: {report['unsupportedLayerSummary']['unsupportedLayerCount']}",
        "",
        "## Error Budget",
        "",
        f"- Dominant contributor: {report['errorBudgetSummary']['dominantErrorContributor']}",
        f"- RSS envelope: {report['errorBudgetSummary']['rss']}",
        "",
        "## Missing Evidence",
        "",
    ]
    for item in report["missingEvidence"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Recommended Next Actions",
        "",
    ])
    for item in report["recommendedNextActions"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        report["claimBoundary"],
        "",
    ])
    return "\n".join(lines)


def _decision(suitability: Dict[str, Any], hardware_gates: List[Dict[str, Any]]) -> str:
    if any(report["stageStatus"] == "blocked" for report in hardware_gates):
        return "blocked_by_missing_hardware_evidence"
    if suitability["suitabilityClass"] == "good_candidate":
        return "simulation_compatible"
    if suitability["suitabilityClass"] == "partial_candidate":
        return "partially_simulation_compatible"
    return "poor_simulation_candidate"
