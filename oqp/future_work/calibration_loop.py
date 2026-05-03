"""Synthetic transfer-matrix calibration loop for future-work validation."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import List

from .mesh_mapping import build_mesh_transfer_model
from .neural_mapping import Matrix, relative_frobenius_error


@dataclass(frozen=True)
class CalibrationResult:
    calibration_mode: str
    measured_transfer_matrix_available: bool
    pre_calibration_error: float
    post_calibration_error: float
    iterations: int
    history: List[float]
    calibrated_matrix: Matrix


CALIBRATION_SWEEP_SEED = 31
CALIBRATION_SWEEP_DEFAULTS = {
    "initial_noise_std": 0.03,
    "learning_rate": 0.55,
    "calibration_iterations": 8,
    "mesh_phase_levels": 64,
}
CALIBRATION_SWEEP_DEFINITIONS = {
    "initial_noise_std": [0.0, 0.01, 0.03, 0.06, 0.1],
    "learning_rate": [0.1, 0.25, 0.55, 0.75, 1.0],
    "calibration_iterations": [1, 2, 4, 8, 12],
    "mesh_phase_levels": [16, 32, 64, 128],
}


def synthetic_initial_estimate(target: Matrix, seed: int = 11, noise_std: float = 0.03) -> Matrix:
    rng = random.Random(seed)
    return [[value + rng.gauss(0.0, noise_std) for value in row] for row in target]


def run_synthetic_calibration_loop(
    target: Matrix,
    initial_estimate: Matrix,
    iterations: int = 8,
    learning_rate: float = 0.55,
) -> CalibrationResult:
    if iterations < 1:
        raise ValueError("iterations must be positive")
    if not 0.0 < learning_rate <= 1.0:
        raise ValueError("learning_rate must be in (0, 1]")

    estimate = [row[:] for row in initial_estimate]
    history = [relative_frobenius_error(target, estimate)]
    for _ in range(iterations):
        estimate = [
            [
                estimate_value + learning_rate * (target_value - estimate_value)
                for estimate_value, target_value in zip(estimate_row, target_row)
            ]
            for estimate_row, target_row in zip(estimate, target)
        ]
        history.append(relative_frobenius_error(target, estimate))

    return CalibrationResult(
        calibration_mode="synthetic_simulation",
        measured_transfer_matrix_available=False,
        pre_calibration_error=history[0],
        post_calibration_error=history[-1],
        iterations=iterations,
        history=history,
        calibrated_matrix=estimate,
    )


def run_calibration_demo() -> dict:
    model = build_mesh_transfer_model()
    initial = synthetic_initial_estimate(model.transfer_matrix)
    result = run_synthetic_calibration_loop(model.target_matrix, initial)
    return {
        "id": "stage-4-simulated-calibration",
        "title": "Simulated transfer-matrix calibration loop",
        "stage": 4,
        "evidenceLevel": "synthetic_calibration_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": result.measured_transfer_matrix_available,
        "productionInferenceReady": False,
        "calibrationMode": result.calibration_mode,
        "calibrationUsesMeasuredData": False,
        "calibrationUsesSyntheticTarget": True,
        "oracleTargetAvailableInSimulation": True,
        "hardwareCalibrationClaimed": False,
        "claimBoundary": "Synthetic simulation-only calibration loop; this is not hardware calibration and does not use measured transfer matrices.",
        "preCalibrationRelativeError": round(result.pre_calibration_error, 15),
        "postCalibrationRelativeError": round(result.post_calibration_error, 15),
        "iterations": result.iterations,
        "history": [round(value, 15) for value in result.history],
        "blockers": [
            "no_measured_hrm_transfer_matrix",
            "no_hardware_calibration_run",
        ],
        "nextValidationGates": [
            "foundry_calibrated_device_model_gate",
            "measured_transfer_matrix_gate",
        ],
    }


def run_calibration_sweep_report() -> dict:
    rows = []
    for parameter, values in CALIBRATION_SWEEP_DEFINITIONS.items():
        for value in values:
            rows.append(_run_calibration_sweep_row(parameter, value))
    return {
        "id": "stage-4-calibration-sweep",
        "title": "Stage 4 synthetic calibration sensitivity sweep",
        "stage": 4,
        "evidenceLevel": "synthetic_calibration_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "calibrationUsesMeasuredData": False,
        "calibrationUsesSyntheticTarget": True,
        "oracleTargetAvailableInSimulation": True,
        "hardwareCalibrationClaimed": False,
        "claimBoundary": "Synthetic simulation-only calibration sensitivity sweep; this is not hardware calibration and does not use measured transfer matrices.",
        "rowCount": len(rows),
        "sweepParameters": list(CALIBRATION_SWEEP_DEFINITIONS.keys()),
        "defaultConfiguration": CALIBRATION_SWEEP_DEFAULTS,
        "rows": rows,
        "blockers": [
            "no_measured_hrm_transfer_matrix",
            "no_hardware_calibration_run",
        ],
        "nextValidationGates": [
            "foundry_calibrated_device_model_gate",
            "measured_transfer_matrix_gate",
        ],
    }


def run_calibration_sweep_analysis_report() -> dict:
    sweep = run_calibration_sweep_report()
    rows = sweep["rows"]
    parameter_summaries = [_calibration_parameter_summary(parameter, rows) for parameter in sweep["sweepParameters"]]
    best_case = min(rows, key=lambda row: (row["postCalibrationRelativeError"], row["sweepParameter"], row["sweepValue"]))
    worst_case = max(rows, key=lambda row: (row["postCalibrationRelativeError"], row["sweepParameter"], row["sweepValue"]))
    ranking = sorted(
        [
            {
                "sweepParameter": summary["sweepParameter"],
                "maxImprovementRatio": summary["maxImprovementRatio"],
                "minPostCalibrationRelativeError": summary["minPostCalibrationRelativeError"],
            }
            for summary in parameter_summaries
        ],
        key=lambda item: (-item["maxImprovementRatio"], item["sweepParameter"]),
    )
    failure_cases = [row for row in rows if row["convergenceStatus"] == "not_improved"]
    return {
        "id": "stage-4-calibration-analysis",
        "title": "Stage 4 synthetic calibration sweep analysis",
        "stage": 4,
        "evidenceLevel": "synthetic_calibration_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "calibrationUsesMeasuredData": False,
        "calibrationUsesSyntheticTarget": True,
        "oracleTargetAvailableInSimulation": True,
        "hardwareCalibrationClaimed": False,
        "claimBoundary": "Deterministic analysis of synthetic calibration sweeps only; no hardware calibration, foundry calibration, measured transfer matrix, or production inference readiness is claimed.",
        "rowCount": sweep["rowCount"],
        "sweepParameters": sweep["sweepParameters"],
        "parameterSummaries": parameter_summaries,
        "bestCaseRow": best_case,
        "worstCaseRow": worst_case,
        "bestCasePostCalibrationRelativeError": best_case["postCalibrationRelativeError"],
        "worstCasePostCalibrationRelativeError": worst_case["postCalibrationRelativeError"],
        "sensitivityRanking": ranking,
        "failureCaseCount": len(failure_cases),
        "failureCases": failure_cases,
        "limitations": [
            "synthetic oracle target available only in simulation",
            "no measured transfer matrix is used",
            "no hardware calibration run is represented",
            "one-parameter-at-a-time sweep with other calibration defaults held fixed",
            "small square deterministic matrix only",
            "real-valued abstract mesh target only",
        ],
        "blockers": [
            "no_measured_hrm_transfer_matrix",
            "no_hardware_calibration_run",
        ],
        "nextValidationGates": [
            "foundry_calibrated_device_model_gate",
            "measured_transfer_matrix_gate",
        ],
    }


def _run_calibration_sweep_row(parameter: str, value: float | int) -> dict:
    config = dict(CALIBRATION_SWEEP_DEFAULTS)
    if parameter not in config:
        raise ValueError(f"unknown calibration sweep parameter: {parameter}")
    config[parameter] = value
    model = build_mesh_transfer_model(phase_levels=int(config["mesh_phase_levels"]))
    initial = synthetic_initial_estimate(
        model.transfer_matrix,
        seed=CALIBRATION_SWEEP_SEED,
        noise_std=float(config["initial_noise_std"]),
    )
    result = run_synthetic_calibration_loop(
        model.target_matrix,
        initial,
        iterations=int(config["calibration_iterations"]),
        learning_rate=float(config["learning_rate"]),
    )
    improvement_ratio = _improvement_ratio(result.pre_calibration_error, result.post_calibration_error)
    improved = result.post_calibration_error <= result.pre_calibration_error
    return {
        "sweepParameter": parameter,
        "sweepValue": value,
        "seed": CALIBRATION_SWEEP_SEED,
        "preCalibrationRelativeError": round(result.pre_calibration_error, 15),
        "postCalibrationRelativeError": round(result.post_calibration_error, 15),
        "improvementRatio": round(improvement_ratio, 15),
        "calibrationIterations": result.iterations,
        "learningRate": float(config["learning_rate"]),
        "initialNoiseStd": float(config["initial_noise_std"]),
        "meshPhaseLevels": int(config["mesh_phase_levels"]),
        "convergenceStatus": "improved" if improved else "not_improved",
        "calibrationFailureReason": None if improved else "post_calibration_error_exceeds_pre_calibration_error",
        "evidenceLevel": "synthetic_calibration_simulation",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "hardwareCalibrationClaimed": False,
    }


def _calibration_parameter_summary(parameter: str, rows: List[dict]) -> dict:
    parameter_rows = [row for row in rows if row["sweepParameter"] == parameter]
    return {
        "sweepParameter": parameter,
        "rowCount": len(parameter_rows),
        "minPostCalibrationRelativeError": min(row["postCalibrationRelativeError"] for row in parameter_rows),
        "maxPostCalibrationRelativeError": max(row["postCalibrationRelativeError"] for row in parameter_rows),
        "maxImprovementRatio": max(row["improvementRatio"] for row in parameter_rows),
        "failureCaseCount": sum(1 for row in parameter_rows if row["convergenceStatus"] == "not_improved"),
    }


def _improvement_ratio(pre_error: float, post_error: float) -> float:
    if pre_error <= 1e-12:
        return 1.0 if post_error <= 1e-12 else 0.0
    return max(0.0, (pre_error - post_error) / pre_error)
