"""Complex/unitary mesh simulation support for HRM neural future work.

This module adds a deterministic complex-valued simulation layer. It models
unitary-factor handling with a complex QR factorization and a phase-quantized
abstract unitary factor. It is not a physical phase-synthesis implementation,
not a foundry layout, and not measured hardware validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
from typing import Dict, Iterable, List, Sequence

EPSILON = 1e-12
ComplexMatrix = List[List[complex]]


@dataclass(frozen=True)
class ComplexUnitaryModel:
    case_id: str
    target_matrix: ComplexMatrix
    unitary_factor: ComplexMatrix
    residual_factor: ComplexMatrix
    approximated_unitary_factor: ComplexMatrix
    ideal_reconstruction: ComplexMatrix
    approximated_reconstruction: ComplexMatrix
    ideal_error: float
    mesh_error: float
    phase_error: float
    amplitude_error: float
    exact_unitarity_deviation: float
    approximated_unitarity_deviation: float


def deterministic_complex_matrices() -> Dict[str, ComplexMatrix]:
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    return {
        "unitary_like_2x2": [
            [inv_sqrt2 + 0.0j, 0.0 + inv_sqrt2 * 1j],
            [0.0 + inv_sqrt2 * 1j, inv_sqrt2 + 0.0j],
        ],
        "complex_4x4": [
            [0.42 + 0.10j, -0.18 + 0.22j, 0.31 - 0.14j, 0.08 + 0.05j],
            [0.12 - 0.33j, 0.55 + 0.00j, -0.21 + 0.19j, 0.27 - 0.08j],
            [-0.36 + 0.04j, 0.16 + 0.28j, 0.47 - 0.11j, -0.13 + 0.24j],
            [0.05 + 0.30j, -0.29 - 0.12j, 0.18 + 0.07j, 0.39 + 0.16j],
        ],
        "phase_dominant_4x4": [
            [_polar(0.62, 0.10), _polar(0.18, 1.30), _polar(0.12, -2.20), _polar(0.08, 2.70)],
            [_polar(0.10, -1.10), _polar(0.58, 1.85), _polar(0.16, 0.40), _polar(0.09, -2.40)],
            [_polar(0.07, 2.20), _polar(0.15, -0.75), _polar(0.60, -1.45), _polar(0.17, 1.10)],
            [_polar(0.13, -2.65), _polar(0.06, 2.95), _polar(0.14, -0.20), _polar(0.57, 2.35)],
        ],
    }


def build_complex_unitary_model(
    matrix: ComplexMatrix,
    case_id: str = "complex_unitary_matrix",
    phase_levels: int = 64,
) -> ComplexUnitaryModel:
    if phase_levels < 2:
        raise ValueError("phase_levels must be at least 2")
    _shape(matrix)
    unitary, residual = complex_qr_factorization(matrix)
    ideal = complex_matmul(unitary, residual)
    approximated_unitary = quantize_unitary_factor(unitary, phase_levels=phase_levels)
    approximated = complex_matmul(approximated_unitary, residual)
    return ComplexUnitaryModel(
        case_id=case_id,
        target_matrix=matrix,
        unitary_factor=unitary,
        residual_factor=residual,
        approximated_unitary_factor=approximated_unitary,
        ideal_reconstruction=ideal,
        approximated_reconstruction=approximated,
        ideal_error=relative_complex_frobenius_error(matrix, ideal),
        mesh_error=relative_complex_frobenius_error(matrix, approximated),
        phase_error=phase_aware_error(matrix, approximated),
        amplitude_error=amplitude_relative_error(matrix, approximated),
        exact_unitarity_deviation=unitarity_deviation(unitary),
        approximated_unitarity_deviation=unitarity_deviation(approximated_unitary),
    )


def run_complex_unitary_mesh_support_report(phase_levels: int = 64) -> dict:
    models = [
        build_complex_unitary_model(matrix, case_id=case_id, phase_levels=phase_levels)
        for case_id, matrix in deterministic_complex_matrices().items()
    ]
    cases = [_case_report(model, phase_levels) for model in models]
    worst_case = max(cases, key=lambda row: row["meshConstrainedReconstructionError"])
    phase_worst_case = max(cases, key=lambda row: row["phaseAwareError"])
    amplitude_worst_case = max(cases, key=lambda row: row["amplitudeError"])
    return {
        "id": "complex-unitary-mesh-support",
        "title": "Complex/unitary mesh support for abstract HRM simulation",
        "stage": 2,
        "evidenceLevel": "abstract_complex_unitary_mesh_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only complex/unitary factor handling; no hardware validation, foundry calibration, measured transfer matrix, physical phase synthesis, or production inference readiness is claimed.",
        "complexValuedSupportImplemented": True,
        "unitaryFactorSupportImplemented": True,
        "complexSvdImplemented": False,
        "unitaryFactorization": "complex_qr_unitary_factor",
        "abstractPhaseQuantizationImplemented": True,
        "physicalPhaseSynthesisImplemented": False,
        "physicalCouplerSynthesisImplemented": False,
        "foundryLayoutSynthesisImplemented": False,
        "complexValueEncoding": "reported_complex_samples_use_real_imag_pairs",
        "phaseLevels": phase_levels,
        "caseCount": len(cases),
        "matrixShapes": [case["matrixShape"] for case in cases],
        "meshConstrainedReconstructionErrorMax": worst_case["meshConstrainedReconstructionError"],
        "phaseAwareErrorMax": phase_worst_case["phaseAwareError"],
        "amplitudeErrorMax": amplitude_worst_case["amplitudeError"],
        "worstCaseId": worst_case["caseId"],
        "phaseWorstCaseId": phase_worst_case["caseId"],
        "amplitudeWorstCaseId": amplitude_worst_case["caseId"],
        "cases": cases,
        "limitations": [
            "simulation-only complex-valued unitary-factor handling",
            "complex QR factorization, not a full complex SVD pipeline",
            "phase quantization is abstract and not a physical phase-shifter synthesis model",
            "no Clements or Reck physical interferometer layout",
            "no foundry layout synthesis",
            "no measured transfer matrix",
        ],
        "blockers": [
            "no_complex_svd_pipeline",
            "no_physical_phase_synthesis",
            "no_foundry_calibrated_mesh_model",
            "no_measured_transfer_matrix",
        ],
        "nextValidationGates": [
            "complex_svd_pipeline",
            "complex_rectangular_matrix_family_sweeps",
            "foundry_calibrated_device_model_gate",
        ],
    }


def complex_qr_factorization(matrix: ComplexMatrix) -> tuple[ComplexMatrix, ComplexMatrix]:
    rows, cols = _shape(matrix)
    if rows != cols:
        raise ValueError("complex unitary support currently requires square matrices")
    columns = _matrix_columns(matrix)
    q_columns: List[List[complex]] = []
    residual = [[0.0 + 0.0j for _ in range(cols)] for _ in range(cols)]
    for col_index, column in enumerate(columns):
        vector = list(column)
        for q_index, q_column in enumerate(q_columns):
            coefficient = _inner_product(q_column, vector)
            residual[q_index][col_index] = coefficient
            vector = [value - coefficient * basis_value for value, basis_value in zip(vector, q_column)]
        norm = _vector_norm(vector)
        if norm <= EPSILON:
            vector = _orthogonal_completion_vector(rows, q_columns, col_index)
            norm = _vector_norm(vector)
        residual[col_index][col_index] = norm + 0.0j
        q_columns.append([value / norm for value in vector])
    return _columns_to_matrix(q_columns), residual


def quantize_unitary_factor(matrix: ComplexMatrix, phase_levels: int = 64) -> ComplexMatrix:
    columns = _matrix_columns(matrix)
    quantized_columns = [
        [_quantize_complex_phase(value, phase_levels) for value in column]
        for column in columns
    ]
    orthonormal = _complete_complex_orthonormal_basis(quantized_columns, len(matrix))
    return _columns_to_matrix(orthonormal)


def relative_complex_frobenius_error(target: ComplexMatrix, candidate: ComplexMatrix) -> float:
    _assert_same_shape(target, candidate)
    denominator = complex_frobenius_norm(target)
    numerator = complex_frobenius_norm(_complex_subtract(target, candidate))
    if denominator <= EPSILON:
        return 0.0 if numerator <= EPSILON else math.inf
    return numerator / denominator


def phase_aware_error(target: ComplexMatrix, candidate: ComplexMatrix) -> float:
    _assert_same_shape(target, candidate)
    weighted_sum = 0.0
    weight_total = 0.0
    for target_row, candidate_row in zip(target, candidate):
        for target_value, candidate_value in zip(target_row, candidate_row):
            weight = abs(target_value)
            if weight <= EPSILON or abs(candidate_value) <= EPSILON:
                continue
            delta = _wrap_angle(cmath.phase(candidate_value) - cmath.phase(target_value))
            weighted_sum += weight * delta * delta
            weight_total += weight
    if weight_total <= EPSILON:
        return 0.0
    return math.sqrt(weighted_sum / weight_total)


def amplitude_relative_error(target: ComplexMatrix, candidate: ComplexMatrix) -> float:
    _assert_same_shape(target, candidate)
    denominator = math.sqrt(sum(abs(value) ** 2 for row in target for value in row))
    numerator = math.sqrt(
        sum(
            (abs(target_value) - abs(candidate_value)) ** 2
            for target_row, candidate_row in zip(target, candidate)
            for target_value, candidate_value in zip(target_row, candidate_row)
        )
    )
    if denominator <= EPSILON:
        return 0.0 if numerator <= EPSILON else math.inf
    return numerator / denominator


def unitarity_deviation(matrix: ComplexMatrix) -> float:
    rows, cols = _shape(matrix)
    if rows != cols:
        raise ValueError("unitarity deviation requires a square matrix")
    identity = _complex_identity(rows)
    gram = complex_matmul(conjugate_transpose(matrix), matrix)
    return relative_complex_frobenius_error(identity, gram)


def complex_matmul(left: ComplexMatrix, right: ComplexMatrix) -> ComplexMatrix:
    left_rows, left_cols = _shape(left)
    right_rows, right_cols = _shape(right)
    if left_cols != right_rows:
        raise ValueError("matrix dimensions do not align")
    right_t = _matrix_columns(right)
    return [
        [sum(left[row][index] * right_t[col][index] for index in range(left_cols)) for col in range(right_cols)]
        for row in range(left_rows)
    ]


def conjugate_transpose(matrix: ComplexMatrix) -> ComplexMatrix:
    _shape(matrix)
    return [[value.conjugate() for value in column] for column in _matrix_columns(matrix)]


def complex_frobenius_norm(matrix: ComplexMatrix) -> float:
    return math.sqrt(sum(abs(value) ** 2 for row in matrix for value in row))


def _case_report(model: ComplexUnitaryModel, phase_levels: int) -> dict:
    rows, cols = _shape(model.target_matrix)
    return {
        "caseId": model.case_id,
        "matrixShape": [rows, cols],
        "phaseLevels": phase_levels,
        "unitaryFactorShape": [len(model.unitary_factor), len(model.unitary_factor[0])],
        "residualFactorShape": [len(model.residual_factor), len(model.residual_factor[0])],
        "reconstructionMode": "complex_qr_unitary_factor_times_residual",
        "complexValuedSupportImplemented": True,
        "unitaryFactorSupportImplemented": True,
        "physicalPhaseSynthesisImplemented": False,
        "physicalCouplerSynthesisImplemented": False,
        "foundryLayoutSynthesisImplemented": False,
        "unitaryLikeInput": model.case_id == "unitary_like_2x2",
        "phaseDominantInput": model.case_id == "phase_dominant_4x4",
        "idealReconstructionError": round(model.ideal_error, 15),
        "meshConstrainedReconstructionError": round(model.mesh_error, 15),
        "errorDelta": round(model.mesh_error - model.ideal_error, 15),
        "phaseAwareError": round(model.phase_error, 15),
        "amplitudeError": round(model.amplitude_error, 15),
        "exactUnitaryFactorDeviation": round(model.exact_unitarity_deviation, 15),
        "approximatedUnitaryFactorDeviation": round(model.approximated_unitarity_deviation, 15),
        "targetMatrixSample": _encode_complex_matrix(model.target_matrix[:2], max_cols=2),
        "approximatedMatrixSample": _encode_complex_matrix(model.approximated_reconstruction[:2], max_cols=2),
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _encode_complex_matrix(matrix: ComplexMatrix, max_cols: int) -> List[List[dict]]:
    return [
        [
            {"real": round(value.real, 12), "imag": round(value.imag, 12)}
            for value in row[:max_cols]
        ]
        for row in matrix
    ]


def _shape(matrix: ComplexMatrix) -> tuple[int, int]:
    if not matrix:
        raise ValueError("matrix must not be empty")
    width = len(matrix[0])
    if width == 0 or any(len(row) != width for row in matrix):
        raise ValueError("matrix must be non-empty and rectangular")
    return len(matrix), width


def _assert_same_shape(left: ComplexMatrix, right: ComplexMatrix) -> None:
    if _shape(left) != _shape(right):
        raise ValueError("matrix shapes do not match")


def _matrix_columns(matrix: ComplexMatrix) -> List[List[complex]]:
    rows, cols = _shape(matrix)
    return [[matrix[row][col] for row in range(rows)] for col in range(cols)]


def _columns_to_matrix(columns: Sequence[Sequence[complex]]) -> ComplexMatrix:
    if not columns:
        return []
    rows = len(columns[0])
    return [[complex(columns[col][row]) for col in range(len(columns))] for row in range(rows)]


def _complete_complex_orthonormal_basis(columns: Sequence[Sequence[complex]], size: int) -> List[List[complex]]:
    basis: List[List[complex]] = []
    for column in columns:
        _append_orthonormal_candidate(basis, column, size)
    for index in range(size):
        candidate = [1.0 + 0.0j if row == index else 0.0 + 0.0j for row in range(size)]
        _append_orthonormal_candidate(basis, candidate, size)
        if len(basis) == size:
            break
    if len(basis) != size:
        raise ValueError("could not complete complex orthonormal basis")
    return basis


def _append_orthonormal_candidate(
    basis: List[List[complex]],
    candidate_values: Sequence[complex],
    size: int,
) -> None:
    if len(candidate_values) != size:
        raise ValueError("basis vector has wrong dimension")
    candidate = [complex(value) for value in candidate_values]
    for existing in basis:
        coefficient = _inner_product(existing, candidate)
        candidate = [value - coefficient * basis_value for value, basis_value in zip(candidate, existing)]
    norm = _vector_norm(candidate)
    if norm > EPSILON:
        basis.append([value / norm for value in candidate])


def _orthogonal_completion_vector(size: int, existing_columns: Sequence[Sequence[complex]], preferred_index: int) -> List[complex]:
    for offset in range(size):
        basis_index = (preferred_index + offset) % size
        candidate = [1.0 + 0.0j if row == basis_index else 0.0 + 0.0j for row in range(size)]
        working = [complex(value) for value in candidate]
        for existing in existing_columns:
            coefficient = _inner_product(existing, working)
            working = [value - coefficient * basis_value for value, basis_value in zip(working, existing)]
        if _vector_norm(working) > EPSILON:
            return working
    raise ValueError("could not create orthogonal completion vector")


def _inner_product(left: Sequence[complex], right: Sequence[complex]) -> complex:
    return sum(left_value.conjugate() * right_value for left_value, right_value in zip(left, right))


def _vector_norm(values: Sequence[complex]) -> float:
    return math.sqrt(sum(abs(value) ** 2 for value in values))


def _quantize_complex_phase(value: complex, phase_levels: int) -> complex:
    magnitude = abs(value)
    if magnitude <= EPSILON:
        return 0.0 + 0.0j
    step = (2.0 * math.pi) / (phase_levels - 1)
    phase = round(cmath.phase(value) / step) * step
    return _polar(magnitude, phase)


def _complex_subtract(left: ComplexMatrix, right: ComplexMatrix) -> ComplexMatrix:
    return [
        [left_value - right_value for left_value, right_value in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def _complex_identity(size: int) -> ComplexMatrix:
    return [[1.0 + 0.0j if row == col else 0.0 + 0.0j for col in range(size)] for row in range(size)]


def _polar(magnitude: float, phase: float) -> complex:
    return magnitude * complex(math.cos(phase), math.sin(phase))


def _wrap_angle(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def _round_list(values: Iterable[float], digits: int = 12) -> List[float]:
    return [round(float(value), digits) for value in values]
