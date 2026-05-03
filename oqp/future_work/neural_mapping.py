"""Numerical SVD mapping for the HRM neural future-work track.

The functions in this module are deliberately small and deterministic. They
model only numerical linear algebra needed for future-work reports; they do not
claim hardware-native inference or hardware validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, List, Sequence

Matrix = List[List[float]]
EPSILON = 1e-12


@dataclass(frozen=True)
class SVDResult:
    u: Matrix
    singular_values: List[float]
    vh: Matrix


def deterministic_weight_matrix() -> Matrix:
    """Return a stable small matrix used by reports and tests."""

    return [
        [0.42, -0.25, 0.31],
        [0.10, 0.56, -0.44],
        [-0.35, 0.18, 0.62],
    ]


def zero_matrix(rows: int, cols: int) -> Matrix:
    return [[0.0 for _ in range(cols)] for _ in range(rows)]


def identity_matrix(size: int) -> Matrix:
    return [[1.0 if row == col else 0.0 for col in range(size)] for row in range(size)]


def transpose(matrix: Matrix) -> Matrix:
    _assert_rectangular(matrix)
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    _assert_rectangular(left)
    _assert_rectangular(right)
    if not left or not right:
        return []
    if len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not align")
    right_t = transpose(right)
    return [[sum(a * b for a, b in zip(row, col)) for col in right_t] for row in left]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    _assert_same_shape(left, right)
    return [[a - b for a, b in zip(row_left, row_right)] for row_left, row_right in zip(left, right)]


def scalar_multiply(matrix: Matrix, scalar: float) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def diagonal_matrix(values: Sequence[float], rows: int | None = None, cols: int | None = None) -> Matrix:
    row_count = rows if rows is not None else len(values)
    col_count = cols if cols is not None else len(values)
    matrix = zero_matrix(row_count, col_count)
    for index, value in enumerate(values[: min(row_count, col_count)]):
        matrix[index][index] = float(value)
    return matrix


def frobenius_norm(matrix: Matrix) -> float:
    return math.sqrt(sum(value * value for row in matrix for value in row))


def relative_frobenius_error(target: Matrix, candidate: Matrix) -> float:
    _assert_same_shape(target, candidate)
    denominator = frobenius_norm(target)
    numerator = frobenius_norm(subtract(target, candidate))
    if denominator <= EPSILON:
        return 0.0 if numerator <= EPSILON else math.inf
    return numerator / denominator


def passive_normalize_singular_values(singular_values: Sequence[float]) -> List[float]:
    if not singular_values:
        return []
    max_value = max(abs(value) for value in singular_values)
    if max_value <= EPSILON:
        return [0.0 for _ in singular_values]
    return [max(0.0, min(1.0, abs(value) / max_value)) for value in singular_values]


def svd_decompose(matrix: Matrix) -> SVDResult:
    """Compute a compact SVD using a Jacobi eigensolver for A^T A.

    This is intentionally scoped to small deterministic matrices used by the
    future-work validation reports. It avoids third-party dependencies so the
    evidence pipeline can run in the base Python environment.
    """

    _assert_rectangular(matrix)
    if not matrix or not matrix[0]:
        return SVDResult([], [], [])

    rows = len(matrix)
    cols = len(matrix[0])
    rank_width = min(rows, cols)
    gram = matmul(transpose(matrix), matrix)
    eigenvalues, eigenvectors = _jacobi_eigen_symmetric(gram)
    order = sorted(range(len(eigenvalues)), key=lambda index: eigenvalues[index], reverse=True)

    singular_values: List[float] = []
    v_columns: List[List[float]] = []
    u_columns: List[List[float]] = []
    for output_index, eigen_index in enumerate(order[:rank_width]):
        singular = math.sqrt(max(eigenvalues[eigen_index], 0.0))
        singular_values.append(singular)
        v_col = [eigenvectors[row][eigen_index] for row in range(cols)]
        v_columns.append(v_col)
        if singular > EPSILON:
            av = _matrix_vector_multiply(matrix, v_col)
            u_columns.append([value / singular for value in av])
        else:
            u_columns.append(_orthogonal_completion_column(rows, u_columns, output_index))

    u = _columns_to_matrix(u_columns, rows)
    vh = [list(col) for col in v_columns]
    return SVDResult(u, singular_values, vh)


def reconstruct_from_svd(result: SVDResult, singular_values: Sequence[float] | None = None) -> Matrix:
    if not result.u or not result.vh:
        return []
    values = list(singular_values) if singular_values is not None else result.singular_values
    sigma = diagonal_matrix(values, len(values), len(values))
    return matmul(matmul(result.u, sigma), result.vh)


def run_svd_mapping_demo() -> dict:
    weight_matrix = deterministic_weight_matrix()
    svd = svd_decompose(weight_matrix)
    reconstruction = reconstruct_from_svd(svd)
    normalized = passive_normalize_singular_values(svd.singular_values)
    passive_target = scalar_multiply(weight_matrix, 1.0 / max(svd.singular_values))
    passive_reconstruction = reconstruct_from_svd(svd, normalized)
    return {
        "id": "stage-1-svd-demo",
        "title": "Numerical SVD mapping demo",
        "stage": 1,
        "evidenceLevel": "numerical_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Numerical SVD demonstration only; no phase/coupler synthesis, active gain, hardware validation, or production inference readiness is claimed.",
        "activeGainImplemented": False,
        "phaseSynthesisImplemented": False,
        "weightMatrix": _round_matrix(weight_matrix),
        "singularValues": _round_list(svd.singular_values),
        "passiveNormalizedSingularValues": _round_list(normalized),
        "relativeFrobeniusReconstructionError": round(relative_frobenius_error(weight_matrix, reconstruction), 15),
        "passiveRelativeFrobeniusReconstructionError": round(relative_frobenius_error(passive_target, passive_reconstruction), 15),
        "matrixScaleRepresentedOutsidePassiveOpticalCore": max(svd.singular_values),
        "blockers": [],
        "nextValidationGates": [
            "abstract_mesh_constrained_mapping",
            "phase_quantization_and_drift_model",
            "synthetic_transfer_matrix_calibration",
        ],
    }


def _jacobi_eigen_symmetric(matrix: Matrix, max_iterations: int = 200, tolerance: float = 1e-14) -> tuple[List[float], Matrix]:
    _assert_square(matrix)
    size = len(matrix)
    working = [row[:] for row in matrix]
    vectors = identity_matrix(size)
    if size == 0:
        return [], []

    for _ in range(max_iterations):
        p, q, max_offdiag = _max_offdiagonal(working)
        if max_offdiag < tolerance:
            break
        app = working[p][p]
        aqq = working[q][q]
        apq = working[p][q]
        angle = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c = math.cos(angle)
        s = math.sin(angle)

        for row in range(size):
            if row != p and row != q:
                arp = working[row][p]
                arq = working[row][q]
                working[row][p] = c * arp - s * arq
                working[p][row] = working[row][p]
                working[row][q] = s * arp + c * arq
                working[q][row] = working[row][q]

        working[p][p] = c * c * app - 2.0 * s * c * apq + s * s * aqq
        working[q][q] = s * s * app + 2.0 * s * c * apq + c * c * aqq
        working[p][q] = 0.0
        working[q][p] = 0.0

        for row in range(size):
            vrp = vectors[row][p]
            vrq = vectors[row][q]
            vectors[row][p] = c * vrp - s * vrq
            vectors[row][q] = s * vrp + c * vrq

    return [working[index][index] for index in range(size)], vectors


def _max_offdiagonal(matrix: Matrix) -> tuple[int, int, float]:
    size = len(matrix)
    p, q = 0, 1 if size > 1 else 0
    max_value = 0.0
    for row in range(size):
        for col in range(row + 1, size):
            value = abs(matrix[row][col])
            if value > max_value:
                p, q, max_value = row, col, value
    return p, q, max_value


def _matrix_vector_multiply(matrix: Matrix, vector: Sequence[float]) -> List[float]:
    return [sum(value * vector[index] for index, value in enumerate(row)) for row in matrix]


def _orthogonal_completion_column(size: int, existing_columns: Sequence[Sequence[float]], preferred_index: int) -> List[float]:
    for offset in range(size):
        basis_index = (preferred_index + offset) % size
        candidate = [1.0 if row == basis_index else 0.0 for row in range(size)]
        for existing in existing_columns:
            dot = sum(a * b for a, b in zip(candidate, existing))
            candidate = [a - dot * b for a, b in zip(candidate, existing)]
        norm = math.sqrt(sum(value * value for value in candidate))
        if norm > EPSILON:
            return [value / norm for value in candidate]
    return [0.0 for _ in range(size)]


def _columns_to_matrix(columns: Sequence[Sequence[float]], rows: int) -> Matrix:
    return [[columns[col][row] for col in range(len(columns))] for row in range(rows)]


def _round_list(values: Iterable[float], digits: int = 12) -> List[float]:
    return [round(float(value), digits) for value in values]


def _round_matrix(matrix: Matrix, digits: int = 12) -> Matrix:
    return [_round_list(row, digits) for row in matrix]


def _assert_rectangular(matrix: Matrix) -> None:
    if not matrix:
        return
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix must be rectangular")


def _assert_square(matrix: Matrix) -> None:
    _assert_rectangular(matrix)
    if len(matrix) != (len(matrix[0]) if matrix else 0):
        raise ValueError("matrix must be square")


def _assert_same_shape(left: Matrix, right: Matrix) -> None:
    _assert_rectangular(left)
    _assert_rectangular(right)
    if len(left) != len(right) or (left and right and len(left[0]) != len(right[0])):
        raise ValueError("matrix shapes do not match")
