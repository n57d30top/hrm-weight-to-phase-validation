"""Simulation-only error budget for HRM neural future work."""

from __future__ import annotations

import math
from typing import Any, Dict, List

from .complex_unitary_mapping import run_complex_unitary_mesh_support_report
from .layer_stack_inference import run_layer_stack_inference_demo_report
from .mesh_mapping import run_mesh_constrained_demo
from .perturbation_model import run_perturbation_sweep_analysis_report
from .rectangular_mapping import run_rectangular_matrix_support_report
from .scaling_benchmark import run_scaling_analysis_report
from .calibration_loop import run_calibration_sweep_analysis_report


EVIDENCE_LEVEL = "simulation_error_budget"
CLAIM_BOUNDARY = (
    "Simulation-only error budget; no physical accuracy, hardware validation, foundry calibration, "
    "measured transfer matrices, production inference readiness, real hardware latency, or real "
    "hardware energy efficiency is claimed."
)


def run_error_budget_report() -> Dict[str, Any]:
    components = _component_errors()
    ordered = sorted(components, key=lambda row: row["errorValue"], reverse=True)
    values = [row["errorValue"] for row in components]
    additive = sum(values)
    rss = math.sqrt(sum(value * value for value in values))
    conservative = max(values)
    return {
        "id": "error-budget-report",
        "title": "Simulation-only accuracy degradation and error budget",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "budgetId": "simulation_error_budget_v1",
        "componentErrors": components,
        "combinedErrorEnvelope": {
            "additive": round(additive, 15),
            "rss": round(rss, 15),
            "conservativeMax": round(conservative, 15),
        },
        "dominantErrorContributor": ordered[0],
        "secondaryErrorContributor": ordered[1],
        "additiveModelUsed": True,
        "rssModelUsed": True,
        "conservativeMaxModelUsed": True,
        "simulationOnly": True,
        "physicalAccuracyClaimed": False,
        "uncertaintyNotes": [
            "components come from different deterministic reports and are not statistically independent",
            "additive and RSS envelopes are planning views only",
            "measured transfer matrices would be required to reduce hardware uncertainty",
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": [
            "no_measured_transfer_matrix",
            "no_foundry_calibrated_device_model",
            "no_hardware_benchmark",
        ],
        "nextValidationGates": [
            "calibration_planner",
            "model_to_hrm_decision_report",
            "measured_transfer_matrix_gate",
        ],
    }


def render_error_budget_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Simulation Error Budget",
        "",
        "This is a simulation-only error budget. It is not a hardware accuracy claim.",
        "",
        "## Components",
        "",
        "| Component | Error | Source |",
        "| --- | --- | --- |",
    ]
    for row in report["componentErrors"]:
        lines.append(f"| {row['component']} | {row['errorValue']} | `{row['sourceReport']}` |")
    lines.extend([
        "",
        "## Combined Envelope",
        "",
        f"- Additive model: {report['combinedErrorEnvelope']['additive']}",
        f"- RSS model: {report['combinedErrorEnvelope']['rss']}",
        f"- Conservative max model: {report['combinedErrorEnvelope']['conservativeMax']}",
        "",
        "## Dominant Contributors",
        "",
        f"- Dominant: {report['dominantErrorContributor']['component']}",
        f"- Secondary: {report['secondaryErrorContributor']['component']}",
        "",
        "## What To Improve First",
        "",
        "- reduce the largest simulated scaling and perturbation terms before interpreting smaller residuals",
        "- use measured transfer matrices to replace simulation-only uncertainty terms when real data exists",
        "",
        "## Claim Boundary",
        "",
        report["claimBoundary"],
        "",
    ])
    return "\n".join(lines)


def _component_errors() -> List[Dict[str, Any]]:
    stage2 = run_mesh_constrained_demo()
    rectangular = run_rectangular_matrix_support_report()
    complex_report = run_complex_unitary_mesh_support_report()
    perturbation = run_perturbation_sweep_analysis_report()
    calibration = run_calibration_sweep_analysis_report()
    layer_stack = run_layer_stack_inference_demo_report()
    scaling = run_scaling_analysis_report()
    return [
        _component("baselineMappingError", stage2["meshConstrainedRelativeError"], "stage-2-mesh-constrained.json"),
        _component("rectangularMappingError", rectangular["meshConstrainedReconstructionErrorMax"], "rectangular-matrix-support.json"),
        _component("complexUnitaryApproximationError", complex_report["phaseAwareErrorMax"], "complex-unitary-mesh-support.json"),
        _component("perturbationError", perturbation["worstCaseErrorDelta"], "stage-3-sweep-analysis.json"),
        _component("calibrationResidualError", calibration["worstCasePostCalibrationRelativeError"], "stage-4-calibration-analysis.json"),
        _component("layerStackOutputError", layer_stack["outputRelativeErrorMax"], "layer-stack-inference-demo.json"),
        _component("scalingWorstCaseError", scaling["maxMeshConstrainedError"], "scaling-analysis.json"),
    ]


def _component(component: str, value: float, source: str) -> Dict[str, Any]:
    return {
        "component": component,
        "errorValue": value,
        "sourceReport": source,
        "simulationOnly": True,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }
