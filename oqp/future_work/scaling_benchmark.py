"""Scaling benchmarks for HRM neural future work.

This module runs a deterministic, CI-light suite over larger square,
rectangular, low-rank, rank-deficient, dense, and complex phase-dominant
matrices. It reports abstract simulation errors only and deliberately avoids
hardware latency, throughput, or energy claims.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, List

from .complex_unitary_mapping import (
    ComplexMatrix,
    build_complex_unitary_model,
)
from .mesh_mapping import build_mesh_transfer_model
from .neural_mapping import Matrix, svd_decompose
from .rectangular_mapping import build_rectangular_mesh_transfer_model


EVIDENCE_LEVEL = "abstract_scaling_benchmark_simulation"
ANALYSIS_EVIDENCE_LEVEL = "abstract_scaling_analysis"


@dataclass(frozen=True)
class ScalingCase:
    case_id: str
    matrix_family: str
    real_or_complex: str
    matrix: Matrix | ComplexMatrix
    limitations: List[str]


def deterministic_scaling_cases() -> List[ScalingCase]:
    return [
        ScalingCase(
            "square_4x4",
            "square",
            "real",
            _dense_real_matrix(4, 4, seed=11),
            ["small square baseline case"],
        ),
        ScalingCase(
            "square_8x8",
            "square",
            "real",
            _dense_real_matrix(8, 8, seed=13),
            ["medium square simulation case"],
        ),
        ScalingCase(
            "square_16x16",
            "square",
            "real",
            _dense_real_matrix(16, 16, seed=17),
            ["largest square case in this CI-light suite"],
        ),
        ScalingCase(
            "rectangular_tall_8x4",
            "rectangular_tall",
            "real",
            _dense_real_matrix(8, 4, seed=19),
            ["rectangular tall simulation; no physical fan-in layout is defined"],
        ),
        ScalingCase(
            "rectangular_tall_16x8",
            "rectangular_tall",
            "real",
            _dense_real_matrix(16, 8, seed=23),
            ["largest tall rectangular case in this CI-light suite"],
        ),
        ScalingCase(
            "rectangular_wide_4x8",
            "rectangular_wide",
            "real",
            _dense_real_matrix(4, 8, seed=29),
            ["rectangular wide simulation; no physical fan-out layout is defined"],
        ),
        ScalingCase(
            "rectangular_wide_8x16",
            "rectangular_wide",
            "real",
            _dense_real_matrix(8, 16, seed=31),
            ["largest wide rectangular case in this CI-light suite"],
        ),
        ScalingCase(
            "low_rank_16x8",
            "low_rank",
            "real",
            _low_rank_real_matrix(16, 8),
            ["low-rank rectangular case; condition details are not hardware evidence"],
        ),
        ScalingCase(
            "rank_deficient_12x6",
            "rank_deficient",
            "real",
            _rank_deficient_real_matrix(12, 6),
            ["rank-deficient rectangular case; null-space behavior is simulation-only"],
        ),
        ScalingCase(
            "dense_seeded_16x16",
            "dense_seeded",
            "real",
            _dense_real_matrix(16, 16, seed=37),
            ["largest dense seeded square case in this CI-light suite"],
        ),
        ScalingCase(
            "phase_dominant_complex_8x8",
            "phase_dominant_complex",
            "complex",
            _phase_dominant_complex_matrix(8),
            ["complex QR unitary-factor handling only; no full complex SVD pipeline"],
        ),
    ]


def run_scaling_benchmark_report(phase_levels: int = 64) -> dict:
    cases = [_case_report(case, phase_levels) for case in deterministic_scaling_cases()]
    worst_case = max(cases, key=lambda row: row["meshConstrainedReconstructionError"])
    return {
        "id": "scaling-benchmark",
        "title": "Scaling benchmark for larger abstract HRM mapping simulations",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only scaling benchmark; no hardware validation, foundry calibration, measured transfer matrix, hardware latency, hardware throughput, hardware energy, accelerator performance, or production inference readiness is claimed.",
        "phaseLevels": phase_levels,
        "caseCount": len(cases),
        "sizeRange": _size_range(cases),
        "shapeFamilies": sorted({case["matrixFamily"] for case in cases}),
        "largestCaseId": max(cases, key=lambda row: row["parameterCount"])["caseId"],
        "maxMeshConstrainedError": worst_case["meshConstrainedReconstructionError"],
        "cases": cases,
        "noHardwarePerformanceClaim": True,
        "localSoftwareRuntimeMeasured": False,
        "hardwareLatency": None,
        "hardwareThroughput": None,
        "hardwareEnergy": None,
        "limitations": [
            "deterministic CI-light matrix suite only",
            "larger cases are still small compared with production neural layers",
            "real cases use abstract real-valued mesh simulation",
            "rectangular cases use orthogonal completion and rectangular sigma cores",
            "complex case uses complex QR unitary-factor handling, not full complex SVD",
            "no hardware latency, throughput, or energy measurement",
            "no foundry calibration or measured transfer matrix",
        ],
        "blockers": [
            "no_large_model_distribution",
            "no_hardware_performance_measurement",
            "no_foundry_calibrated_mesh_model",
            "no_measured_transfer_matrix",
        ],
        "nextValidationGates": [
            "review_pack",
            "release_candidate_hardening",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_scaling_analysis_report(phase_levels: int = 64) -> dict:
    benchmark = run_scaling_benchmark_report(phase_levels=phase_levels)
    cases = benchmark["cases"]
    best_case = min(cases, key=lambda row: row["meshConstrainedReconstructionError"])
    worst_case = max(cases, key=lambda row: row["meshConstrainedReconstructionError"])
    average_error = sum(row["meshConstrainedReconstructionError"] for row in cases) / len(cases)
    return {
        "id": "scaling-analysis",
        "title": "Scaling benchmark analysis",
        "stage": 2,
        "evidenceLevel": ANALYSIS_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only scaling analysis; no hardware validation, foundry calibration, measured transfer matrix, hardware latency, hardware energy efficiency, accelerator performance, or production inference readiness is claimed.",
        "benchmarkReport": "scaling-benchmark.json",
        "caseCount": benchmark["caseCount"],
        "sizeRange": benchmark["sizeRange"],
        "shapeFamilies": benchmark["shapeFamilies"],
        "bestCase": _case_summary(best_case),
        "worstCase": _case_summary(worst_case),
        "averageMeshConstrainedError": round(average_error, 15),
        "maxMeshConstrainedError": worst_case["meshConstrainedReconstructionError"],
        "errorByShapeFamily": _error_by_shape_family(cases),
        "errorByMatrixSize": _error_by_matrix_size(cases),
        "scalingNotes": [
            "No monotonic error trend is assumed across unrelated matrix families.",
            "Operation scale is a deterministic size proxy, not a runtime or hardware performance claim.",
            "Complex/unitary scaling currently covers one phase-dominant 8x8 case through QR unitary-factor handling.",
            "The largest real cases in this suite are 16x16, 16x8, and 8x16.",
        ],
        "limitations": benchmark["limitations"],
        "noHardwarePerformanceClaim": True,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "hardwareLatency": None,
        "hardwareEnergy": None,
        "blockers": benchmark["blockers"],
        "nextValidationGates": benchmark["nextValidationGates"],
    }


def _case_report(case: ScalingCase, phase_levels: int) -> dict:
    if case.real_or_complex == "complex":
        return _complex_case_report(case, phase_levels)
    return _real_case_report(case, phase_levels)


def _real_case_report(case: ScalingCase, phase_levels: int) -> dict:
    matrix = case.matrix  # type: ignore[assignment]
    rows, cols = _shape(matrix)
    if rows == cols:
        model = build_mesh_transfer_model(matrix, phase_levels=phase_levels)
        singular_values = svd_decompose(matrix).singular_values
        abstract_phase_count = len(model.left_mesh.phase_settings) + len(model.right_mesh.phase_settings)
        abstract_coupler_count = len(model.left_mesh.coupler_settings) + len(model.right_mesh.coupler_settings)
        mapping_mode = "abstract_square_real_mesh"
    else:
        model = build_rectangular_mesh_transfer_model(matrix, case_id=case.case_id, phase_levels=phase_levels)
        singular_values = model.singular_values
        abstract_phase_count = len(model.left_mesh.phase_settings) + len(model.right_mesh.phase_settings)
        abstract_coupler_count = len(model.left_mesh.coupler_settings) + len(model.right_mesh.coupler_settings)
        mapping_mode = "abstract_rectangular_orthogonal_completion_mesh"
    return _base_case_report(
        case=case,
        shape=[rows, cols],
        rank=_numerical_rank(singular_values),
        effective_rank=_numerical_rank(singular_values),
        phase_levels=phase_levels,
        parameter_count=rows * cols,
        abstract_phase_count=abstract_phase_count,
        abstract_coupler_count=abstract_coupler_count,
        ideal_error=model.ideal_error,
        mesh_error=model.mesh_error,
        mapping_mode=mapping_mode,
        amplitude_error=None,
        phase_error=None,
    )


def _complex_case_report(case: ScalingCase, phase_levels: int) -> dict:
    matrix = case.matrix  # type: ignore[assignment]
    rows, cols = _shape(matrix)
    model = build_complex_unitary_model(matrix, case_id=case.case_id, phase_levels=phase_levels)
    rank = _complex_qr_rank(model.residual_factor)
    return _base_case_report(
        case=case,
        shape=[rows, cols],
        rank=rank,
        effective_rank=rank,
        phase_levels=phase_levels,
        parameter_count=rows * cols,
        abstract_phase_count=None,
        abstract_coupler_count=None,
        ideal_error=model.ideal_error,
        mesh_error=model.mesh_error,
        mapping_mode="complex_qr_unitary_factor",
        amplitude_error=model.amplitude_error,
        phase_error=model.phase_error,
    )


def _base_case_report(
    case: ScalingCase,
    shape: List[int],
    rank: int,
    effective_rank: int,
    phase_levels: int,
    parameter_count: int,
    abstract_phase_count: int | None,
    abstract_coupler_count: int | None,
    ideal_error: float,
    mesh_error: float,
    mapping_mode: str,
    amplitude_error: float | None,
    phase_error: float | None,
) -> dict:
    return {
        "caseId": case.case_id,
        "shape": shape,
        "realOrComplex": case.real_or_complex,
        "matrixFamily": case.matrix_family,
        "rank": rank,
        "effectiveRank": effective_rank,
        "parameterCount": parameter_count,
        "abstractPhaseCount": abstract_phase_count,
        "abstractCouplerCount": abstract_coupler_count,
        "phaseLevels": phase_levels,
        "mappingMode": mapping_mode,
        "idealReconstructionError": round(ideal_error, 15),
        "meshConstrainedReconstructionError": round(mesh_error, 15),
        "errorDelta": round(mesh_error - ideal_error, 15),
        "amplitudeError": None if amplitude_error is None else round(amplitude_error, 15),
        "phaseAwareError": None if phase_error is None else round(phase_error, 15),
        "estimatedOperationScale": {
            "matrixVectorMultiplyTerms": parameter_count,
            "matrixShapeProduct": parameter_count,
            "isHardwarePerformanceClaim": False,
        },
        "localSoftwareRuntime": None,
        "hardwareLatency": None,
        "hardwareThroughput": None,
        "hardwareEnergy": None,
        "limitations": case.limitations,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _dense_real_matrix(rows: int, cols: int, seed: int) -> Matrix:
    scale = 1.0 / math.sqrt(max(rows, cols))
    return [
        [
            round(
                scale
                * (
                    math.sin((row + 1) * (col + 1 + seed) * 0.37)
                    + 0.5 * math.cos((row + seed + 1) * (col + 1) * 0.19)
                ),
                12,
            )
            for col in range(cols)
        ]
        for row in range(rows)
    ]


def _low_rank_real_matrix(rows: int, cols: int) -> Matrix:
    left_a = [math.sin((row + 1) * 0.31) for row in range(rows)]
    left_b = [math.cos((row + 1) * 0.17) for row in range(rows)]
    right_a = [math.cos((col + 1) * 0.23) for col in range(cols)]
    right_b = [math.sin((col + 1) * 0.41) for col in range(cols)]
    return [
        [round(0.45 * left_a[row] * right_a[col] + 0.25 * left_b[row] * right_b[col], 12) for col in range(cols)]
        for row in range(rows)
    ]


def _rank_deficient_real_matrix(rows: int, cols: int) -> Matrix:
    base = _low_rank_real_matrix(rows, cols)
    return [
        [
            round(base[row][col] + 0.05 * ((row % 3) - 1) * ((col % 2) - 0.5), 12)
            if col < cols - 1
            else round(base[row][0] + base[row][1], 12)
            for col in range(cols)
        ]
        for row in range(rows)
    ]


def _phase_dominant_complex_matrix(size: int) -> ComplexMatrix:
    return [
        [
            _polar(
                0.18 + (0.42 if row == col else 0.03 * ((row + col) % 3)),
                ((row + 1) * 0.47) - ((col + 1) * 0.29) + (0.11 * row * col),
            )
            for col in range(size)
        ]
        for row in range(size)
    ]


def _shape(matrix: Any) -> tuple[int, int]:
    return len(matrix), len(matrix[0]) if matrix else 0


def _numerical_rank(singular_values: List[float], tolerance: float = 1e-8) -> int:
    return sum(1 for value in singular_values if value > tolerance)


def _complex_qr_rank(residual_factor: ComplexMatrix, tolerance: float = 1e-10) -> int:
    return sum(1 for index, row in enumerate(residual_factor) if abs(row[index]) > tolerance)


def _polar(magnitude: float, phase: float) -> complex:
    return magnitude * complex(math.cos(phase), math.sin(phase))


def _case_summary(row: dict) -> dict:
    return {
        "caseId": row["caseId"],
        "shape": row["shape"],
        "matrixFamily": row["matrixFamily"],
        "realOrComplex": row["realOrComplex"],
        "parameterCount": row["parameterCount"],
        "meshConstrainedReconstructionError": row["meshConstrainedReconstructionError"],
        "errorDelta": row["errorDelta"],
    }


def _size_range(cases: List[dict]) -> dict:
    params = [case["parameterCount"] for case in cases]
    shapes = [case["shape"] for case in cases]
    return {
        "minParameterCount": min(params),
        "maxParameterCount": max(params),
        "minShape": min(shapes, key=lambda shape: shape[0] * shape[1]),
        "maxShape": max(shapes, key=lambda shape: shape[0] * shape[1]),
    }


def _error_by_shape_family(cases: List[dict]) -> List[dict]:
    return _grouped_error_summary(cases, "matrixFamily")


def _error_by_matrix_size(cases: List[dict]) -> List[dict]:
    rows = []
    for case in sorted(cases, key=lambda row: (row["parameterCount"], row["caseId"])):
        rows.append({
            "caseId": case["caseId"],
            "shape": case["shape"],
            "parameterCount": case["parameterCount"],
            "meshConstrainedReconstructionError": case["meshConstrainedReconstructionError"],
        })
    return rows


def _grouped_error_summary(cases: List[dict], key: str) -> List[dict]:
    groups: Dict[str, List[dict]] = {}
    for case in cases:
        groups.setdefault(case[key], []).append(case)
    summaries = []
    for name, rows in groups.items():
        average = sum(row["meshConstrainedReconstructionError"] for row in rows) / len(rows)
        worst = max(rows, key=lambda row: row["meshConstrainedReconstructionError"])
        summaries.append({
            "shapeFamily": name,
            "caseCount": len(rows),
            "averageMeshConstrainedError": round(average, 15),
            "worstCaseId": worst["caseId"],
            "maxMeshConstrainedError": worst["meshConstrainedReconstructionError"],
        })
    return sorted(summaries, key=lambda row: row["maxMeshConstrainedError"], reverse=True)
