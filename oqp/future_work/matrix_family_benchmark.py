"""Deterministic matrix-family benchmarks for HRM neural future work.

This module compares the existing square, rectangular, and complex/unitary
simulation paths across a fixed set of matrix families. It is an abstract
simulation benchmark only; it does not add hardware evidence or unblock any
hardware-facing gate.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List

from .complex_unitary_mapping import (
    ComplexMatrix,
    build_complex_unitary_model,
    deterministic_complex_matrices,
)
from .mesh_mapping import build_mesh_transfer_model
from .neural_mapping import Matrix, svd_decompose
from .rectangular_mapping import build_rectangular_mesh_transfer_model


EVIDENCE_LEVEL = "abstract_matrix_family_benchmark_simulation"
ANALYSIS_EVIDENCE_LEVEL = "abstract_matrix_family_analysis"


@dataclass(frozen=True)
class MatrixFamilyCase:
    case_id: str
    matrix_family: str
    real_or_complex: str
    matrix: Matrix | ComplexMatrix
    limitations: List[str]


def deterministic_matrix_family_cases() -> List[MatrixFamilyCase]:
    complex_cases = deterministic_complex_matrices()
    return [
        MatrixFamilyCase(
            case_id="identity_4x4",
            matrix_family="identity",
            real_or_complex="real",
            matrix=_identity(4),
            limitations=["identity control case; not representative of trained dense neural weights"],
        ),
        MatrixFamilyCase(
            case_id="diagonal_dynamic_range_4x4",
            matrix_family="diagonal_dynamic_range",
            real_or_complex="real",
            matrix=[
                [1.00, 0.00, 0.00, 0.00],
                [0.00, 0.50, 0.00, 0.00],
                [0.00, 0.00, 0.10, 0.00],
                [0.00, 0.00, 0.00, 0.02],
            ],
            limitations=["diagonal dynamic-range case; ignores dense mixing structure"],
        ),
        MatrixFamilyCase(
            case_id="low_rank_6x4",
            matrix_family="low_rank",
            real_or_complex="real",
            matrix=[
                [0.5000, -0.0500, 0.2200, -0.1800],
                [0.6500, -0.2750, 0.7200, -0.4300],
                [-0.2000, 0.2000, -0.4600, 0.2400],
                [-1.1000, 0.0500, -0.3600, 0.3400],
                [0.2500, -0.0250, 0.1100, -0.0900],
                [0.3250, -0.1375, 0.3600, -0.2150],
            ],
            limitations=["rank-deficient rectangular case; condition number is undefined"],
        ),
        MatrixFamilyCase(
            case_id="rank_deficient_5x3",
            matrix_family="rank_deficient",
            real_or_complex="real",
            matrix=[
                [1.00, 2.00, 3.00],
                [0.50, 1.00, 1.50],
                [-1.00, 0.00, -1.00],
                [2.00, -1.00, 1.00],
                [3.00, 1.00, 4.00],
            ],
            limitations=["rank-deficient rectangular case; condition number is undefined"],
        ),
        MatrixFamilyCase(
            case_id="ill_conditioned_4x4",
            matrix_family="ill_conditioned",
            real_or_complex="real",
            matrix=[
                [1.000, 0.015, -0.010, 0.005],
                [0.000, 0.100, 0.012, -0.006],
                [0.000, 0.000, 0.010, 0.003],
                [0.000, 0.000, 0.000, 0.001],
            ],
            limitations=["small deterministic ill-conditioned matrix; no training distribution is represented"],
        ),
        MatrixFamilyCase(
            case_id="sparse_like_6x6",
            matrix_family="sparse_like",
            real_or_complex="real",
            matrix=[
                [0.70, 0.00, -0.20, 0.00, 0.00, 0.10],
                [0.00, -0.55, 0.00, 0.25, 0.00, 0.00],
                [0.18, 0.00, 0.62, 0.00, -0.16, 0.00],
                [0.00, 0.21, 0.00, -0.48, 0.00, 0.12],
                [-0.09, 0.00, 0.14, 0.00, 0.58, 0.00],
                [0.00, 0.08, 0.00, -0.11, 0.00, 0.44],
            ],
            limitations=["sparse-like hand-authored case; no sparse hardware routing model is included"],
        ),
        MatrixFamilyCase(
            case_id="dense_seeded_4x4",
            matrix_family="dense_seeded",
            real_or_complex="real",
            matrix=[
                [0.31, -0.42, 0.18, 0.27],
                [-0.15, 0.53, -0.34, 0.11],
                [0.46, 0.07, -0.29, -0.38],
                [0.22, -0.17, 0.41, 0.09],
            ],
            limitations=["single deterministic dense case; not a statistical model benchmark"],
        ),
        MatrixFamilyCase(
            case_id="rectangular_tall_8x4",
            matrix_family="rectangular_tall",
            real_or_complex="real",
            matrix=[
                [0.22, -0.31, 0.14, 0.07],
                [-0.18, 0.49, 0.25, -0.36],
                [0.41, 0.05, -0.33, 0.19],
                [0.09, -0.27, 0.52, 0.13],
                [-0.35, 0.21, 0.08, 0.44],
                [0.16, 0.38, -0.23, -0.29],
                [0.28, -0.12, 0.37, -0.18],
                [-0.24, 0.32, 0.11, 0.26],
            ],
            limitations=["rectangular tall simulation; no physical rectangular mesh layout is defined"],
        ),
        MatrixFamilyCase(
            case_id="rectangular_wide_4x8",
            matrix_family="rectangular_wide",
            real_or_complex="real",
            matrix=[
                [0.17, -0.24, 0.36, 0.05, -0.19, 0.31, 0.08, -0.12],
                [-0.28, 0.47, 0.09, -0.33, 0.18, 0.06, -0.22, 0.27],
                [0.39, 0.12, -0.44, 0.25, 0.04, -0.35, 0.16, 0.21],
                [0.11, -0.08, 0.29, 0.14, -0.41, 0.23, -0.17, 0.34],
            ],
            limitations=["rectangular wide simulation; no physical fan-out or readout model is included"],
        ),
        MatrixFamilyCase(
            case_id="complex_phase_dominant_4x4",
            matrix_family="complex_phase_dominant",
            real_or_complex="complex",
            matrix=complex_cases["phase_dominant_4x4"],
            limitations=["complex QR unitary-factor handling only; no full complex SVD pipeline"],
        ),
        MatrixFamilyCase(
            case_id="unitary_like_4x4",
            matrix_family="unitary_like",
            real_or_complex="complex",
            matrix=_fourier_unitary_4x4(),
            limitations=["unitary-like deterministic control; no physical interferometer layout is generated"],
        ),
    ]


def run_matrix_family_benchmark_report(phase_levels: int = 64) -> dict:
    rows = [_case_report(case, phase_levels) for case in deterministic_matrix_family_cases()]
    worst_case = max(rows, key=lambda row: row["meshConstrainedReconstructionError"])
    max_delta_case = max(rows, key=lambda row: row["errorDelta"])
    return {
        "id": "matrix-family-benchmark",
        "title": "Matrix-family benchmark for abstract HRM mapping simulation",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only matrix-family benchmark; no hardware validation, foundry calibration, measured transfer matrix, or production inference readiness is claimed.",
        "phaseLevels": phase_levels,
        "caseCount": len(rows),
        "matrixFamilies": [row["matrixFamily"] for row in rows],
        "matrixShapes": [row["shape"] for row in rows],
        "realCaseCount": sum(1 for row in rows if row["realOrComplex"] == "real"),
        "complexCaseCount": sum(1 for row in rows if row["realOrComplex"] == "complex"),
        "meshConstrainedReconstructionErrorMax": worst_case["meshConstrainedReconstructionError"],
        "errorDeltaMax": max_delta_case["errorDelta"],
        "worstCaseId": worst_case["caseId"],
        "maxErrorDeltaCaseId": max_delta_case["caseId"],
        "cases": rows,
        "limitations": [
            "simulation-only benchmark over small deterministic matrix families",
            "real square cases use the abstract real-valued mesh approximation",
            "rectangular cases use orthogonal completion and rectangular sigma cores",
            "complex cases use complex QR unitary-factor handling, not a full complex SVD pipeline",
            "no physical Clements/Reck layout",
            "no foundry layout synthesis",
            "no measured transfer matrix",
        ],
        "blockers": [
            "no_large_model_weight_distribution",
            "no_physical_mesh_layout",
            "no_foundry_calibrated_mesh_model",
            "no_measured_transfer_matrix",
        ],
        "nextValidationGates": [
            "multi_layer_toy_inference_pipeline",
            "model_weight_manifest_import",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_matrix_family_analysis_report(phase_levels: int = 64) -> dict:
    benchmark = run_matrix_family_benchmark_report(phase_levels=phase_levels)
    rows = benchmark["cases"]
    best_case = min(rows, key=lambda row: row["meshConstrainedReconstructionError"])
    worst_case = max(rows, key=lambda row: row["meshConstrainedReconstructionError"])
    max_delta_case = max(rows, key=lambda row: row["errorDelta"])
    average_error = sum(row["meshConstrainedReconstructionError"] for row in rows) / len(rows)
    return {
        "id": "matrix-family-analysis",
        "title": "Matrix-family benchmark analysis",
        "stage": 2,
        "evidenceLevel": ANALYSIS_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only matrix-family analysis; no hardware validation, foundry calibration, measured transfer matrix, or production inference readiness is claimed.",
        "benchmarkReport": "matrix-family-benchmark.json",
        "caseCount": len(rows),
        "bestCase": _case_summary(best_case),
        "worstCase": _case_summary(worst_case),
        "maxErrorDelta": max_delta_case["errorDelta"],
        "maxErrorDeltaCase": _case_summary(max_delta_case),
        "averageMeshConstrainedError": round(average_error, 15),
        "familyRankingByError": [
            _case_summary(row)
            for row in sorted(rows, key=lambda item: item["meshConstrainedReconstructionError"], reverse=True)
        ],
        "familyRankingByConditionSensitivity": _condition_ranking(rows),
        "hardestFamilyNotes": [
            f"{worst_case['caseId']} has the largest mesh-constrained reconstruction error in this deterministic suite.",
            f"{max_delta_case['caseId']} has the largest error delta relative to its ideal reconstruction.",
            "Rank-deficient and complex cases are interpreted only within their current abstract simulation paths.",
        ],
        "monotonicityNotes": [
            "No monotonicity is expected across unrelated matrix families.",
            "Condition number is reported only when the real-valued compact SVD provides a full-rank spectrum.",
            "Complex/unitary cases are ranked by error but excluded from condition-number sensitivity ranking.",
        ],
        "limitations": [
            "small deterministic matrix families only",
            "no sampled training distribution",
            "no large model layer statistics",
            "complex cases use complex QR unitary-factor handling, not full complex SVD",
            "no physical layout, foundry calibration, measured transfer matrix, timing, or energy evidence",
        ],
        "blockers": benchmark["blockers"],
        "nextValidationGates": benchmark["nextValidationGates"],
    }


def _case_report(case: MatrixFamilyCase, phase_levels: int) -> dict:
    if case.real_or_complex == "complex":
        return _complex_case_report(case, phase_levels)
    return _real_case_report(case, phase_levels)


def _real_case_report(case: MatrixFamilyCase, phase_levels: int) -> dict:
    matrix = case.matrix  # type: ignore[assignment]
    rows, cols = _real_shape(matrix)
    if rows == cols:
        model = build_mesh_transfer_model(matrix, phase_levels=phase_levels)
        singular_values = svd_decompose(matrix).singular_values
        ideal_error = model.ideal_error
        mesh_error = model.mesh_error
        mapping_mode = "abstract_square_real_mesh"
    else:
        model = build_rectangular_mesh_transfer_model(matrix, case_id=case.case_id, phase_levels=phase_levels)
        singular_values = model.singular_values
        ideal_error = model.ideal_error
        mesh_error = model.mesh_error
        mapping_mode = "abstract_rectangular_orthogonal_completion_mesh"

    rank = _numerical_rank(singular_values)
    condition_number = _condition_number(singular_values, min(rows, cols))
    return _base_case_report(
        case=case,
        shape=[rows, cols],
        rank=rank,
        condition_number=condition_number,
        phase_levels=phase_levels,
        ideal_error=ideal_error,
        mesh_error=mesh_error,
        mapping_mode=mapping_mode,
        amplitude_error=None,
        phase_error=None,
    )


def _complex_case_report(case: MatrixFamilyCase, phase_levels: int) -> dict:
    matrix = case.matrix  # type: ignore[assignment]
    rows, cols = _complex_shape(matrix)
    model = build_complex_unitary_model(matrix, case_id=case.case_id, phase_levels=phase_levels)
    rank = _complex_qr_rank(model.residual_factor)
    return _base_case_report(
        case=case,
        shape=[rows, cols],
        rank=rank,
        condition_number=None,
        phase_levels=phase_levels,
        ideal_error=model.ideal_error,
        mesh_error=model.mesh_error,
        mapping_mode="complex_qr_unitary_factor",
        amplitude_error=model.amplitude_error,
        phase_error=model.phase_error,
    ) | {
        "unitaryFactorDeviation": round(model.approximated_unitarity_deviation, 15),
    }


def _base_case_report(
    case: MatrixFamilyCase,
    shape: List[int],
    rank: int,
    condition_number: float | None,
    phase_levels: int,
    ideal_error: float,
    mesh_error: float,
    mapping_mode: str,
    amplitude_error: float | None,
    phase_error: float | None,
) -> dict:
    return {
        "caseId": case.case_id,
        "matrixFamily": case.matrix_family,
        "shape": shape,
        "matrixShape": shape,
        "rank": rank,
        "conditionNumber": None if condition_number is None else round(condition_number, 15),
        "realOrComplex": case.real_or_complex,
        "mappingMode": mapping_mode,
        "phaseLevels": phase_levels,
        "idealReconstructionError": round(ideal_error, 15),
        "meshConstrainedReconstructionError": round(mesh_error, 15),
        "errorDelta": round(mesh_error - ideal_error, 15),
        "amplitudeError": None if amplitude_error is None else round(amplitude_error, 15),
        "phaseAwareError": None if phase_error is None else round(phase_error, 15),
        "limitations": case.limitations,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _case_summary(row: dict) -> dict:
    return {
        "caseId": row["caseId"],
        "matrixFamily": row["matrixFamily"],
        "shape": row["shape"],
        "realOrComplex": row["realOrComplex"],
        "meshConstrainedReconstructionError": row["meshConstrainedReconstructionError"],
        "errorDelta": row["errorDelta"],
    }


def _condition_ranking(rows: List[dict]) -> List[dict]:
    eligible = [row for row in rows if row["conditionNumber"] is not None]
    return [
        {
            "caseId": row["caseId"],
            "matrixFamily": row["matrixFamily"],
            "conditionNumber": row["conditionNumber"],
            "meshConstrainedReconstructionError": row["meshConstrainedReconstructionError"],
            "conditionSensitivityProxy": round(
                row["meshConstrainedReconstructionError"] * math.log10(max(row["conditionNumber"], 1.0)),
                15,
            ),
        }
        for row in sorted(
            eligible,
            key=lambda item: (
                item["meshConstrainedReconstructionError"] * math.log10(max(item["conditionNumber"], 1.0)),
                item["conditionNumber"],
            ),
            reverse=True,
        )
    ]


def _condition_number(singular_values: List[float], rank_width: int) -> float | None:
    positive = [value for value in singular_values if value > 1e-8]
    if len(positive) != rank_width or not positive:
        return None
    return max(positive) / min(positive)


def _numerical_rank(singular_values: List[float], tolerance: float = 1e-8) -> int:
    return sum(1 for value in singular_values if value > tolerance)


def _complex_qr_rank(residual_factor: ComplexMatrix, tolerance: float = 1e-10) -> int:
    return sum(1 for index, row in enumerate(residual_factor) if abs(row[index]) > tolerance)


def _real_shape(matrix: Matrix) -> tuple[int, int]:
    return len(matrix), len(matrix[0]) if matrix else 0


def _complex_shape(matrix: ComplexMatrix) -> tuple[int, int]:
    return len(matrix), len(matrix[0]) if matrix else 0


def _identity(size: int) -> Matrix:
    return [[1.0 if row == col else 0.0 for col in range(size)] for row in range(size)]


def _fourier_unitary_4x4() -> ComplexMatrix:
    size = 4
    scale = 1.0 / math.sqrt(size)
    return [
        [
            scale * complex(
                math.cos(2.0 * math.pi * row * col / size),
                math.sin(2.0 * math.pi * row * col / size),
            )
            for col in range(size)
        ]
        for row in range(size)
    ]
