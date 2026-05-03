"""Evidence gates for HRM neural mapping future work.

The gates block by default. They only report readiness when explicit evidence
manifests provide the required provenance fields. No data is inferred from the
main hardware readiness reports.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

FOUNDATION_FALSE_FLAGS = {
    "hardwareValidated": False,
    "foundryCalibrated": False,
    "measuredTransferMatrixAvailable": False,
    "productionInferenceReady": False,
}

FOUNDRY_REQUIRED_FIELDS = [
    "evidenceClass",
    "foundrySParameters",
    "calibratedCompactModel",
    "foundryPdkReference",
    "calibratedLossModel",
    "calibratedCrosstalkModel",
    "calibratedPhaseShifterModel",
    "artifactHash",
]

MEASURED_TRANSFER_MATRIX_REQUIRED_FIELDS = [
    "measurementDate",
    "instrumentOrSetupDescription",
    "matrixShape",
    "wavelengthNm",
    "operatingCondition",
    "calibrationProcedure",
    "matrixArtifactRef",
    "artifactHash",
]

HARDWARE_BENCHMARK_REQUIRED_FIELDS = [
    "measuredTransferMatrix",
    "calibratedInputOutputEncoding",
    "detectorReadoutModelOrMeasurement",
    "dacAdcOrControlPathCharacterization",
    "taskDataset",
    "softwareBaseline",
    "accuracyMetric",
    "latencyMetric",
    "energyMetric",
    "driftRecalibrationMetric",
]


def foundry_calibration_gate(manifest_path: str | Path | None = None) -> Dict[str, Any]:
    manifest = _read_manifest(manifest_path)
    missing = _missing_fields(manifest, FOUNDRY_REQUIRED_FIELDS)
    calibrated = bool(manifest) and not missing and manifest.get("evidenceClass") == "foundry_calibrated_device_model"
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
        "manifestPath": str(manifest_path) if manifest_path else None,
        "missingEvidence": missing,
        "blockerReason": None if calibrated else "no_foundry_calibrated_device_model",
        "blockers": [] if calibrated else ["no_foundry_calibrated_device_model"],
        "nextValidationGates": [
            "provide_foundry_sparameters_or_calibrated_compact_model",
            "run_measured_transfer_matrix_gate",
        ],
    }


def measured_transfer_matrix_gate(manifest_path: str | Path | None = None) -> Dict[str, Any]:
    manifest = _read_manifest(manifest_path)
    missing = _missing_fields(manifest, MEASURED_TRANSFER_MATRIX_REQUIRED_FIELDS)
    available = bool(manifest) and not missing
    return {
        "id": "stage-6-measured-transfer-matrix-gate",
        "title": "Measured HRM transfer-matrix validation gate",
        "stage": 6,
        "evidenceLevel": "measured_transfer_matrix_gate",
        "stageStatus": "complete" if available else "blocked",
        "hardwareValidated": available,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": available,
        "productionInferenceReady": False,
        "claimBoundary": "Gate only; no measured transfer matrix is claimed unless provenance-bearing measured artifacts are supplied.",
        "acceptanceCriteria": MEASURED_TRANSFER_MATRIX_REQUIRED_FIELDS,
        "manifestPath": str(manifest_path) if manifest_path else None,
        "missingEvidence": missing,
        "blockerReason": None if available else "no_measured_hrm_transfer_matrix",
        "blockers": [] if available else ["no_measured_hrm_transfer_matrix"],
        "nextValidationGates": [
            "provide_measured_hrm_transfer_matrix_with_provenance",
            "run_end_to_end_hardware_benchmark_gate",
        ],
    }


def hardware_benchmark_gate(manifest_path: str | Path | None = None) -> Dict[str, Any]:
    manifest = _read_manifest(manifest_path)
    missing = _missing_fields(manifest, HARDWARE_BENCHMARK_REQUIRED_FIELDS)
    ready = bool(manifest) and not missing
    return {
        "id": "stage-7-hardware-benchmark-gate",
        "title": "End-to-end hardware inference benchmark gate",
        "stage": 7,
        "evidenceLevel": "hardware_benchmark_gate",
        "stageStatus": "complete" if ready else "blocked",
        "hardwareValidated": ready,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": bool(manifest.get("measuredTransferMatrix")) if manifest else False,
        "productionInferenceReady": ready,
        "claimBoundary": "Gate only; no production inference readiness is claimed unless end-to-end measured benchmark evidence is supplied.",
        "acceptanceCriteria": HARDWARE_BENCHMARK_REQUIRED_FIELDS,
        "manifestPath": str(manifest_path) if manifest_path else None,
        "missingEvidence": missing,
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
        "docPath": str(path),
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


def _missing_fields(manifest: Dict[str, Any], fields: Iterable[str]) -> List[str]:
    if not manifest:
        return list(fields)
    missing = []
    for field in fields:
        value = manifest.get(field)
        if value is None or value == "" or value == [] or value == {}:
            missing.append(field)
    return missing
