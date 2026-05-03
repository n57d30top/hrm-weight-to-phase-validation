#!/usr/bin/env python3
"""Generate the HRM neural future-work validation ladder reports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from oqp.future_work.calibration_loop import (  # noqa: E402
    run_calibration_demo,
    run_calibration_sweep_analysis_report,
    run_calibration_sweep_report,
)
from oqp.future_work.mesh_mapping import run_mesh_constrained_demo  # noqa: E402
from oqp.future_work.neural_mapping import run_svd_mapping_demo  # noqa: E402
from oqp.future_work.perturbation_model import (  # noqa: E402
    run_perturbation_demo,
    run_perturbation_sweep_analysis_report,
    run_perturbation_sweep_report,
)
from oqp.future_work.validation_gates import (  # noqa: E402
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
    stage_0_specification_gate,
)


DOC_DIR = ROOT / "docs" / "future-work"
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"
SPEC_DOC = DOC_DIR / "hrm-neural-weight-to-phase-mapping.md"
LEDGER_PATH = DOC_DIR / "evidence-ledger.json"

STAGE_FILES = {
    0: "stage-0-specification.json",
    1: "stage-1-svd-demo.json",
    2: "stage-2-mesh-constrained.json",
    3: "stage-3-perturbation-model.json",
    4: "stage-4-simulated-calibration.json",
    5: "stage-5-foundry-calibration-gate.json",
    6: "stage-6-measured-transfer-matrix-gate.json",
    7: "stage-7-hardware-benchmark-gate.json",
}

SUPPLEMENTAL_REPORT_FILES = {
    "stage-3-perturbation-sweep": "stage-3-perturbation-sweep.json",
    "stage-3-sweep-analysis": "stage-3-sweep-analysis.json",
    "stage-4-calibration-analysis": "stage-4-calibration-analysis.json",
    "stage-4-calibration-sweep": "stage-4-calibration-sweep.json",
}


def main() -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    reports = [
        stage_0_specification_gate(SPEC_DOC),
        run_svd_mapping_demo(),
        run_mesh_constrained_demo(),
        run_perturbation_demo(),
        run_calibration_demo(),
        foundry_calibration_gate(DOC_DIR / "evidence-inputs" / "foundry-device-model.json"),
        measured_transfer_matrix_gate(DOC_DIR / "evidence-inputs" / "measured-transfer-matrix.json"),
        hardware_benchmark_gate(DOC_DIR / "evidence-inputs" / "hardware-benchmark.json"),
    ]

    supplemental_reports = [
        run_perturbation_sweep_report(),
        run_perturbation_sweep_analysis_report(),
        run_calibration_sweep_report(),
        run_calibration_sweep_analysis_report(),
    ]

    for report in reports:
        _write_json(REPORT_DIR / STAGE_FILES[int(report["stage"])], report)
    for report in supplemental_reports:
        _write_json(REPORT_DIR / SUPPLEMENTAL_REPORT_FILES[report["id"]], report)

    summary = _build_summary(reports, supplemental_reports)
    summary_path = REPORT_DIR / "validation-ladder-summary.json"
    _write_json(summary_path, summary)

    ledger = {
        "schemaVersion": "hrm-neural.future-work-ledger.v1",
        "entries": [_ledger_entry(report) for report in reports + supplemental_reports],
    }
    _write_json(LEDGER_PATH, ledger)

    artifact_paths = (
        [REPORT_DIR / STAGE_FILES[stage] for stage in sorted(STAGE_FILES)]
        + [REPORT_DIR / SUPPLEMENTAL_REPORT_FILES[key] for key in sorted(SUPPLEMENTAL_REPORT_FILES)]
        + [summary_path]
    )
    _write_artifact_hashes(artifact_paths, REPORT_DIR / "ARTIFACTS.sha256")

    print(json.dumps({
        "ok": True,
        "reportDir": str(REPORT_DIR),
        "ledger": str(LEDGER_PATH),
        "summary": str(summary_path),
        "stages": [{"stage": report["stage"], "stageStatus": report["stageStatus"]} for report in reports],
    }, sort_keys=True))


def _build_summary(reports: List[Dict[str, Any]], supplemental_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "id": "validation-ladder-summary",
        "title": "HRM neural weight-to-phase mapping validation ladder summary",
        "schemaVersion": "hrm-neural.validation-ladder.v1",
        "trackStatus": "future_work_only",
        "notIncludedInMainHardwareReadiness": True,
        "claimBoundary": "This future-work track does not improve hardware readiness and does not claim hardware-native intelligence, autonomous cognition, quantum consciousness, power-free computation, quantum advantage, hardware validation, foundry calibration, measured transfer matrices, production inference readiness, or a completed hardware benchmark.",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "stages": [
            {
                "stage": report["stage"],
                "id": report["id"],
                "title": report["title"],
                "stageStatus": report["stageStatus"],
                "evidenceLevel": report["evidenceLevel"],
                "hardwareValidated": report["hardwareValidated"],
                "foundryCalibrated": report["foundryCalibrated"],
                "measuredTransferMatrixAvailable": report["measuredTransferMatrixAvailable"],
                "productionInferenceReady": report["productionInferenceReady"],
                "keyMetrics": _key_metrics(report),
                "blockers": report.get("blockers", []),
            }
            for report in reports
        ],
        "supplementalReports": [
            {
                "stage": report["stage"],
                "id": report["id"],
                "title": report["title"],
                "stageStatus": report["stageStatus"],
                "evidenceLevel": report["evidenceLevel"],
                "hardwareValidated": report["hardwareValidated"],
                "foundryCalibrated": report["foundryCalibrated"],
                "measuredTransferMatrixAvailable": report["measuredTransferMatrixAvailable"],
                "productionInferenceReady": report["productionInferenceReady"],
                "keyMetrics": _key_metrics(report),
                "blockers": report.get("blockers", []),
            }
            for report in supplemental_reports
        ],
    }


def _key_metrics(report: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "relativeFrobeniusReconstructionError",
        "passiveRelativeFrobeniusReconstructionError",
        "idealSvdRelativeError",
        "meshConstrainedRelativeError",
        "meshErrorDelta",
        "abstractPhaseParameterizationImplemented",
        "abstractCouplerParameterizationImplemented",
        "physicalPhaseSynthesisImplemented",
        "physicalCouplerSynthesisImplemented",
        "foundryLayoutSynthesisImplemented",
        "baselineMeshRelativeError",
        "perturbedRelativeError",
        "errorDelta",
        "preCalibrationRelativeError",
        "postCalibrationRelativeError",
        "calibrationUsesMeasuredData",
        "calibrationUsesSyntheticTarget",
        "oracleTargetAvailableInSimulation",
        "hardwareCalibrationClaimed",
        "rowCount",
        "worstCaseErrorDelta",
        "bestCasePerturbedRelativeError",
        "bestCasePostCalibrationRelativeError",
        "worstCasePostCalibrationRelativeError",
        "failureCaseCount",
        "blockerReason",
    ]
    return {key: report[key] for key in keys if key in report}


def _ledger_entry(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": report["id"],
        "title": report["title"],
        "stage": report["stage"],
        "evidenceLevel": report["evidenceLevel"],
        "stageStatus": report["stageStatus"],
        "hardwareValidated": report["hardwareValidated"],
        "foundryCalibrated": report["foundryCalibrated"],
        "measuredTransferMatrixAvailable": report["measuredTransferMatrixAvailable"],
        "productionInferenceReady": report["productionInferenceReady"],
        "blockers": report.get("blockers", []),
        "nextValidationGates": report.get("nextValidationGates", []),
    }


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_artifact_hashes(paths: Iterable[Path], output_path: Path) -> None:
    lines = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rel = path.relative_to(ROOT)
        lines.append(f"{digest}  {rel}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
