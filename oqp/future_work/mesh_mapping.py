"""Abstract mesh-constrained mapping for HRM neural future work.

This module implements a deterministic real-valued rotation mesh approximation.
It is an abstract simulation layer only. It is not a foundry layout, not an HRM
chip calibration, and not a production phase synthesis algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Sequence

from .neural_mapping import (
    Matrix,
    deterministic_weight_matrix,
    matmul,
    passive_normalize_singular_values,
    reconstruct_from_svd,
    relative_frobenius_error,
    scalar_multiply,
    svd_decompose,
    transpose,
)


@dataclass(frozen=True)
class GivensRotation:
    row_a: int
    row_b: int
    theta: float


@dataclass(frozen=True)
class AbstractPhaseSetting:
    role: str
    target: str
    radians: float


@dataclass(frozen=True)
class AbstractCouplerSetting:
    row_a: int
    row_b: int
    theta: float
    through_power: float
    cross_power: float


@dataclass(frozen=True)
class MeshApproximation:
    size: int
    phase_levels: int
    rotations: List[GivensRotation]
    output_signs: List[float]
    phase_settings: List[AbstractPhaseSetting]
    coupler_settings: List[AbstractCouplerSetting]
    approximation: Matrix
    limitations: List[str]


@dataclass(frozen=True)
class MeshTransferModel:
    target_matrix: Matrix
    singular_values: List[float]
    left_mesh: MeshApproximation
    right_mesh: MeshApproximation
    transfer_matrix: Matrix
    ideal_error: float
    mesh_error: float


def approximate_orthogonal_with_mesh(matrix: Matrix, phase_levels: int = 64) -> MeshApproximation:
    if phase_levels < 2:
        raise ValueError("phase_levels must be at least 2")
    _assert_square(matrix)
    size = len(matrix)
    rotations, signs = decompose_orthogonal_to_givens(matrix)
    quantized = [
        GivensRotation(rotation.row_a, rotation.row_b, quantize_phase(rotation.theta, phase_levels))
        for rotation in rotations
    ]
    approximation = reconstruct_from_givens(size, quantized, signs)
    phase_settings, coupler_settings = build_abstract_phase_coupler_settings(quantized, signs)
    return MeshApproximation(
        size=size,
        phase_levels=phase_levels,
        rotations=quantized,
        output_signs=signs,
        phase_settings=phase_settings,
        coupler_settings=coupler_settings,
        approximation=approximation,
        limitations=[
            "real-valued orthogonal rotation mesh only",
            "deterministic abstract phase and coupler settings only",
            "not a real fabricated chip mesh or foundry-calibrated HRM layout",
            "no routing constraints, thermal crosstalk model, wavelength model, splitter excess-loss model, or measured transfer matrix",
        ],
    )


def build_abstract_phase_coupler_settings(
    rotations: Sequence[GivensRotation],
    signs: Sequence[float],
) -> tuple[List[AbstractPhaseSetting], List[AbstractCouplerSetting]]:
    phase_settings: List[AbstractPhaseSetting] = []
    coupler_settings: List[AbstractCouplerSetting] = []
    for index, rotation in enumerate(rotations):
        phase_settings.append(AbstractPhaseSetting(
            role="rotation_phase",
            target=f"rotation_{index}_rows_{rotation.row_a}_{rotation.row_b}",
            radians=_wrap_phase(rotation.theta),
        ))
        coupler_settings.append(AbstractCouplerSetting(
            row_a=rotation.row_a,
            row_b=rotation.row_b,
            theta=rotation.theta,
            through_power=math.cos(rotation.theta) ** 2,
            cross_power=math.sin(rotation.theta) ** 2,
        ))
    for index, sign in enumerate(signs):
        if sign < 0.0:
            phase_settings.append(AbstractPhaseSetting(
                role="output_sign_phase",
                target=f"output_{index}",
                radians=math.pi,
            ))
    return phase_settings, coupler_settings


def decompose_orthogonal_to_givens(matrix: Matrix) -> tuple[List[GivensRotation], List[float]]:
    _assert_square(matrix)
    size = len(matrix)
    working = [row[:] for row in matrix]
    rotations: List[GivensRotation] = []
    for col in range(size):
        for row in range(size - 1, col, -1):
            upper = working[row - 1][col]
            lower = working[row][col]
            radius = math.hypot(upper, lower)
            if radius <= 1e-12:
                continue
            c = upper / radius
            s = lower / radius
            theta = math.atan2(s, c)
            _left_apply_givens(working, row - 1, row, theta)
            rotations.append(GivensRotation(row - 1, row, theta))
    signs = [1.0 if working[index][index] >= 0 else -1.0 for index in range(size)]
    return rotations, signs


def reconstruct_from_givens(size: int, rotations: Sequence[GivensRotation], signs: Sequence[float]) -> Matrix:
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    for index in range(size):
        matrix[index][index] = signs[index] if index < len(signs) else 1.0
    for rotation in reversed(rotations):
        _left_apply_givens_transpose(matrix, rotation.row_a, rotation.row_b, rotation.theta)
    return matrix


def build_mesh_transfer_model(weight_matrix: Matrix | None = None, phase_levels: int = 64) -> MeshTransferModel:
    weight_matrix = weight_matrix if weight_matrix is not None else deterministic_weight_matrix()
    svd = svd_decompose(weight_matrix)
    normalized_singulars = passive_normalize_singular_values(svd.singular_values)
    max_singular = max(svd.singular_values) if svd.singular_values else 0.0
    target_scale = 0.0 if max_singular <= 1e-12 else 1.0 / max_singular
    target = scalar_multiply(weight_matrix, target_scale)
    ideal = reconstruct_from_svd(svd, normalized_singulars)

    left_mesh = approximate_orthogonal_with_mesh(svd.u, phase_levels=phase_levels)
    right_mesh = approximate_orthogonal_with_mesh(svd.vh, phase_levels=phase_levels)
    sigma = [[0.0 for _ in normalized_singulars] for _ in normalized_singulars]
    for index, value in enumerate(normalized_singulars):
        sigma[index][index] = value
    transfer = matmul(matmul(left_mesh.approximation, sigma), right_mesh.approximation)

    return MeshTransferModel(
        target_matrix=target,
        singular_values=normalized_singulars,
        left_mesh=left_mesh,
        right_mesh=right_mesh,
        transfer_matrix=transfer,
        ideal_error=relative_frobenius_error(target, ideal),
        mesh_error=relative_frobenius_error(target, transfer),
    )


def run_mesh_constrained_demo(phase_levels: int = 64) -> dict:
    model = build_mesh_transfer_model(phase_levels=phase_levels)
    phase_count = len(model.left_mesh.phase_settings) + len(model.right_mesh.phase_settings)
    coupler_count = len(model.left_mesh.coupler_settings) + len(model.right_mesh.coupler_settings)
    return {
        "id": "stage-2-mesh-constrained",
        "title": "Mesh-constrained HRM transfer-matrix approximation",
        "stage": 2,
        "evidenceLevel": "abstract_mesh_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "meshModel": "abstract_hrm_mesh_simulation",
        "realChipMesh": False,
        "meshParameterizationStatus": "deterministic_abstract_phase_coupler_parameterization",
        "abstractRotationParameterizationImplemented": True,
        "abstractPhaseParameterizationImplemented": True,
        "abstractCouplerParameterizationImplemented": True,
        "physicalPhaseSynthesisImplemented": False,
        "physicalCouplerSynthesisImplemented": False,
        "foundryLayoutSynthesisImplemented": False,
        "complexUnitaryMeshImplemented": False,
        "rectangularLayerSupportImplemented": False,
        "clementsReckPhysicalLayoutImplemented": False,
        "activeGainImplemented": False,
        "claimBoundary": "Abstract real-valued mesh approximation only; this is not a real chip mesh, foundry layout, measured transfer matrix, or production inference path.",
        "currentDemoScope": [
            "small deterministic matrix",
            "square matrix only",
            "real-valued orthogonal approximation",
            "no complex unitary mesh",
            "no rectangular neural layer support",
            "no Clements or Reck physical interferometer layout",
        ],
        "phaseLevels": phase_levels,
        "phaseCount": phase_count,
        "couplerCount": coupler_count,
        "matrixShape": [len(model.target_matrix), len(model.target_matrix[0]) if model.target_matrix else 0],
        "squareMatrixOnly": True,
        "realValuedOrthogonalApproximation": True,
        "leftMeshPhaseCount": len(model.left_mesh.phase_settings),
        "leftMeshCouplerCount": len(model.left_mesh.coupler_settings),
        "rightMeshPhaseCount": len(model.right_mesh.phase_settings),
        "rightMeshCouplerCount": len(model.right_mesh.coupler_settings),
        "abstractMeshParameterization": {
            "left": _mesh_parameterization_report(model.left_mesh),
            "right": _mesh_parameterization_report(model.right_mesh),
        },
        "singularValuesPassiveRange": [round(value, 12) for value in model.singular_values],
        "idealSvdRelativeError": round(model.ideal_error, 15),
        "meshConstrainedRelativeError": round(model.mesh_error, 15),
        "meshErrorDelta": round(model.mesh_error - model.ideal_error, 15),
        "leftMeshRotationCount": len(model.left_mesh.rotations),
        "rightMeshRotationCount": len(model.right_mesh.rotations),
        "meshLimitations": sorted(set(model.left_mesh.limitations + model.right_mesh.limitations)),
        "limitations": sorted(set(model.left_mesh.limitations + model.right_mesh.limitations)),
        "blockers": [
            "no_foundry_calibrated_mesh_model",
            "no_measured_transfer_matrix",
        ],
        "nextValidationGates": [
            "quantization_drift_loss_noise_perturbation",
            "synthetic_transfer_matrix_calibration",
            "foundry_calibrated_device_model_gate",
        ],
    }


def quantize_phase(theta: float, phase_levels: int) -> float:
    step = (2.0 * math.pi) / (phase_levels - 1)
    return round(theta / step) * step


def _mesh_parameterization_report(mesh: MeshApproximation) -> dict:
    return {
        "phaseLevels": mesh.phase_levels,
        "rotationCount": len(mesh.rotations),
        "phaseCount": len(mesh.phase_settings),
        "couplerCount": len(mesh.coupler_settings),
        "phaseSettings": [
            {
                "role": setting.role,
                "target": setting.target,
                "radians": round(setting.radians, 12),
            }
            for setting in mesh.phase_settings
        ],
        "couplerSettings": [
            {
                "rowA": setting.row_a,
                "rowB": setting.row_b,
                "theta": round(setting.theta, 12),
                "throughPower": round(setting.through_power, 12),
                "crossPower": round(setting.cross_power, 12),
            }
            for setting in mesh.coupler_settings
        ],
    }


def _wrap_phase(theta: float) -> float:
    return theta % (2.0 * math.pi)


def _left_apply_givens(matrix: Matrix, row_a: int, row_b: int, theta: float) -> None:
    c = math.cos(theta)
    s = math.sin(theta)
    row_upper = matrix[row_a][:]
    row_lower = matrix[row_b][:]
    for col in range(len(matrix[0])):
        matrix[row_a][col] = c * row_upper[col] + s * row_lower[col]
        matrix[row_b][col] = -s * row_upper[col] + c * row_lower[col]


def _left_apply_givens_transpose(matrix: Matrix, row_a: int, row_b: int, theta: float) -> None:
    c = math.cos(theta)
    s = math.sin(theta)
    row_upper = matrix[row_a][:]
    row_lower = matrix[row_b][:]
    for col in range(len(matrix[0])):
        matrix[row_a][col] = c * row_upper[col] - s * row_lower[col]
        matrix[row_b][col] = s * row_upper[col] + c * row_lower[col]


def _assert_square(matrix: Matrix) -> None:
    if not matrix:
        return
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix must be rectangular")
    if len(matrix) != width:
        raise ValueError("matrix must be square")
