"""Calibration and transfer-matrix assimilation planning artifacts."""

from __future__ import annotations

from typing import Any, Dict, List


CALIBRATION_EVIDENCE_LEVEL = "calibration_plan_only"
ASSIMILATION_EVIDENCE_LEVEL = "transfer_matrix_assimilation_plan_only"
CLAIM_BOUNDARY = (
    "Plan only; no measured transfer matrix is available, no hardware validation is claimed, "
    "and Stage 6 remains blocked."
)


def run_calibration_plan_report() -> Dict[str, Any]:
    required_measurement_vectors = [
        "canonical basis inputs",
        "phase-stepped calibration tones",
        "held-out validation vectors",
    ]
    acceptance_criteria = [
        "all raw and processed artifact hashes verify",
        "matrix shape and convention match manifest",
        "held-out validation error is reported",
        "provenance and operator/source are declared",
    ]
    return {
        "id": "calibration-plan",
        "title": "Calibration plan for future measured HRM transfer matrices",
        "stage": 6,
        "evidenceLevel": CALIBRATION_EVIDENCE_LEVEL,
        "stageStatus": "blocked",
        "calibrationPlanOnly": True,
        "assimilationPlanOnly": False,
        "measuredTransferMatrixAvailable": False,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "productionInferenceReady": False,
        "requiredMeasurementVectors": required_measurement_vectors,
        "measurementVectorCount": len(required_measurement_vectors),
        "inputBasis": "canonical_complex_field_basis",
        "outputReadoutConvention": "complex_field_or_real_intensity_with_declared_phase_recovery",
        "wavelengthCondition": "single wavelength or wavelength sweep declared by measurement package",
        "temperatureCondition": "temperature logged for each measured transfer-matrix artifact",
        "matrixConvention": ["real", "complex"],
        "calibrationSequence": [
            "measure dark/readout baseline",
            "measure input basis responses",
            "estimate transfer matrix",
            "normalize according to declared convention",
            "validate on held-out vectors",
            "hash raw and processed artifacts",
        ],
        "driftMonitoringPlan": [
            "repeat sentinel vector measurements",
            "track transfer-matrix delta over time",
            "record temperature and control settings",
        ],
        "recalibrationTrigger": "sentinel_relative_error_exceeds_declared_threshold",
        "acceptanceCriteria": acceptance_criteria,
        "acceptanceCriteriaCount": len(acceptance_criteria),
        "requiredArtifactHashes": ["raw measurement package", "processed transfer matrix", "validation summary"],
        "requiredProvenance": ["device id", "measurement date", "operator or source", "setup description"],
        "claimBoundary": CLAIM_BOUNDARY,
        "blockers": ["no_measured_hrm_transfer_matrix"],
        "nextValidationGates": ["measured_transfer_matrix_gate", "hardware_benchmark_gate"],
    }


def run_transfer_matrix_assimilation_plan_report() -> Dict[str, Any]:
    return {
        "id": "transfer-matrix-assimilation-plan",
        "title": "Transfer-matrix assimilation plan for future measured artifacts",
        "stage": 6,
        "evidenceLevel": ASSIMILATION_EVIDENCE_LEVEL,
        "stageStatus": "blocked",
        "calibrationPlanOnly": False,
        "assimilationPlanOnly": True,
        "measuredTransferMatrixAvailable": False,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "productionInferenceReady": False,
        "measuredTransferMatrixInput": "required future Stage 6 artifact",
        "targetTransferMatrix": "abstract HRM transfer candidate from simulation report",
        "alignmentNormalizationStep": [
            "match matrix convention",
            "normalize global phase or scale according to manifest",
            "align input and output channel ordering",
        ],
        "errorMetrics": [
            "relative Frobenius error",
            "phase-aware error when complex data exists",
            "amplitude error",
            "held-out vector output error",
        ],
        "correctionFittingStep": [
            "fit diagonal phase/scale corrections first",
            "fit low-order coupling correction only if justified by measured data",
            "report residual error after correction",
        ],
        "validationVectors": [
            "canonical basis holdout",
            "seeded dense validation vectors",
            "model-layer representative vectors",
        ],
        "passFailCriteria": [
            "all referenced artifacts exist and hash-verify",
            "declared uncertainty is present",
            "validation vector residuals are below declared threshold",
            "claim boundary remains explicit",
        ],
        "limitations": [
            "no measured matrix is included",
            "assimilation cannot complete until Stage 6 evidence exists",
            "does not imply production inference readiness",
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "blockers": ["no_measured_hrm_transfer_matrix"],
        "nextValidationGates": ["measured_transfer_matrix_gate", "hardware_benchmark_gate"],
    }


def render_transfer_matrix_assimilation_protocol() -> str:
    plan = run_calibration_plan_report()
    assimilation = run_transfer_matrix_assimilation_plan_report()
    lines = [
        "# Transfer-Matrix Assimilation Protocol",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Required Measurement Fields",
        "",
    ]
    for item in plan["requiredProvenance"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Calibration Sequence",
        "",
    ])
    for item in plan["calibrationSequence"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Assimilation Steps",
        "",
    ])
    for item in assimilation["alignmentNormalizationStep"] + assimilation["correctionFittingStep"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Pass/Fail Criteria",
        "",
    ])
    for item in assimilation["passFailCriteria"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)
