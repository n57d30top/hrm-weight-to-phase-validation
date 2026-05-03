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
