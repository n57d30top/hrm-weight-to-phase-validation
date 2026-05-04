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
from oqp.future_work.complex_unitary_mapping import run_complex_unitary_mesh_support_report  # noqa: E402
from oqp.future_work.calibration_planner import (  # noqa: E402
    render_transfer_matrix_assimilation_protocol,
    run_calibration_plan_report,
    run_transfer_matrix_assimilation_plan_report,
)
from oqp.future_work.decision_report import (  # noqa: E402
    render_model_to_hrm_decision_markdown,
    run_model_to_hrm_decision_report,
)
from oqp.future_work.design_space_explorer import (  # noqa: E402
    render_hardware_design_space_pareto,
    run_hardware_design_space_analysis_report,
    run_hardware_design_space_sweep_report,
)
from oqp.future_work.error_budget import (  # noqa: E402
    render_error_budget_markdown,
    run_error_budget_report,
)
from oqp.future_work.hardware_requirements import (  # noqa: E402
    run_hardware_requirements_analysis_report,
    run_hardware_requirements_envelope_report,
)
from oqp.future_work.hardware_scenario_estimator import (  # noqa: E402
    run_hardware_scenario_analysis_report,
    run_hardware_scenario_estimates_report,
)
from oqp.future_work.matrix_family_benchmark import (  # noqa: E402
    run_matrix_family_analysis_report,
    run_matrix_family_benchmark_report,
)
from oqp.future_work.layer_stack_inference import (  # noqa: E402
    run_layer_stack_error_analysis_report,
    run_layer_stack_inference_demo_report,
)
from oqp.future_work.mesh_mapping import run_mesh_constrained_demo  # noqa: E402
from oqp.future_work.model_export_adapter import (  # noqa: E402
    render_model_export_adapter_protocol,
    run_model_export_adapter_demo_report,
    run_model_export_adapter_validation_report,
)
from oqp.future_work.model_portfolio import (  # noqa: E402
    render_model_portfolio_decision_summary,
    run_model_portfolio_benchmark_report,
    run_model_portfolio_ranking_report,
)
from oqp.future_work.model_weight_manifest import (  # noqa: E402
    run_model_weight_eligibility_analysis_report,
    run_model_weight_import_demo_report,
)
from oqp.future_work.model_suitability import (  # noqa: E402
    run_model_suitability_analysis_report,
    run_model_suitability_profile_report,
)
from oqp.future_work.neural_mapping import run_svd_mapping_demo  # noqa: E402
from oqp.future_work.perturbation_model import (  # noqa: E402
    run_perturbation_demo,
    run_perturbation_sweep_analysis_report,
    run_perturbation_sweep_report,
)
from oqp.future_work.rectangular_mapping import run_rectangular_matrix_support_report  # noqa: E402
from oqp.future_work.rc_readiness import (  # noqa: E402
    render_rc1_readiness_markdown,
    run_rc1_readiness_report,
)
from oqp.future_work.release_readiness import (  # noqa: E402
    render_release_readiness_markdown,
    run_release_readiness_report,
)
from oqp.future_work.review_pack import (  # noqa: E402
    render_review_pack_limitations_markdown,
    render_review_pack_markdown,
    render_review_pack_metrics_csv,
    render_review_pack_stage_table_markdown,
    run_review_pack_summary_report,
)
from oqp.future_work.scaling_benchmark import (  # noqa: E402
    run_scaling_analysis_report,
    run_scaling_benchmark_report,
)
from oqp.future_work.static_dashboard import render_static_dashboard  # noqa: E402
from oqp.future_work.transfer_matrix_ingestion_sandbox import run_transfer_matrix_ingestion_sandbox_report  # noqa: E402
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
    "calibration-plan": "calibration-plan.json",
    "complex-unitary-mesh-support": "complex-unitary-mesh-support.json",
    "error-budget-report": "error-budget-report.json",
    "hardware-design-space-analysis": "hardware-design-space-analysis.json",
    "hardware-design-space-sweep": "hardware-design-space-sweep.json",
    "hardware-requirements-analysis": "hardware-requirements-analysis.json",
    "hardware-requirements-envelope": "hardware-requirements-envelope.json",
    "hardware-scenario-analysis": "hardware-scenario-analysis.json",
    "hardware-scenario-estimates": "hardware-scenario-estimates.json",
    "layer-stack-error-analysis": "layer-stack-error-analysis.json",
    "layer-stack-inference-demo": "layer-stack-inference-demo.json",
    "matrix-family-analysis": "matrix-family-analysis.json",
    "matrix-family-benchmark": "matrix-family-benchmark.json",
    "model-export-adapter-demo": "model-export-adapter-demo.json",
    "model-export-adapter-validation": "model-export-adapter-validation.json",
    "model-portfolio-benchmark": "model-portfolio-benchmark.json",
    "model-portfolio-ranking": "model-portfolio-ranking.json",
    "model-to-hrm-decision-report": "model-to-hrm-decision-report.json",
    "model-weight-eligibility-analysis": "model-weight-eligibility-analysis.json",
    "model-weight-import-demo": "model-weight-import-demo.json",
    "model-suitability-analysis": "model-suitability-analysis.json",
    "model-suitability-profile": "model-suitability-profile.json",
    "rectangular-matrix-support": "rectangular-matrix-support.json",
    "release-readiness-v0.1.0": "release-readiness-v0.1.0.json",
    "review-pack-summary": "review-pack-summary.json",
    "scaling-analysis": "scaling-analysis.json",
    "scaling-benchmark": "scaling-benchmark.json",
    "stage-3-perturbation-sweep": "stage-3-perturbation-sweep.json",
    "stage-3-sweep-analysis": "stage-3-sweep-analysis.json",
    "stage-4-calibration-analysis": "stage-4-calibration-analysis.json",
    "stage-4-calibration-sweep": "stage-4-calibration-sweep.json",
    "transfer-matrix-assimilation-plan": "transfer-matrix-assimilation-plan.json",
    "transfer-matrix-ingestion-sandbox": "transfer-matrix-ingestion-sandbox.json",
    "v0.1.0-rc1-readiness": "v0.1.0-rc1-readiness.json",
}


def main() -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    stage_5 = foundry_calibration_gate(DOC_DIR / "evidence-inputs" / "foundry-device-model.json")
    stage_6 = measured_transfer_matrix_gate(DOC_DIR / "evidence-inputs" / "measured-transfer-matrix.json")
    stage_7 = hardware_benchmark_gate(
        DOC_DIR / "evidence-inputs" / "hardware-benchmark.json",
        measured_transfer_matrix_report=stage_6,
    )

    reports = [
        stage_0_specification_gate(SPEC_DOC),
        run_svd_mapping_demo(),
        run_mesh_constrained_demo(),
        run_perturbation_demo(),
        run_calibration_demo(),
        stage_5,
        stage_6,
        stage_7,
    ]

    supplemental_reports = [
        run_complex_unitary_mesh_support_report(),
        run_layer_stack_inference_demo_report(),
        run_layer_stack_error_analysis_report(),
        run_matrix_family_benchmark_report(),
        run_matrix_family_analysis_report(),
        run_model_weight_import_demo_report(),
        run_model_weight_eligibility_analysis_report(),
        run_model_suitability_profile_report(),
        run_model_suitability_analysis_report(),
        run_model_portfolio_benchmark_report(),
        run_model_portfolio_ranking_report(),
        run_model_export_adapter_demo_report(),
        run_model_export_adapter_validation_report(),
        run_rectangular_matrix_support_report(),
        run_scaling_benchmark_report(),
        run_scaling_analysis_report(),
        run_hardware_design_space_sweep_report(),
        run_hardware_design_space_analysis_report(),
        run_hardware_scenario_estimates_report(),
        run_hardware_scenario_analysis_report(),
        run_hardware_requirements_envelope_report(),
        run_hardware_requirements_analysis_report(),
        run_error_budget_report(),
        run_calibration_plan_report(),
        run_transfer_matrix_assimilation_plan_report(),
        run_transfer_matrix_ingestion_sandbox_report(),
        run_model_to_hrm_decision_report(),
        run_perturbation_sweep_report(),
        run_perturbation_sweep_analysis_report(),
        run_calibration_sweep_report(),
        run_calibration_sweep_analysis_report(),
    ]
    review_pack_summary = run_review_pack_summary_report(reports, supplemental_reports)
    supplemental_reports.append(review_pack_summary)
    release_readiness = run_release_readiness_report(reports, supplemental_reports)
    supplemental_reports.append(release_readiness)
    rc1_readiness = run_rc1_readiness_report(reports, supplemental_reports)
    supplemental_reports.append(rc1_readiness)

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

    review_pack_artifact_paths = [
        REPORT_DIR / "review-pack.md",
        REPORT_DIR / "review-pack-metrics.csv",
        REPORT_DIR / "review-pack-stage-table.md",
        REPORT_DIR / "review-pack-limitations.md",
    ]
    release_readiness_artifact_paths = [
        REPORT_DIR / "release-readiness-v0.1.0.md",
    ]
    planning_artifact_paths = [
        REPORT_DIR / "error-budget-analysis.md",
        REPORT_DIR / "model-to-hrm-decision-report.md",
        REPORT_DIR / "model-portfolio-decision-summary.md",
        REPORT_DIR / "hardware-design-space-pareto.md",
        REPORT_DIR / "v0.1.0-rc1-readiness.md",
        DOC_DIR / "transfer-matrix-assimilation-protocol.md",
        DOC_DIR / "model-export-adapter-protocol.md",
        ROOT / "docs" / "ROADMAP-v0.2.md",
        ROOT / "docs" / "REVIEWER_GUIDE.md",
        ROOT / "docs" / "QUICKSTART.md",
        ROOT / "dashboard" / "index.html",
        ROOT / "fixtures" / "model-export-adapter" / "tiny-linear-export-example.json",
        ROOT / "fixtures" / "transfer-matrix-sandbox" / "synthetic-transfer-matrix.json",
    ]
    _write_text(review_pack_artifact_paths[0], render_review_pack_markdown(review_pack_summary))
    _write_text(review_pack_artifact_paths[1], render_review_pack_metrics_csv(review_pack_summary))
    _write_text(review_pack_artifact_paths[2], render_review_pack_stage_table_markdown(review_pack_summary))
    _write_text(review_pack_artifact_paths[3], render_review_pack_limitations_markdown(review_pack_summary))
    _write_text(release_readiness_artifact_paths[0], render_release_readiness_markdown(release_readiness))
    _write_text(planning_artifact_paths[0], render_error_budget_markdown(_report_by_id(supplemental_reports, "error-budget-report")))
    _write_text(
        planning_artifact_paths[1],
        render_model_to_hrm_decision_markdown(_report_by_id(supplemental_reports, "model-to-hrm-decision-report")),
    )
    _write_text(
        planning_artifact_paths[2],
        render_model_portfolio_decision_summary(_report_by_id(supplemental_reports, "model-portfolio-ranking")),
    )
    _write_text(
        planning_artifact_paths[3],
        render_hardware_design_space_pareto(_report_by_id(supplemental_reports, "hardware-design-space-analysis")),
    )
    _write_text(planning_artifact_paths[4], render_rc1_readiness_markdown(rc1_readiness))
    _write_text(planning_artifact_paths[5], render_transfer_matrix_assimilation_protocol())
    _write_text(planning_artifact_paths[6], render_model_export_adapter_protocol())
    _write_text(planning_artifact_paths[7], _render_v02_roadmap())
    _write_text(planning_artifact_paths[10], render_static_dashboard(reports, supplemental_reports))

    artifact_paths = (
        [REPORT_DIR / STAGE_FILES[stage] for stage in sorted(STAGE_FILES)]
        + [REPORT_DIR / SUPPLEMENTAL_REPORT_FILES[key] for key in sorted(SUPPLEMENTAL_REPORT_FILES)]
        + [summary_path]
        + review_pack_artifact_paths
        + release_readiness_artifact_paths
        + planning_artifact_paths
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
        "rectangularLayerSupportImplemented",
        "rectangularMode",
        "meshConstrainedReconstructionErrorMax",
        "averageMeshConstrainedError",
        "errorDeltaMax",
        "maxErrorDelta",
        "caseCount",
        "matrixFamilies",
        "matrixShapes",
        "inputShapes",
        "outputShapes",
        "realCaseCount",
        "complexCaseCount",
        "bestCase",
        "worstCase",
        "modelCount",
        "portfolioFixtures",
        "bestSimulationCandidate",
        "worstSimulationCandidate",
        "generatedManifestValid",
        "pyTorchHardDependency",
        "adapterProtocolVersion",
        "modelId",
        "layerCount",
        "linearLayerCount",
        "classicalActivationCount",
        "opticalNonlinearityImplemented",
        "outputRelativeError",
        "outputRelativeErrorMax",
        "cumulativeError",
        "cumulativeErrorMax",
        "worstModelByOutputError",
        "worstLayerByError",
        "errorsCompoundAcrossLayers",
        "eligibleLayerCount",
        "ineligibleLayerCount",
        "classicalLayerCount",
        "totalLayerCount",
        "mappableLayerCount",
        "unsupportedLayerCount",
        "mappableLinearLayerShare",
        "mappableParameterShare",
        "rectangularLayerShare",
        "complexLayerShare",
        "modelSuitabilityScore",
        "suitabilityClass",
        "eligibleLinearLayerCount",
        "eligibleRectangularLayerCount",
        "eligibleComplexLayerCount",
        "classicalOnlyLayerCount",
        "hashValidationPassed",
        "pathValidationPassed",
        "unsupportedLayerTypes",
        "sizeRange",
        "shapeFamilies",
        "largestCaseId",
        "maxMeshConstrainedError",
        "releaseCandidateFor",
        "completedSimulationStageCount",
        "supplementalReportCount",
        "reportCount",
        "blockedHardwareGateCount",
        "noHardwarePerformanceClaim",
        "phaseBitsValues",
        "paretoCandidateCount",
        "bestErrorCandidate",
        "worstErrorCandidate",
        "syntheticFixtureOnly",
        "publicMeasuredEvidence",
        "measurementDataClaimed",
        "validationPassed",
        "scenarioCount",
        "parametricEstimateOnly",
        "measuredHardwarePerformance",
        "bestLatencyScenario",
        "worstLatencyScenario",
        "bestEnergyScenario",
        "worstEnergyScenario",
        "targetOutputRelativeErrorValues",
        "simulationDerivedOnly",
        "metRequirementCount",
        "unmetRequirementCount",
        "budgetId",
        "combinedErrorEnvelope",
        "dominantErrorContributor",
        "secondaryErrorContributor",
        "simulationOnly",
        "physicalAccuracyClaimed",
        "calibrationPlanOnly",
        "assimilationPlanOnly",
        "measurementVectorCount",
        "acceptanceCriteriaCount",
        "decision",
        "decisionIsNotHardwareValidation",
        "suitabilityScore",
        "includedCapabilityCount",
        "decisionReportCapabilityCount",
        "v02RoadmapItemCount",
        "complexValuedSupportImplemented",
        "unitaryFactorSupportImplemented",
        "complexSvdImplemented",
        "unitaryFactorization",
        "phaseAwareErrorMax",
        "amplitudeErrorMax",
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


def _report_by_id(reports: Iterable[Dict[str, Any]], report_id: str) -> Dict[str, Any]:
    for report in reports:
        if report["id"] == report_id:
            return report
    raise KeyError(report_id)


def _render_v02_roadmap() -> str:
    return "\n".join([
        "# v0.2 Roadmap",
        "",
        "This roadmap keeps the project simulation-only unless real external evidence is supplied.",
        "Stage 5, Stage 6, and Stage 7 remain blocked by default.",
        "",
        "## Recommended Work",
        "",
        "- expand the model portfolio beyond deterministic fixtures",
        "- add richer optional PyTorch export adapter examples while keeping framework dependencies optional",
        "- improve design-space objective functions with measured data only when real evidence exists",
        "- keep synthetic transfer-matrix ingestion sandbox separate from Stage 6 public evidence",
        "- extend the static dashboard with report filtering",
        "- strengthen synthetic calibration models with explicit limitations",
        "- add foundry or PDK integration only with real external evidence",
        "",
        "## Claim Boundary",
        "",
        "This roadmap does not claim hardware validation, foundry calibration, measured transfer matrices, "
        "production inference readiness, quantum advantage, hardware-native intelligence, or power-free computation.",
        "",
    ])


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _write_artifact_hashes(paths: Iterable[Path], output_path: Path) -> None:
    lines = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rel = path.relative_to(ROOT)
        lines.append(f"{digest}  {rel}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
