"""Future-work validation helpers for HRM neural mapping.

These modules are simulation and evidence-gate utilities only. They do not
promote HRM neural mapping into hardware readiness evidence.
"""

from .neural_mapping import (
    SVDResult,
    deterministic_weight_matrix,
    passive_normalize_singular_values,
    reconstruct_from_svd,
    relative_frobenius_error,
    run_svd_mapping_demo,
    svd_decompose,
)
from .rectangular_mapping import (
    build_rectangular_mesh_transfer_model,
    run_rectangular_matrix_support_report,
)

__all__ = [
    "SVDResult",
    "deterministic_weight_matrix",
    "passive_normalize_singular_values",
    "reconstruct_from_svd",
    "relative_frobenius_error",
    "run_svd_mapping_demo",
    "build_rectangular_mesh_transfer_model",
    "run_rectangular_matrix_support_report",
    "svd_decompose",
]
