"""Perturbation model for the HRM neural mapping future-work track.

The model is deterministic when seeded and is intentionally not physically
calibrated. It provides a reproducible stress test for the abstract mesh model.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
import random
from typing import List

from .mesh_mapping import (
    GivensRotation,
    MeshApproximation,
    MeshTransferModel,
    build_abstract_phase_coupler_settings,
    build_mesh_transfer_model,
    reconstruct_from_givens,
)
from .neural_mapping import Matrix, matmul, relative_frobenius_error


@dataclass(frozen=True)
class PerturbationConfig:
    seed: int = 7
    phase_quantization_levels: int = 32
    phase_noise_std_rad: float = 0.002
    insertion_loss_db: float = 0.15
    coupler_imbalance: float = 0.01
    thermal_drift_rad_per_stage: float = 0.001
    detector_noise_std: float = 0.0005


@dataclass(frozen=True)
class PerturbedTransferModel:
    config: PerturbationConfig
    transfer_matrix: Matrix
    baseline_error: float
    perturbed_error: float
    error_delta: float
    physical_accuracy_claimed: bool


SWEEP_SEED = 17
SWEEP_DEFINITIONS = {
    "phase_quantization_bits": [3, 4, 5, 6, 7],
    "phase_noise_sigma_rad": [0.0, 0.001, 0.002, 0.005, 0.01],
    "insertion_loss_db": [0.0, 0.05, 0.15, 0.3, 0.6],
    "coupler_imbalance": [0.0, 0.005, 0.01, 0.02, 0.05],
    "thermal_drift_proxy_rad_per_stage": [0.0, 0.0005, 0.001, 0.002, 0.005],
    "detector_noise_placeholder_std": [0.0, 0.00025, 0.0005, 0.001, 0.002],
}


def apply_perturbations(model: MeshTransferModel, config: PerturbationConfig) -> PerturbedTransferModel:
    rng = random.Random(config.seed)
    left_mesh = _perturb_mesh(model.left_mesh, config, rng)
    right_mesh = _perturb_mesh(model.right_mesh, config, rng)
    singular_values = _perturb_singular_values(model.singular_values, config)
    sigma = [[0.0 for _ in singular_values] for _ in singular_values]
    for index, value in enumerate(singular_values):
        sigma[index][index] = value
    transfer = matmul(matmul(left_mesh.approximation, sigma), right_mesh.approximation)
    transfer = _apply_detector_noise(transfer, config, rng)
    perturbed_error = relative_frobenius_error(model.target_matrix, transfer)
    return PerturbedTransferModel(
        config=config,
        transfer_matrix=transfer,
        baseline_error=model.mesh_error,
        perturbed_error=perturbed_error,
        error_delta=perturbed_error - model.mesh_error,
        physical_accuracy_claimed=False,
    )


def run_perturbation_demo() -> dict:
    model = build_mesh_transfer_model()
    config = PerturbationConfig()
    perturbed = apply_perturbations(model, config)
    return {
        "id": "stage-3-perturbation-model",
        "title": "Quantization, drift, loss, and noise perturbation model",
        "stage": 3,
        "evidenceLevel": "uncalibrated_perturbation_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Uncalibrated deterministic perturbation simulation only; no physical accuracy, hardware validation, or production inference readiness is claimed.",
        "physicalAccuracyClaimed": perturbed.physical_accuracy_claimed,
        "perturbations": {
            "phaseQuantizationLevels": config.phase_quantization_levels,
            "phaseNoiseStdRad": config.phase_noise_std_rad,
            "insertionLossDb": config.insertion_loss_db,
            "couplerImbalance": config.coupler_imbalance,
            "thermalDriftRadPerStage": config.thermal_drift_rad_per_stage,
            "detectorNoiseStd": config.detector_noise_std,
            "seed": config.seed,
        },
        "baselineMeshRelativeError": round(perturbed.baseline_error, 15),
        "perturbedRelativeError": round(perturbed.perturbed_error, 15),
        "errorDelta": round(perturbed.error_delta, 15),
        "blockers": [
            "no_foundry_calibrated_loss_phase_noise_model",
            "no_measured_drift_or_detector_noise_data",
        ],
        "nextValidationGates": [
            "synthetic_transfer_matrix_calibration",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_perturbation_sweep_report() -> dict:
    model = build_mesh_transfer_model()
    rows = []
    for parameter, values in SWEEP_DEFINITIONS.items():
        for value in values:
            config = _config_for_sweep(parameter, value)
            perturbed = apply_perturbations(model, config)
            rows.append({
                "sweepParameter": parameter,
                "sweepValue": value,
                "seed": config.seed,
                "phaseQuantizationLevels": config.phase_quantization_levels,
                "baselineMeshRelativeError": round(perturbed.baseline_error, 15),
                "perturbedRelativeError": round(perturbed.perturbed_error, 15),
                "errorDelta": round(perturbed.error_delta, 15),
                "evidenceLevel": "uncalibrated_perturbation_simulation",
                "hardwareValidated": False,
                "foundryCalibrated": False,
                "measuredTransferMatrixAvailable": False,
                "productionInferenceReady": False,
            })
    return {
        "id": "stage-3-perturbation-sweep",
        "title": "Stage 3 deterministic perturbation sensitivity sweep",
        "stage": 3,
        "evidenceLevel": "uncalibrated_perturbation_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "physicalAccuracyClaimed": False,
        "claimBoundary": "Deterministic uncalibrated perturbation sweep only; no physical accuracy, hardware validation, foundry calibration, measured transfer matrix, or production inference readiness is claimed.",
        "baselineMeshRelativeError": round(model.mesh_error, 15),
        "rowCount": len(rows),
        "sweepParameters": list(SWEEP_DEFINITIONS.keys()),
        "rows": rows,
        "blockers": [
            "no_foundry_calibrated_loss_phase_noise_model",
            "no_measured_drift_or_detector_noise_data",
        ],
        "nextValidationGates": [
            "synthetic_transfer_matrix_calibration",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_perturbation_sweep_analysis_report() -> dict:
    sweep = run_perturbation_sweep_report()
    rows = sweep["rows"]
    parameter_summaries = [_parameter_summary(parameter, rows) for parameter in sweep["sweepParameters"]]
    sensitivity_ranking = sorted(
        [
            {
                "sweepParameter": summary["sweepParameter"],
                "maxErrorDelta": summary["maxErrorDelta"],
                "maxPerturbedRelativeError": summary["maxPerturbedRelativeError"],
            }
            for summary in parameter_summaries
        ],
        key=lambda item: (-item["maxErrorDelta"], item["sweepParameter"]),
    )
    worst_case = max(rows, key=lambda row: (row["errorDelta"], row["sweepParameter"], row["sweepValue"]))
    best_case = min(rows, key=lambda row: (row["perturbedRelativeError"], row["sweepParameter"], row["sweepValue"]))
    control = _control_all_perturbations_disabled()
    return {
        "id": "stage-3-sweep-analysis",
        "title": "Stage 3 perturbation sweep sensitivity analysis",
        "stage": 3,
        "evidenceLevel": "uncalibrated_perturbation_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "physicalAccuracyClaimed": False,
        "claimBoundary": "Deterministic analysis of uncalibrated perturbation sweeps only; no physical accuracy, hardware validation, foundry calibration, measured transfer matrix, or production inference readiness is claimed.",
        "baselineMeshRelativeError": sweep["baselineMeshRelativeError"],
        "rowCount": sweep["rowCount"],
        "sweepParameters": sweep["sweepParameters"],
        "parameterSummaries": parameter_summaries,
        "worstCaseRow": worst_case,
        "bestCaseRow": best_case,
        "worstCaseErrorDelta": worst_case["errorDelta"],
        "bestCasePerturbedRelativeError": best_case["perturbedRelativeError"],
        "sensitivityRanking": sensitivity_ranking,
        "controlSummary": control,
        "monotonicityNotes": [
            "Monotonicity is not expected as a physical law in this report.",
            "Each one-parameter sweep is evaluated under the fixed baseline perturbation configuration unless that parameter is explicitly overridden.",
            "Deterministic noise samples, quantization, loss scaling, and mesh approximation error can interact nonlinearly.",
        ],
        "limitations": [
            "uncalibrated simulation only",
            "small square deterministic matrix only",
            "real-valued orthogonal mesh approximation only",
            "one-parameter-at-a-time sweep with other perturbation defaults left enabled",
            "deterministic seeds support reproducibility but do not represent measured noise statistics",
            "no foundry-calibrated loss, phase-noise, drift, crosstalk, or detector model",
            "no measured transfer matrix or hardware calibration loop",
        ],
        "blockers": [
            "no_foundry_calibrated_loss_phase_noise_model",
            "no_measured_drift_or_detector_noise_data",
        ],
        "nextValidationGates": [
            "synthetic_transfer_matrix_calibration",
            "foundry_calibrated_device_model_gate",
        ],
    }


def _perturb_mesh(mesh: MeshApproximation, config: PerturbationConfig, rng: random.Random) -> MeshApproximation:
    rotations: List[GivensRotation] = []
    for index, rotation in enumerate(mesh.rotations):
        quantized = _quantize(rotation.theta, config.phase_quantization_levels)
        noisy = quantized + rng.gauss(0.0, config.phase_noise_std_rad)
        drifted = noisy + config.thermal_drift_rad_per_stage * (index + 1)
        rotations.append(GivensRotation(rotation.row_a, rotation.row_b, drifted))
    approximation = reconstruct_from_givens(mesh.size, rotations, mesh.output_signs)
    phase_settings, coupler_settings = build_abstract_phase_coupler_settings(rotations, mesh.output_signs)
    return MeshApproximation(
        size=mesh.size,
        phase_levels=config.phase_quantization_levels,
        rotations=rotations,
        output_signs=mesh.output_signs,
        phase_settings=phase_settings,
        coupler_settings=coupler_settings,
        approximation=approximation,
        limitations=mesh.limitations,
    )


def _perturb_singular_values(values: List[float], config: PerturbationConfig) -> List[float]:
    loss_scale = 10 ** (-config.insertion_loss_db / 20.0)
    perturbed = []
    for index, value in enumerate(values):
        imbalance = 1.0 + (config.coupler_imbalance if index % 2 == 0 else -config.coupler_imbalance)
        perturbed.append(max(0.0, min(1.0, value * loss_scale * imbalance)))
    return perturbed


def _apply_detector_noise(matrix: Matrix, config: PerturbationConfig, rng: random.Random) -> Matrix:
    if config.detector_noise_std <= 0.0:
        return [row[:] for row in matrix]
    return [[value + rng.gauss(0.0, config.detector_noise_std) for value in row] for row in matrix]


def _config_for_sweep(parameter: str, value: float | int) -> PerturbationConfig:
    config = PerturbationConfig(seed=SWEEP_SEED)
    if parameter == "phase_quantization_bits":
        return replace(config, phase_quantization_levels=2 ** int(value))
    if parameter == "phase_noise_sigma_rad":
        return replace(config, phase_noise_std_rad=float(value))
    if parameter == "insertion_loss_db":
        return replace(config, insertion_loss_db=float(value))
    if parameter == "coupler_imbalance":
        return replace(config, coupler_imbalance=float(value))
    if parameter == "thermal_drift_proxy_rad_per_stage":
        return replace(config, thermal_drift_rad_per_stage=float(value))
    if parameter == "detector_noise_placeholder_std":
        return replace(config, detector_noise_std=float(value))
    raise ValueError(f"unknown sweep parameter: {parameter}")


def _parameter_summary(parameter: str, rows: List[dict]) -> dict:
    parameter_rows = [row for row in rows if row["sweepParameter"] == parameter]
    min_error = min(row["perturbedRelativeError"] for row in parameter_rows)
    max_error = max(row["perturbedRelativeError"] for row in parameter_rows)
    max_delta = max(row["errorDelta"] for row in parameter_rows)
    return {
        "sweepParameter": parameter,
        "rowCount": len(parameter_rows),
        "minPerturbedRelativeError": min_error,
        "maxPerturbedRelativeError": max_error,
        "maxErrorDelta": max_delta,
        "observedMonotonicNondecreasing": _is_monotonic_nondecreasing(
            [row["perturbedRelativeError"] for row in parameter_rows]
        ),
        "monotonicityExpected": False,
        "monotonicityNote": "Not expected from this uncalibrated one-parameter sweep because other default perturbations remain enabled unless explicitly overridden.",
    }


def _control_all_perturbations_disabled() -> dict:
    model = build_mesh_transfer_model()
    result = apply_perturbations(model, PerturbationConfig(
        seed=SWEEP_SEED,
        phase_quantization_levels=64,
        phase_noise_std_rad=0.0,
        insertion_loss_db=0.0,
        coupler_imbalance=0.0,
        thermal_drift_rad_per_stage=0.0,
        detector_noise_std=0.0,
    ))
    delta = result.perturbed_error - model.mesh_error
    return {
        "id": "control_all_perturbations_disabled",
        "description": "All Stage 3 perturbations disabled; expected to match or remain close to the Stage 2 baseline mesh error.",
        "seed": SWEEP_SEED,
        "baselineMeshRelativeError": round(model.mesh_error, 15),
        "controlRelativeError": round(result.perturbed_error, 15),
        "controlErrorDelta": round(delta, 15),
        "controlMatchesBaselineWithinTolerance": abs(delta) <= 1e-12,
        "tolerance": 1e-12,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _is_monotonic_nondecreasing(values: List[float]) -> bool:
    return all(current <= following for current, following in zip(values, values[1:]))


def _quantize(value: float, levels: int) -> float:
    if levels < 2:
        raise ValueError("phase_quantization_levels must be at least 2")
    step = (2.0 * math.pi) / (levels - 1)
    return round(value / step) * step
