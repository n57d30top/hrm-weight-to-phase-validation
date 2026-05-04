"""Simulation-derived hardware requirement envelopes for HRM neural planning."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List


EVIDENCE_LEVEL = "simulation_derived_hardware_requirements"
ANALYSIS_EVIDENCE_LEVEL = "simulation_derived_hardware_requirements_analysis"
CLAIM_BOUNDARY = (
    "Simulation-derived requirement envelope only; these are not real hardware specifications, "
    "hardware validation, foundry calibration, measured transfer matrices, production inference "
    "readiness, or quantum advantage."
)

TARGET_ERRORS = [0.10, 0.05, 0.02]
CASE_BASE_ERRORS = {
    "identity_4x4": 0.0,
    "rectangular_tall_8x4": 0.099951757092972,
    "complex_phase_dominant_4x4": 0.026860550074221,
    "tiny_mlp_4_6_3": 0.061296868009442,
}


def run_hardware_requirements_envelope_report() -> Dict[str, Any]:
    rows = [
        _requirement_row(case_id, base_error, target_error)
        for target_error in TARGET_ERRORS
        for case_id, base_error in CASE_BASE_ERRORS.items()
    ]
    return {
        "id": "hardware-requirements-envelope",
        "title": "Simulation-derived hardware requirement envelope",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "targetOutputRelativeErrorValues": TARGET_ERRORS,
        "caseCount": len(CASE_BASE_ERRORS),
        "rowCount": len(rows),
        "simulationDerivedOnly": True,
        "requirements": rows,
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": [
            "no_foundry_calibrated_device_model",
            "no_measured_transfer_matrix",
            "no_hardware_benchmark",
        ],
        "nextValidationGates": [
            "error_budget_report",
            "calibration_planner",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_hardware_requirements_analysis_report() -> Dict[str, Any]:
    envelope = run_hardware_requirements_envelope_report()
    rows = envelope["requirements"]
    met_rows = [row for row in rows if row["requirementStatus"] == "met_in_simulated_envelope"]
    unmet_rows = [row for row in rows if row["requirementStatus"] != "met_in_simulated_envelope"]
    return {
        "id": "hardware-requirements-analysis",
        "title": "Simulation-derived hardware requirements analysis",
        "stage": 2,
        "evidenceLevel": ANALYSIS_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "simulationDerivedOnly": True,
        "targetOutputRelativeErrorValues": TARGET_ERRORS,
        "easiestCaseRequirements": _case_requirements_summary("identity_4x4", rows),
        "hardestCaseRequirements": _case_requirements_summary("rectangular_tall_8x4", rows),
        "commonBottlenecks": _common_bottlenecks(unmet_rows),
        "requirementsByTargetError": _requirements_by_target(rows),
        "recommendationsForLabMeasurement": [
            "measure phase-setting repeatability before interpreting phase-noise requirements",
            "measure insertion-loss distributions across the mesh",
            "measure coupler imbalance and thermal drift under operating conditions",
            "provide measured transfer matrices before changing Stage 6 status",
        ],
        "metRequirementCount": len(met_rows),
        "unmetRequirementCount": len(unmet_rows),
        "limitations": [
            "requirements are deterministic envelopes derived from simulation cases",
            "no foundry-calibrated device model is used",
            "no measured transfer matrix is used",
            "thresholds below baseline simulation error are reported as not met",
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": envelope["blockers"],
        "nextValidationGates": envelope["nextValidationGates"],
    }


def _requirement_row(case_id: str, base_error: float, target_error: float) -> Dict[str, Any]:
    slack = target_error - base_error
    if slack <= 0.0:
        return {
            "targetError": target_error,
            "caseId": case_id,
            "baselineSimulationError": base_error,
            "requirementStatus": "not_met_in_simulated_sweep",
            "requiredPhaseResolutionBits": None,
            "maxPhaseNoiseSigmaRad": None,
            "maxInsertionLossDb": None,
            "maxCouplerImbalance": None,
            "maxThermalDriftProxyRad": None,
            "maxDetectorNoiseStd": None,
            "calibrationAssumption": "synthetic_oracle_calibration_only",
            "simulationDerivedOnly": True,
            "requirementBottleneck": "baseline_simulation_error_exceeds_target",
            "hardwareValidated": False,
            "foundryCalibrated": False,
            "measuredTransferMatrixAvailable": False,
            "productionInferenceReady": False,
        }
    strictness = _target_strictness(target_error)
    return {
        "targetError": target_error,
        "caseId": case_id,
        "baselineSimulationError": base_error,
        "requirementStatus": "met_in_simulated_envelope",
        "requiredPhaseResolutionBits": strictness["phase_bits"],
        "maxPhaseNoiseSigmaRad": round(min(slack * 0.25, strictness["phase_noise"]), 6),
        "maxInsertionLossDb": round(min(slack * 5.0, strictness["loss_db"]), 6),
        "maxCouplerImbalance": round(min(slack * 0.5, strictness["coupler"]), 6),
        "maxThermalDriftProxyRad": round(min(slack * 0.35, strictness["drift"]), 6),
        "maxDetectorNoiseStd": round(min(slack * 0.2, strictness["detector"]), 6),
        "calibrationAssumption": "synthetic_oracle_calibration_only",
        "simulationDerivedOnly": True,
        "requirementBottleneck": "phase_resolution_and_drift",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _target_strictness(target_error: float) -> Dict[str, Any]:
    if target_error <= 0.02:
        return {"phase_bits": 10, "phase_noise": 0.003, "loss_db": 0.05, "coupler": 0.005, "drift": 0.003, "detector": 0.001}
    if target_error <= 0.05:
        return {"phase_bits": 8, "phase_noise": 0.01, "loss_db": 0.15, "coupler": 0.015, "drift": 0.01, "detector": 0.004}
    return {"phase_bits": 6, "phase_noise": 0.03, "loss_db": 0.35, "coupler": 0.04, "drift": 0.025, "detector": 0.01}


def _case_requirements_summary(case_id: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    case_rows = [row for row in rows if row["caseId"] == case_id]
    return {
        "caseId": case_id,
        "rows": case_rows,
        "metTargets": [row["targetError"] for row in case_rows if row["requirementStatus"] == "met_in_simulated_envelope"],
        "unmetTargets": [row["targetError"] for row in case_rows if row["requirementStatus"] != "met_in_simulated_envelope"],
    }


def _common_bottlenecks(unmet_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts = Counter(row["requirementBottleneck"] for row in unmet_rows)
    return [
        {"bottleneck": key, "count": value}
        for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _requirements_by_target(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["targetError"])].append(row)
    return {
        target: {
            "metCount": sum(1 for row in target_rows if row["requirementStatus"] == "met_in_simulated_envelope"),
            "notMetCount": sum(1 for row in target_rows if row["requirementStatus"] != "met_in_simulated_envelope"),
        }
        for target, target_rows in sorted(grouped.items(), key=lambda item: float(item[0]), reverse=True)
    }
