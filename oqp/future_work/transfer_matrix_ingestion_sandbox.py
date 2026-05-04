"""Synthetic transfer-matrix ingestion sandbox.

The sandbox validates ingestion mechanics with synthetic fixtures only. It does
not provide measured transfer-matrix evidence and must not unblock Stage 6.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "transfer-matrix-sandbox" / "synthetic-transfer-matrix.json"
EVIDENCE_LEVEL = "synthetic_transfer_matrix_ingestion_sandbox"
CLAIM_BOUNDARY = (
    "Synthetic ingestion sandbox only; this does not claim measured transfer matrices, hardware validation, "
    "foundry calibration, production inference readiness, quantum advantage, hardware-native intelligence, "
    "or power-free computation."
)


def run_transfer_matrix_ingestion_sandbox_report(fixture_path: Path | None = None) -> Dict[str, Any]:
    path = fixture_path or FIXTURE
    payload = json.loads(path.read_text(encoding="utf-8"))
    validation = _validate_payload(payload)
    target = payload["targetMatrix"]
    synthetic = payload["syntheticObservedMatrix"]
    normalized_target = _normalize(target)
    normalized_synthetic = _normalize(synthetic)
    comparison = _matrix_comparison(normalized_target, normalized_synthetic)
    return {
        "id": "transfer-matrix-ingestion-sandbox",
        "title": "Synthetic transfer-matrix ingestion sandbox",
        "stage": 6,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "blocked",
        "syntheticFixtureOnly": True,
        "publicMeasuredEvidence": False,
        "measurementDataClaimed": False,
        "fixturePath": {
            "configured": path.relative_to(ROOT).as_posix(),
            "exists": path.is_file(),
        },
        "fixtureSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "validationPassed": validation["passed"],
        "validationFindings": validation["findings"],
        "normalization": {
            "method": "frobenius_norm",
            "targetNorm": round(_frobenius_norm(target), 15),
            "syntheticObservedNorm": round(_frobenius_norm(synthetic), 15),
        },
        "comparison": comparison,
        "sandboxLimitations": [
            "synthetic fixture only",
            "not public measured evidence",
            "does not satisfy Stage 6 measured-transfer-matrix gate",
            "does not satisfy Stage 7 hardware benchmark gate",
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": [
            "synthetic_fixture_only",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": [
            "measured_transfer_matrix_gate",
            "hardware_benchmark_gate",
        ],
    }


def _validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []
    for field in ["fixtureId", "fixtureKind", "targetMatrix", "syntheticObservedMatrix", "claimBoundary"]:
        if field not in payload:
            findings.append({"field": field, "reason": "missing_required_field"})
    if payload.get("fixtureKind") != "synthetic_test_only":
        findings.append({"field": "fixtureKind", "reason": "must_be_synthetic_test_only"})
    if "targetMatrix" in payload and "syntheticObservedMatrix" in payload:
        if _shape(payload["targetMatrix"]) != _shape(payload["syntheticObservedMatrix"]):
            findings.append({"field": "syntheticObservedMatrix", "reason": "shape_mismatch"})
    return {"passed": not findings, "findings": findings}


def _matrix_comparison(target: List[List[float]], observed: List[List[float]]) -> Dict[str, Any]:
    diff_sq = 0.0
    target_sq = 0.0
    max_abs = 0.0
    for row_t, row_o in zip(target, observed):
        for value_t, value_o in zip(row_t, row_o):
            delta = value_o - value_t
            diff_sq += delta * delta
            target_sq += value_t * value_t
            max_abs = max(max_abs, abs(delta))
    rel = math.sqrt(diff_sq) / max(math.sqrt(target_sq), 1e-12)
    return {
        "targetVsSyntheticRelativeFrobeniusError": round(rel, 15),
        "maxAbsoluteEntryDelta": round(max_abs, 15),
        "comparisonIsSyntheticOnly": True,
        "hardwareValidated": False,
        "measuredTransferMatrixAvailable": False,
    }


def _normalize(matrix: List[List[float]]) -> List[List[float]]:
    norm = max(_frobenius_norm(matrix), 1e-12)
    return [[value / norm for value in row] for row in matrix]


def _frobenius_norm(matrix: List[List[float]]) -> float:
    return math.sqrt(sum(value * value for row in matrix for value in row))


def _shape(matrix: List[List[float]]) -> List[int]:
    return [len(matrix), len(matrix[0]) if matrix else 0]
