"""Rectangular matrix support for the HRM neural future-work track.

This module extends the abstract simulation path from square toy matrices to
rectangular neural layer shapes. It uses full orthogonal completions around a
rectangular singular-value transfer core. It is still a simulation-only model,
not a foundry layout, measured transfer matrix, or production inference path.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Iterable, List, Sequence

from .mesh_mapping import MeshApproximation, approximate_orthogonal_with_mesh
from .neural_mapping import (
    EPSILON,
    Matrix,
    diagonal_matrix,
    matmul,
    passive_normalize_singular_values,
    relative_frobenius_error,
    scalar_multiply,
    svd_decompose,
)

RECTANGULAR_MODE = "orthogonal_completion_rectangular_sigma"


@dataclass(frozen=True)
class RectangularMeshTransferModel:
    case_id: str
    weight_matrix: Matrix
    target_matrix: Matrix
    ideal_matrix: Matrix
    transfer_matrix: Matrix
    singular_values: List[float]
    passive_singular_values: List[float]
    left_mesh: MeshApproximation
    right_mesh: MeshApproximation
    matrix_rank: int
    effective_rank: int
    padding_applied: bool
    truncation_applied: bool
    ideal_error: float
    mesh_error: float


def deterministic_rectangular_matrices() -> Dict[str, Matrix]:
    return {
        "tall_6x4": [
            [0.42, -0.11, 0.28, 0.07],
            [-0.23, 0.51, 0.16, -0.32],
            [0.35, 0.09, -0.41, 0.22],
            [0.12, -0.37, 0.44, 0.18],
            [-0.31, 0.26, 0.05, 0.49],
            [0.08, 0.33, -0.19, -0.27],
        ],
        "wide_4x6": [
            [0.31, -0.18, 0.42, 0.07, -0.22, 0.15],
            [-0.28, 0.55, 0.11, -0.34, 0.21, 0.09],
            [0.17, 0.24, -0.46, 0.38, 0.06, -0.29],
            [0.44, -0.09, 0.27, 0.13, -0.35, 0.19],
        ],
        "rank_deficient_5x3": [
            [1.00, 2.00, 3.00],
            [0.50, 1.00, 1.50],
            [-1.00, 0.00, -1.00],
            [2.00, -1.00, 1.00],
            [3.00, 1.00, 4.00],
        ],
    }


def build_rectangular_mesh_transfer_model(
    weight_matrix: Matrix,
    case_id: str = "rectangular_matrix",
    phase_levels: int = 64,
    rank_tolerance: float = 1e-10,
) -> RectangularMeshTransferModel:
    rows, cols = _shape(weight_matrix)
    if rows == cols:
        raise ValueError("rectangular model requires m != n")

    svd = svd_decompose(weight_matrix)
    passive_singulars = passive_normalize_singular_values(svd.singular_values)
    max_singular = max(svd.singular_values) if svd.singular_values else 0.0
    target_scale = 0.0 if max_singular <= EPSILON else 1.0 / max_singular
    target = scalar_multiply(weight_matrix, target_scale)

    left_basis = _complete_orthonormal_basis(_matrix_columns(svd.u), rows)
    right_basis_rows = _complete_orthonormal_basis(svd.vh, cols)
    full_u = _columns_to_matrix(left_basis)
    full_vh = [row[:] for row in right_basis_rows]
    sigma = diagonal_matrix(passive_singulars, rows, cols)

    ideal = matmul(matmul(full_u, sigma), full_vh)
    left_mesh = approximate_orthogonal_with_mesh(full_u, phase_levels=phase_levels)
    right_mesh = approximate_orthogonal_with_mesh(full_vh, phase_levels=phase_levels)
    transfer = matmul(matmul(left_mesh.approximation, sigma), right_mesh.approximation)

    matrix_rank = _numerical_rank(svd.singular_values, rank_tolerance)
    return RectangularMeshTransferModel(
        case_id=case_id,
        weight_matrix=weight_matrix,
        target_matrix=target,
        ideal_matrix=ideal,
        transfer_matrix=transfer,
        singular_values=list(svd.singular_values),
        passive_singular_values=passive_singulars,
        left_mesh=left_mesh,
        right_mesh=right_mesh,
        matrix_rank=matrix_rank,
        effective_rank=matrix_rank,
        padding_applied=True,
        truncation_applied=False,
        ideal_error=relative_frobenius_error(target, ideal),
        mesh_error=relative_frobenius_error(target, transfer),
    )


def run_rectangular_matrix_support_report(phase_levels: int = 64) -> dict:
    models = [
        build_rectangular_mesh_transfer_model(matrix, case_id=case_id, phase_levels=phase_levels)
        for case_id, matrix in deterministic_rectangular_matrices().items()
    ]
    cases = [_case_report(model, phase_levels) for model in models]
    worst_case = max(cases, key=lambda row: row["meshConstrainedReconstructionError"])
    max_delta_case = max(cases, key=lambda row: row["errorDelta"])
    return {
        "id": "rectangular-matrix-support",
        "title": "Rectangular matrix support for abstract HRM mesh simulation",
        "stage": 2,
        "evidenceLevel": "abstract_rectangular_mesh_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only rectangular SVD and abstract mesh approximation; no hardware validation, foundry calibration, measured transfer matrix, or production inference readiness is claimed.",
        "rectangularLayerSupportImplemented": True,
        "rectangularMode": RECTANGULAR_MODE,
        "representation": "full_square_left_right_orthogonal_meshes_with_rectangular_sigma_core",
        "phaseLevels": phase_levels,
        "caseCount": len(cases),
        "inputShapes": [case["inputShape"] for case in cases],
        "outputShapes": [case["outputShape"] for case in cases],
        "matrixShapes": [case["matrixShape"] for case in cases],
        "meshConstrainedReconstructionErrorMax": worst_case["meshConstrainedReconstructionError"],
        "errorDeltaMax": max_delta_case["errorDelta"],
        "worstCaseId": worst_case["caseId"],
        "maxErrorDeltaCaseId": max_delta_case["caseId"],
        "cases": cases,
        "limitations": [
            "simulation-only real-valued rectangular transfer representation",
            "rectangular support uses orthogonal completion and zero-padded rectangular sigma core",
            "no complex unitary mesh mode",
            "no Clements or Reck physical interferometer layout",
            "no foundry layout synthesis",
            "no measured transfer matrix",
        ],
        "blockers": [
            "no_complex_unitary_mesh",
            "no_foundry_calibrated_mesh_model",
            "no_measured_transfer_matrix",
        ],
        "nextValidationGates": [
            "complex_unitary_mesh_mode",
            "matrix_family_sweeps",
            "foundry_calibrated_device_model_gate",
        ],
    }


def _case_report(model: RectangularMeshTransferModel, phase_levels: int) -> dict:
    rows, cols = _shape(model.weight_matrix)
    rank_width = min(rows, cols)
    return {
        "caseId": model.case_id,
        "inputShape": [cols],
        "outputShape": [rows],
        "matrixShape": [rows, cols],
        "matrixRank": model.matrix_rank,
        "effectiveRank": model.effective_rank,
        "rankWidth": rank_width,
        "rectangularMode": RECTANGULAR_MODE,
        "paddingApplied": model.padding_applied,
        "leftOrthogonalCompletionApplied": rows > rank_width or model.matrix_rank < rank_width,
        "rightOrthogonalCompletionApplied": cols > rank_width or model.matrix_rank < rank_width,
        "truncationApplied": model.truncation_applied,
        "sigmaShape": [rows, cols],
        "phaseLevels": phase_levels,
        "leftMeshSize": model.left_mesh.size,
        "rightMeshSize": model.right_mesh.size,
        "leftMeshRotationCount": len(model.left_mesh.rotations),
        "rightMeshRotationCount": len(model.right_mesh.rotations),
        "leftMeshPhaseCount": len(model.left_mesh.phase_settings),
        "rightMeshPhaseCount": len(model.right_mesh.phase_settings),
        "leftMeshCouplerCount": len(model.left_mesh.coupler_settings),
        "rightMeshCouplerCount": len(model.right_mesh.coupler_settings),
        "singularValuesPassiveRange": _round_list(model.passive_singular_values),
        "idealReconstructionError": round(model.ideal_error, 15),
        "meshConstrainedReconstructionError": round(model.mesh_error, 15),
        "errorDelta": round(model.mesh_error - model.ideal_error, 15),
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _shape(matrix: Matrix) -> tuple[int, int]:
    if not matrix:
        raise ValueError("matrix must not be empty")
    width = len(matrix[0])
    if width == 0 or any(len(row) != width for row in matrix):
        raise ValueError("matrix must be non-empty and rectangular")
    return len(matrix), width


def _matrix_columns(matrix: Matrix) -> List[List[float]]:
    if not matrix:
        return []
    return [[matrix[row][col] for row in range(len(matrix))] for col in range(len(matrix[0]))]


def _columns_to_matrix(columns: Sequence[Sequence[float]]) -> Matrix:
    if not columns:
        return []
    rows = len(columns[0])
    return [[float(columns[col][row]) for col in range(len(columns))] for row in range(rows)]


def _complete_orthonormal_basis(columns: Sequence[Sequence[float]], size: int) -> List[List[float]]:
    basis: List[List[float]] = []
    for column in columns:
        _append_orthonormal_candidate(basis, column, size)
    for index in range(size):
        candidate = [1.0 if row == index else 0.0 for row in range(size)]
        _append_orthonormal_candidate(basis, candidate, size)
        if len(basis) == size:
            break
    if len(basis) != size:
        raise ValueError("could not complete orthonormal basis")
    return basis


def _append_orthonormal_candidate(
    basis: List[List[float]],
    candidate_values: Sequence[float],
    size: int,
) -> None:
    if len(candidate_values) != size:
        raise ValueError("basis vector has wrong dimension")
    candidate = [float(value) for value in candidate_values]
    for existing in basis:
        dot = sum(a * b for a, b in zip(candidate, existing))
        candidate = [a - dot * b for a, b in zip(candidate, existing)]
    norm = math.sqrt(sum(value * value for value in candidate))
    if norm > EPSILON:
        basis.append([value / norm for value in candidate])


def _numerical_rank(singular_values: Sequence[float], tolerance: float) -> int:
    if not singular_values:
        return 0
    scale = max(abs(value) for value in singular_values)
    threshold = max(tolerance, tolerance * scale)
    return sum(1 for value in singular_values if abs(value) > threshold)


def _round_list(values: Iterable[float], digits: int = 12) -> List[float]:
    return [round(float(value), digits) for value in values]
