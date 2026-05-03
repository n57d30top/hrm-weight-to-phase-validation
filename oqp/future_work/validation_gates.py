"""Evidence gates for HRM neural mapping future work.

The gates block by default. They only report readiness when explicit evidence
manifests provide the required provenance fields. No data is inferred from the
main hardware readiness reports.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from datetime import date
from typing import Any, Dict, Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]

FOUNDATION_FALSE_FLAGS = {
    "hardwareValidated": False,
    "foundryCalibrated": False,
    "measuredTransferMatrixAvailable": False,
    "productionInferenceReady": False,
}

FOUNDRY_REQUIRED_FIELDS = [
    "artifactId",
    "evidenceClass",
    "foundryOrPdkSource",
    "sourceVersion",
    "sourceDate",
    "deviceScope",
    "sParameterArtifacts",
    "calibratedCompactModelArtifacts",
    "calibratedLossModelArtifact",
    "calibratedCrosstalkModelArtifact",
    "calibratedPhaseShifterModelArtifact",
    "wavelengthRange",
    "temperatureOrOperatingCondition",
    "calibrationProcedure",
    "provenance",
    "uncertaintyOrErrorEstimate",
    "operatorOrSource",
    "claimBoundary",
]

MEASURED_TRANSFER_MATRIX_REQUIRED_FIELDS = [
    "artifactId",
    "measurementDate",
    "deviceId",
    "setupDescription",
    "wavelength",
    "temperatureOrOperatingCondition",
    "matrixShape",
    "matrixConvention",
    "calibrationProcedure",
    "rawArtifactReference",
    "processedArtifactReference",
    "sha256Hash",
    "provenance",
    "uncertaintyOrErrorEstimate",
    "operatorOrSource",
    "claimBoundary",
]

HARDWARE_BENCHMARK_REQUIRED_FIELDS = [
    "benchmarkId",
    "deviceId",
    "measuredTransferMatrixReference",
    "dataset",
    "softwareBaseline",
    "inputEncoding",
    "outputReadout",
    "controlPathCharacterization",
    "detectorReadoutCharacterization",
    "accuracyMetric",
    "latencyMetric",
    "energyMetric",
    "driftRecalibrationMetric",
    "environment",
    "rawResultsHash",
    "processedResultsHash",
    "provenance",
    "claimBoundary",
]


def foundry_calibration_gate(manifest_path: str | Path | None = None) -> Dict[str, Any]:
    manifest = _read_manifest(manifest_path)
    base_dir = _manifest_base_dir(manifest_path)
    missing = validate_required_fields(manifest, FOUNDRY_REQUIRED_FIELDS)
    invalid: List[Dict[str, Any]] = []
    hash_mismatches: List[Dict[str, Any]] = []
    missing_artifacts: List[Dict[str, Any]] = []
    if manifest:
        _validate_stage_5_manifest(manifest, base_dir, missing_artifacts, hash_mismatches, invalid)
    calibrated = bool(manifest) and not missing and not invalid and not hash_mismatches and not missing_artifacts
    return {
        "id": "stage-5-foundry-calibration-gate",
        "title": "Foundry-calibrated device-model validation gate",
        "stage": 5,
        "evidenceLevel": "foundry_calibration_gate",
        "stageStatus": "complete" if calibrated else "blocked",
        "hardwareValidated": False,
        "foundryCalibrated": calibrated,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Gate only; no foundry calibration is claimed unless explicit foundry-calibrated S-parameters or equivalent models are supplied.",
        "acceptanceCriteria": FOUNDRY_REQUIRED_FIELDS,
        "manifestPath": _manifest_path_report(manifest_path),
        "missingEvidence": missing,
        "invalidEvidence": invalid,
        "hashMismatches": hash_mismatches,
        "missingArtifactReferences": missing_artifacts,
        "blockedByDependency": None,
        "blockerReason": None if calibrated else "no_foundry_calibrated_device_model",
        "blockers": [] if calibrated else ["no_foundry_calibrated_device_model"],
        "nextValidationGates": [
            "provide_foundry_sparameters_or_calibrated_compact_model",
            "run_measured_transfer_matrix_gate",
        ],
    }


def measured_transfer_matrix_gate(manifest_path: str | Path | None = None) -> Dict[str, Any]:
    manifest = _read_manifest(manifest_path)
    base_dir = _manifest_base_dir(manifest_path)
    missing = validate_required_fields(manifest, MEASURED_TRANSFER_MATRIX_REQUIRED_FIELDS)
    invalid: List[Dict[str, Any]] = []
    hash_mismatches: List[Dict[str, Any]] = []
    missing_artifacts: List[Dict[str, Any]] = []
    if manifest:
        _validate_stage_6_manifest(manifest, base_dir, missing_artifacts, hash_mismatches, invalid)
    available = bool(manifest) and not missing and not invalid and not hash_mismatches and not missing_artifacts
    return {
        "id": "stage-6-measured-transfer-matrix-gate",
        "title": "Measured HRM transfer-matrix validation gate",
        "stage": 6,
        "evidenceLevel": "measured_transfer_matrix_gate",
        "stageStatus": "complete" if available else "blocked",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": available,
        "productionInferenceReady": False,
        "claimBoundary": "Gate only; no measured transfer matrix is claimed unless provenance-bearing measured artifacts are supplied.",
        "acceptanceCriteria": MEASURED_TRANSFER_MATRIX_REQUIRED_FIELDS,
        "manifestPath": _manifest_path_report(manifest_path),
        "missingEvidence": missing,
        "invalidEvidence": invalid,
        "hashMismatches": hash_mismatches,
        "missingArtifactReferences": missing_artifacts,
        "blockedByDependency": None,
        "blockerReason": None if available else "no_measured_hrm_transfer_matrix",
        "blockers": [] if available else ["no_measured_hrm_transfer_matrix"],
        "nextValidationGates": [
            "provide_measured_hrm_transfer_matrix_with_provenance",
            "run_end_to_end_hardware_benchmark_gate",
        ],
    }


def hardware_benchmark_gate(
    manifest_path: str | Path | None = None,
    measured_transfer_matrix_report: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    manifest = _read_manifest(manifest_path)
    base_dir = _manifest_base_dir(manifest_path)
    missing = validate_required_fields(manifest, HARDWARE_BENCHMARK_REQUIRED_FIELDS)
    invalid: List[Dict[str, Any]] = []
    hash_mismatches: List[Dict[str, Any]] = []
    missing_artifacts: List[Dict[str, Any]] = []
    dependency_complete = _stage_6_dependency_complete(measured_transfer_matrix_report)
    blocked_by_dependency = None if dependency_complete else "stage_6_measured_transfer_matrix_gate_not_complete"
    if manifest:
        _validate_stage_7_manifest(manifest, base_dir, missing_artifacts, hash_mismatches, invalid)
    ready = (
        bool(manifest)
        and dependency_complete
        and not missing
        and not invalid
        and not hash_mismatches
        and not missing_artifacts
    )
    return {
        "id": "stage-7-hardware-benchmark-gate",
        "title": "End-to-end hardware inference benchmark gate",
        "stage": 7,
        "evidenceLevel": "hardware_benchmark_gate",
        "stageStatus": "complete" if ready else "blocked",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": dependency_complete,
        "productionInferenceReady": False,
        "claimBoundary": "Gate only; no production inference readiness is claimed unless end-to-end measured benchmark evidence is supplied.",
        "acceptanceCriteria": HARDWARE_BENCHMARK_REQUIRED_FIELDS,
        "manifestPath": _manifest_path_report(manifest_path),
        "missingEvidence": missing,
        "invalidEvidence": invalid,
        "hashMismatches": hash_mismatches,
        "missingArtifactReferences": missing_artifacts,
        "blockedByDependency": blocked_by_dependency,
        "blockerReason": None if ready else "no_end_to_end_hardware_benchmark",
        "blockers": [] if ready else ["no_end_to_end_hardware_benchmark"],
        "nextValidationGates": [
            "provide_measured_transfer_matrix",
            "provide_calibrated_io_and_control_characterization",
            "provide_dataset_baseline_metrics_latency_energy_and_drift_results",
        ],
    }


def stage_0_specification_gate(doc_path: str | Path) -> Dict[str, Any]:
    path = Path(doc_path)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_boundaries = [
        "Do not claim hardware-native intelligence",
        "Do not claim autonomous cognition",
        "Do not claim quantum consciousness",
        "Do not claim power-free computation",
        "Do not claim quantum advantage",
        "Do not claim production inference readiness",
        "Do not claim hardware validation unless measured hardware data is present",
        "Do not claim foundry calibration unless foundry-calibrated S-parameters or equivalent foundry device models are present",
        "Do not claim measured transfer matrices unless real measured transfer-matrix artifacts are present",
        "Do not promote this future-work track into the main hardware readiness score",
    ]
    missing = [boundary for boundary in required_boundaries if boundary not in text]
    forbidden_phrase_present = "validated compilation path" in text.lower()
    complete = path.exists() and not missing and not forbidden_phrase_present
    return {
        "id": "stage-0-specification",
        "title": "Future-work specification",
        "stage": 0,
        "evidenceLevel": "theoretical_extension",
        "stageStatus": "complete" if complete else "blocked",
        **FOUNDATION_FALSE_FLAGS,
        "docPath": _display_path(path),
        "claimBoundariesPresent": not missing,
        "missingClaimBoundaries": missing,
        "forbiddenHardwareCompilationPhrasePresent": forbidden_phrase_present,
        "blockers": [] if complete else ["future_work_specification_incomplete"],
        "nextValidationGates": [
            "numerical_svd_mapping_demo",
            "abstract_mesh_constrained_mapping",
        ],
    }


def _read_manifest(path: str | Path | None) -> Dict[str, Any]:
    if path is None:
        return {}
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {}
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"manifest must be a JSON object: {manifest_path}")
    return data


def validate_required_fields(manifest: Dict[str, Any], required_fields: Iterable[str]) -> List[str]:
    if not manifest:
        return list(required_fields)
    missing = []
    for field in required_fields:
        value = manifest.get(field)
        if value is None or value == "" or value == [] or value == {}:
            missing.append(field)
    return missing


def validate_relative_artifact_reference(path: Any, base_dir: str | Path | None = None) -> Tuple[bool, Path | None, str | None]:
    if not validate_nonempty_string(path):
        return False, None, "artifact_reference_must_be_nonempty_string"
    candidate = Path(str(path))
    if candidate.is_absolute():
        return False, None, "artifact_reference_must_be_relative"
    if ".." in candidate.parts:
        return False, None, "artifact_reference_must_not_escape_manifest_directory"
    root = Path(base_dir) if base_dir is not None else REPO_ROOT
    resolved = root / candidate
    if not resolved.is_file():
        return False, resolved, "artifact_reference_missing"
    return True, resolved, None


def validate_sha256(path: str | Path, expected_hash: Any) -> bool:
    if not validate_nonempty_string(expected_hash):
        return False
    expected = str(expected_hash).strip().lower()
    if not _is_sha256_hex(expected):
        return False
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return digest == expected


def validate_iso_date(value: Any) -> bool:
    if not validate_nonempty_string(value):
        return False
    try:
        date.fromisoformat(str(value))
    except ValueError:
        return False
    return True


def validate_allowed_value(value: Any, allowed_values: Iterable[str]) -> bool:
    if not validate_nonempty_string(value):
        return False
    return str(value) in set(allowed_values)


def validate_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_stage_5_manifest(
    manifest: Dict[str, Any],
    base_dir: Path,
    missing_artifacts: List[Dict[str, Any]],
    hash_mismatches: List[Dict[str, Any]],
    invalid: List[Dict[str, Any]],
) -> None:
    _validate_nonempty_fields(manifest, [
        "artifactId",
        "foundryOrPdkSource",
        "sourceVersion",
        "deviceScope",
        "wavelengthRange",
        "temperatureOrOperatingCondition",
        "calibrationProcedure",
        "provenance",
        "uncertaintyOrErrorEstimate",
        "operatorOrSource",
        "claimBoundary",
    ], invalid)
    if manifest.get("evidenceClass") != "foundry_calibrated_device_model":
        invalid.append({
            "field": "evidenceClass",
            "reason": "must_be_foundry_calibrated_device_model",
        })
    if not validate_iso_date(manifest.get("sourceDate")):
        invalid.append({"field": "sourceDate", "reason": "invalid_iso_date"})

    _validate_hash_reference_list(
        "sParameterArtifacts",
        manifest.get("sParameterArtifacts"),
        base_dir,
        missing_artifacts,
        hash_mismatches,
        invalid,
    )
    _validate_hash_reference_list(
        "calibratedCompactModelArtifacts",
        manifest.get("calibratedCompactModelArtifacts"),
        base_dir,
        missing_artifacts,
        hash_mismatches,
        invalid,
    )
    _validate_hash_reference(
        "calibratedLossModelArtifact",
        manifest.get("calibratedLossModelArtifact"),
        base_dir,
        missing_artifacts,
        hash_mismatches,
        invalid,
    )
    _validate_hash_reference(
        "calibratedCrosstalkModelArtifact",
        manifest.get("calibratedCrosstalkModelArtifact"),
        base_dir,
        missing_artifacts,
        hash_mismatches,
        invalid,
    )
    _validate_hash_reference(
        "calibratedPhaseShifterModelArtifact",
        manifest.get("calibratedPhaseShifterModelArtifact"),
        base_dir,
        missing_artifacts,
        hash_mismatches,
        invalid,
    )


def _validate_stage_6_manifest(
    manifest: Dict[str, Any],
    base_dir: Path,
    missing_artifacts: List[Dict[str, Any]],
    hash_mismatches: List[Dict[str, Any]],
    invalid: List[Dict[str, Any]],
) -> None:
    _validate_nonempty_fields(manifest, [
        "artifactId",
        "deviceId",
        "setupDescription",
        "wavelength",
        "temperatureOrOperatingCondition",
        "calibrationProcedure",
        "provenance",
        "uncertaintyOrErrorEstimate",
        "operatorOrSource",
        "claimBoundary",
    ], invalid)
    if not validate_iso_date(manifest.get("measurementDate")):
        invalid.append({"field": "measurementDate", "reason": "invalid_iso_date"})
    if not validate_allowed_value(manifest.get("matrixConvention"), ["real", "complex"]):
        invalid.append({"field": "matrixConvention", "reason": "allowed_values_are_real_or_complex"})
    if not _valid_matrix_shape(manifest.get("matrixShape")):
        invalid.append({"field": "matrixShape", "reason": "matrix_shape_must_be_nonempty_positive_integer_list"})

    raw_ok, _, raw_error = validate_relative_artifact_reference(manifest.get("rawArtifactReference"), base_dir)
    if not raw_ok:
        missing_artifacts.append({
            "field": "rawArtifactReference",
            "path": manifest.get("rawArtifactReference"),
            "reason": raw_error,
        })
    processed_ok, processed_path, processed_error = validate_relative_artifact_reference(
        manifest.get("processedArtifactReference"),
        base_dir,
    )
    if not processed_ok:
        missing_artifacts.append({
            "field": "processedArtifactReference",
            "path": manifest.get("processedArtifactReference"),
            "reason": processed_error,
        })
    elif not validate_sha256(processed_path, manifest.get("sha256Hash")):
        hash_mismatches.append({
            "field": "sha256Hash",
            "path": manifest.get("processedArtifactReference"),
            "reason": "sha256_mismatch",
        })


def _validate_stage_7_manifest(
    manifest: Dict[str, Any],
    base_dir: Path,
    missing_artifacts: List[Dict[str, Any]],
    hash_mismatches: List[Dict[str, Any]],
    invalid: List[Dict[str, Any]],
) -> None:
    _validate_nonempty_fields(manifest, [
        "benchmarkId",
        "deviceId",
        "measuredTransferMatrixReference",
        "dataset",
        "softwareBaseline",
        "inputEncoding",
        "outputReadout",
        "controlPathCharacterization",
        "detectorReadoutCharacterization",
        "accuracyMetric",
        "latencyMetric",
        "energyMetric",
        "driftRecalibrationMetric",
        "environment",
        "provenance",
        "claimBoundary",
    ], invalid)
    mtx_ok, _, mtx_error = validate_relative_artifact_reference(
        manifest.get("measuredTransferMatrixReference"),
        base_dir,
    )
    if not mtx_ok:
        missing_artifacts.append({
            "field": "measuredTransferMatrixReference",
            "path": manifest.get("measuredTransferMatrixReference"),
            "reason": mtx_error,
        })
    _validate_hash_reference("rawResultsHash", manifest.get("rawResultsHash"), base_dir, missing_artifacts, hash_mismatches, invalid)
    _validate_hash_reference(
        "processedResultsHash",
        manifest.get("processedResultsHash"),
        base_dir,
        missing_artifacts,
        hash_mismatches,
        invalid,
    )


def _validate_hash_reference_list(
    field: str,
    values: Any,
    base_dir: Path,
    missing_artifacts: List[Dict[str, Any]],
    hash_mismatches: List[Dict[str, Any]],
    invalid: List[Dict[str, Any]],
) -> None:
    if not isinstance(values, list) or not values:
        invalid.append({"field": field, "reason": "expected_nonempty_hash_reference_list"})
        return
    for index, value in enumerate(values):
        _validate_hash_reference(
            f"{field}[{index}]",
            value,
            base_dir,
            missing_artifacts,
            hash_mismatches,
            invalid,
        )


def _validate_hash_reference(
    field: str,
    value: Any,
    base_dir: Path,
    missing_artifacts: List[Dict[str, Any]],
    hash_mismatches: List[Dict[str, Any]],
    invalid: List[Dict[str, Any]],
) -> None:
    artifact_reference, expected_hash = _hash_reference_parts(value)
    if artifact_reference is None or expected_hash is None:
        invalid.append({"field": field, "reason": "expected_hash_reference_with_artifactReference_and_sha256"})
        return
    ok, artifact_path, error = validate_relative_artifact_reference(artifact_reference, base_dir)
    if not ok:
        missing_artifacts.append({"field": field, "path": artifact_reference, "reason": error})
        return
    if not validate_sha256(artifact_path, expected_hash):
        hash_mismatches.append({"field": field, "path": artifact_reference, "reason": "sha256_mismatch"})


def _hash_reference_parts(value: Any) -> Tuple[str | None, str | None]:
    if isinstance(value, dict):
        reference = value.get("artifactReference") or value.get("path")
        expected = value.get("sha256") or value.get("hash")
        return reference, expected
    if validate_nonempty_string(value):
        parts = str(value).split()
        if len(parts) == 2 and _is_sha256_hex(parts[0]):
            return parts[1], parts[0]
    return None, None


def _validate_nonempty_fields(manifest: Dict[str, Any], fields: Iterable[str], invalid: List[Dict[str, Any]]) -> None:
    for field in fields:
        if field in manifest and not validate_nonempty_string(manifest.get(field)):
            invalid.append({"field": field, "reason": "must_be_nonempty_string"})


def _valid_matrix_shape(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, int) and item > 0 for item in value)


def _stage_6_dependency_complete(report: Dict[str, Any] | None) -> bool:
    return bool(
        report
        and report.get("stageStatus") == "complete"
        and report.get("measuredTransferMatrixAvailable") is True
    )


def _manifest_base_dir(path: str | Path | None) -> Path:
    if path is None:
        return REPO_ROOT
    return Path(path).parent


def _manifest_path_report(path: str | Path | None) -> Dict[str, Any] | None:
    if path is None:
        return None
    manifest_path = Path(path)
    return {
        "configured": _display_path(manifest_path),
        "exists": manifest_path.exists(),
    }


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value.lower())
