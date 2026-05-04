import json
import unittest
from pathlib import Path

from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmReportIndexingTest(unittest.TestCase):
    def test_validation_summary_includes_rectangular_support(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("rectangular-matrix-support", reports)
        report = reports["rectangular-matrix-support"]
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_rectangular_mesh_simulation")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertEqual(report["keyMetrics"]["caseCount"], 3)
        self.assertEqual(report["keyMetrics"]["matrixShapes"], [[6, 4], [4, 6], [5, 3]])
        self.assertIn("meshConstrainedReconstructionErrorMax", report["keyMetrics"])
        self.assertIn("errorDeltaMax", report["keyMetrics"])
        self.assertTrue(report["keyMetrics"]["rectangularLayerSupportImplemented"])
        self.assertEqual(report["keyMetrics"]["rectangularMode"], "orthogonal_completion_rectangular_sigma")

    def test_validation_summary_includes_complex_unitary_support(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("complex-unitary-mesh-support", reports)
        report = reports["complex-unitary-mesh-support"]
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_complex_unitary_mesh_simulation")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertTrue(report["keyMetrics"]["complexValuedSupportImplemented"])
        self.assertTrue(report["keyMetrics"]["unitaryFactorSupportImplemented"])
        self.assertFalse(report["keyMetrics"]["complexSvdImplemented"])
        self.assertIn("phaseAwareErrorMax", report["keyMetrics"])
        self.assertIn("amplitudeErrorMax", report["keyMetrics"])

    def test_validation_summary_includes_matrix_family_reports(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("matrix-family-benchmark", reports)
        self.assertIn("matrix-family-analysis", reports)
        benchmark = reports["matrix-family-benchmark"]
        analysis = reports["matrix-family-analysis"]
        self.assertEqual(benchmark["stage"], 2)
        self.assertEqual(benchmark["stageStatus"], "complete")
        self.assertEqual(benchmark["evidenceLevel"], "abstract_matrix_family_benchmark_simulation")
        self.assertEqual(benchmark["keyMetrics"]["caseCount"], 11)
        self.assertIn("matrixFamilies", benchmark["keyMetrics"])
        self.assertEqual(benchmark["keyMetrics"]["realCaseCount"], 9)
        self.assertEqual(benchmark["keyMetrics"]["complexCaseCount"], 2)
        self.assertFalse(benchmark["hardwareValidated"])
        self.assertFalse(benchmark["foundryCalibrated"])
        self.assertFalse(benchmark["measuredTransferMatrixAvailable"])
        self.assertFalse(benchmark["productionInferenceReady"])
        self.assertEqual(analysis["stage"], 2)
        self.assertEqual(analysis["stageStatus"], "complete")
        self.assertEqual(analysis["evidenceLevel"], "abstract_matrix_family_analysis")
        self.assertEqual(analysis["keyMetrics"]["caseCount"], 11)
        self.assertIn("averageMeshConstrainedError", analysis["keyMetrics"])
        self.assertIn("maxErrorDelta", analysis["keyMetrics"])
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])

    def test_validation_summary_includes_layer_stack_reports(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("layer-stack-inference-demo", reports)
        self.assertIn("layer-stack-error-analysis", reports)
        demo = reports["layer-stack-inference-demo"]
        analysis = reports["layer-stack-error-analysis"]
        self.assertEqual(demo["stage"], 2)
        self.assertEqual(demo["stageStatus"], "complete")
        self.assertEqual(demo["evidenceLevel"], "abstract_layer_stack_inference_simulation")
        self.assertEqual(demo["keyMetrics"]["modelCount"], 2)
        self.assertEqual(demo["keyMetrics"]["linearLayerCount"], 2)
        self.assertEqual(demo["keyMetrics"]["classicalActivationCount"], 1)
        self.assertFalse(demo["keyMetrics"]["opticalNonlinearityImplemented"])
        self.assertIn("outputRelativeError", demo["keyMetrics"])
        self.assertIn("cumulativeError", demo["keyMetrics"])
        self.assertFalse(demo["hardwareValidated"])
        self.assertFalse(demo["foundryCalibrated"])
        self.assertFalse(demo["measuredTransferMatrixAvailable"])
        self.assertFalse(demo["productionInferenceReady"])
        self.assertEqual(analysis["stage"], 2)
        self.assertEqual(analysis["stageStatus"], "complete")
        self.assertEqual(analysis["evidenceLevel"], "abstract_layer_stack_error_analysis")
        self.assertEqual(analysis["keyMetrics"]["modelCount"], 2)
        self.assertIn("worstLayerByError", analysis["keyMetrics"])
        self.assertIn("errorsCompoundAcrossLayers", analysis["keyMetrics"])
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])

    def test_validation_summary_includes_model_weight_reports(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("model-weight-import-demo", reports)
        self.assertIn("model-weight-eligibility-analysis", reports)
        imported = reports["model-weight-import-demo"]
        analysis = reports["model-weight-eligibility-analysis"]
        self.assertEqual(imported["stage"], 2)
        self.assertEqual(imported["stageStatus"], "complete")
        self.assertEqual(imported["evidenceLevel"], "model_weight_manifest_import_simulation")
        self.assertEqual(imported["keyMetrics"]["modelId"], "tiny_mlp_manifest_4_6_3")
        self.assertEqual(imported["keyMetrics"]["eligibleLayerCount"], 2)
        self.assertEqual(imported["keyMetrics"]["classicalLayerCount"], 3)
        self.assertTrue(imported["keyMetrics"]["hashValidationPassed"])
        self.assertTrue(imported["keyMetrics"]["pathValidationPassed"])
        self.assertFalse(imported["hardwareValidated"])
        self.assertFalse(imported["foundryCalibrated"])
        self.assertFalse(imported["measuredTransferMatrixAvailable"])
        self.assertFalse(imported["productionInferenceReady"])
        self.assertEqual(analysis["stage"], 2)
        self.assertEqual(analysis["stageStatus"], "complete")
        self.assertEqual(analysis["evidenceLevel"], "model_weight_manifest_eligibility_analysis")
        self.assertEqual(analysis["keyMetrics"]["eligibleRectangularLayerCount"], 2)
        self.assertEqual(analysis["keyMetrics"]["eligibleComplexLayerCount"], 0)
        self.assertEqual(analysis["keyMetrics"]["ineligibleLayerCount"], 0)
        self.assertEqual(analysis["keyMetrics"]["unsupportedLayerTypes"], [])
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])

    def test_validation_summary_includes_model_suitability_reports(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("model-suitability-profile", reports)
        self.assertIn("model-suitability-analysis", reports)
        profile = reports["model-suitability-profile"]
        analysis = reports["model-suitability-analysis"]
        self.assertEqual(profile["stage"], 2)
        self.assertEqual(profile["stageStatus"], "complete")
        self.assertEqual(profile["evidenceLevel"], "model_suitability_profile_simulation")
        self.assertEqual(profile["keyMetrics"]["modelSuitabilityScore"], 87.647)
        self.assertEqual(profile["keyMetrics"]["suitabilityClass"], "good_candidate")
        self.assertEqual(profile["keyMetrics"]["mappableLayerCount"], 2)
        self.assertEqual(profile["keyMetrics"]["classicalLayerCount"], 3)
        self.assertEqual(profile["keyMetrics"]["unsupportedLayerCount"], 0)
        self.assertFalse(profile["hardwareValidated"])
        self.assertFalse(profile["foundryCalibrated"])
        self.assertFalse(profile["measuredTransferMatrixAvailable"])
        self.assertFalse(profile["productionInferenceReady"])
        self.assertEqual(analysis["stage"], 2)
        self.assertEqual(analysis["stageStatus"], "complete")
        self.assertEqual(analysis["evidenceLevel"], "model_suitability_analysis")
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])

    def test_validation_summary_includes_scaling_reports(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("scaling-benchmark", reports)
        self.assertIn("scaling-analysis", reports)
        benchmark = reports["scaling-benchmark"]
        analysis = reports["scaling-analysis"]
        self.assertEqual(benchmark["stage"], 2)
        self.assertEqual(benchmark["stageStatus"], "complete")
        self.assertEqual(benchmark["evidenceLevel"], "abstract_scaling_benchmark_simulation")
        self.assertEqual(benchmark["keyMetrics"]["caseCount"], 11)
        self.assertIn("sizeRange", benchmark["keyMetrics"])
        self.assertIn("largestCaseId", benchmark["keyMetrics"])
        self.assertTrue(benchmark["keyMetrics"]["noHardwarePerformanceClaim"])
        self.assertFalse(benchmark["hardwareValidated"])
        self.assertFalse(benchmark["foundryCalibrated"])
        self.assertFalse(benchmark["measuredTransferMatrixAvailable"])
        self.assertFalse(benchmark["productionInferenceReady"])
        self.assertEqual(analysis["stage"], 2)
        self.assertEqual(analysis["stageStatus"], "complete")
        self.assertEqual(analysis["evidenceLevel"], "abstract_scaling_analysis")
        self.assertEqual(analysis["keyMetrics"]["caseCount"], 11)
        self.assertIn("averageMeshConstrainedError", analysis["keyMetrics"])
        self.assertIn("maxMeshConstrainedError", analysis["keyMetrics"])
        self.assertTrue(analysis["keyMetrics"]["noHardwarePerformanceClaim"])
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])

    def test_validation_summary_includes_planning_reports(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        expected = {
            "hardware-scenario-estimates": "parametric_hardware_scenario_estimate",
            "hardware-scenario-analysis": "parametric_hardware_scenario_analysis",
            "hardware-requirements-envelope": "simulation_derived_hardware_requirements",
            "hardware-requirements-analysis": "simulation_derived_hardware_requirements_analysis",
            "error-budget-report": "simulation_error_budget",
            "calibration-plan": "calibration_plan_only",
            "transfer-matrix-assimilation-plan": "transfer_matrix_assimilation_plan_only",
            "model-to-hrm-decision-report": "simulation_only_model_to_hrm_decision",
            "model-portfolio-benchmark": "model_portfolio_benchmark_simulation",
            "model-portfolio-ranking": "model_portfolio_ranking_simulation",
            "model-export-adapter-demo": "model_export_adapter_protocol",
            "model-export-adapter-validation": "model_export_adapter_validation",
            "hardware-design-space-sweep": "hardware_design_space_sweep_simulation",
            "hardware-design-space-analysis": "hardware_design_space_analysis",
            "transfer-matrix-ingestion-sandbox": "synthetic_transfer_matrix_ingestion_sandbox",
            "v0.1.0-rc1-readiness": "v0.1.0_rc1_readiness_audit",
        }
        for report_id, evidence_level in expected.items():
            self.assertIn(report_id, reports)
            report = reports[report_id]
            self.assertEqual(report["evidenceLevel"], evidence_level)
            self.assertFalse(report["hardwareValidated"])
            self.assertFalse(report["foundryCalibrated"])
            self.assertFalse(report["measuredTransferMatrixAvailable"])
            self.assertFalse(report["productionInferenceReady"])
        self.assertTrue(reports["hardware-scenario-estimates"]["keyMetrics"]["parametricEstimateOnly"])
        self.assertFalse(reports["hardware-scenario-estimates"]["keyMetrics"]["measuredHardwarePerformance"])
        self.assertTrue(reports["hardware-requirements-envelope"]["keyMetrics"]["simulationDerivedOnly"])
        self.assertTrue(reports["error-budget-report"]["keyMetrics"]["simulationOnly"])
        self.assertFalse(reports["error-budget-report"]["keyMetrics"]["physicalAccuracyClaimed"])
        self.assertTrue(reports["model-to-hrm-decision-report"]["keyMetrics"]["decisionIsNotHardwareValidation"])
        self.assertFalse(reports["model-export-adapter-demo"]["keyMetrics"]["pyTorchHardDependency"])
        self.assertTrue(reports["model-export-adapter-validation"]["keyMetrics"]["generatedManifestValid"])
        self.assertGreater(reports["hardware-design-space-analysis"]["keyMetrics"]["paretoCandidateCount"], 0)
        self.assertTrue(reports["transfer-matrix-ingestion-sandbox"]["keyMetrics"]["syntheticFixtureOnly"])

    def test_validation_summary_includes_review_pack(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("review-pack-summary", reports)
        report = reports["review-pack-summary"]
        self.assertEqual(report["stage"], 0)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "simulation_review_pack")
        self.assertIn("reportCount", report["keyMetrics"])
        self.assertEqual(report["keyMetrics"]["blockedHardwareGateCount"], 3)
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])

    def test_validation_summary_includes_release_readiness(self):
        summary = json.loads((REPORT_DIR / "validation-ladder-summary.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in summary["supplementalReports"]
        }
        self.assertIn("release-readiness-v0.1.0", reports)
        report = reports["release-readiness-v0.1.0"]
        self.assertEqual(report["stage"], 0)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "release_candidate_hardening_audit")
        self.assertEqual(report["keyMetrics"]["releaseCandidateFor"], "v0.1.0")
        self.assertEqual(report["keyMetrics"]["completedSimulationStageCount"], 5)
        self.assertEqual(report["keyMetrics"]["blockedHardwareGateCount"], 3)
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])

    def test_evidence_ledger_includes_rectangular_support(self):
        ledger = json.loads((ROOT / "docs" / "future-work" / "evidence-ledger.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in ledger["entries"]
        }
        self.assertIn("rectangular-matrix-support", reports)
        report = reports["rectangular-matrix-support"]
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_rectangular_mesh_simulation")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertIn("complex-unitary-mesh-support", reports)
        complex_report = reports["complex-unitary-mesh-support"]
        self.assertEqual(complex_report["stage"], 2)
        self.assertEqual(complex_report["stageStatus"], "complete")
        self.assertEqual(complex_report["evidenceLevel"], "abstract_complex_unitary_mesh_simulation")
        self.assertFalse(complex_report["hardwareValidated"])
        self.assertFalse(complex_report["foundryCalibrated"])
        self.assertFalse(complex_report["measuredTransferMatrixAvailable"])
        self.assertFalse(complex_report["productionInferenceReady"])
        self.assertIn("matrix-family-benchmark", reports)
        benchmark_report = reports["matrix-family-benchmark"]
        self.assertEqual(benchmark_report["stage"], 2)
        self.assertEqual(benchmark_report["stageStatus"], "complete")
        self.assertEqual(benchmark_report["evidenceLevel"], "abstract_matrix_family_benchmark_simulation")
        self.assertFalse(benchmark_report["hardwareValidated"])
        self.assertFalse(benchmark_report["foundryCalibrated"])
        self.assertFalse(benchmark_report["measuredTransferMatrixAvailable"])
        self.assertFalse(benchmark_report["productionInferenceReady"])
        self.assertIn("matrix-family-analysis", reports)
        analysis_report = reports["matrix-family-analysis"]
        self.assertEqual(analysis_report["stage"], 2)
        self.assertEqual(analysis_report["stageStatus"], "complete")
        self.assertEqual(analysis_report["evidenceLevel"], "abstract_matrix_family_analysis")
        self.assertFalse(analysis_report["hardwareValidated"])
        self.assertFalse(analysis_report["foundryCalibrated"])
        self.assertFalse(analysis_report["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis_report["productionInferenceReady"])
        self.assertIn("layer-stack-inference-demo", reports)
        layer_stack_report = reports["layer-stack-inference-demo"]
        self.assertEqual(layer_stack_report["stage"], 2)
        self.assertEqual(layer_stack_report["stageStatus"], "complete")
        self.assertEqual(layer_stack_report["evidenceLevel"], "abstract_layer_stack_inference_simulation")
        self.assertFalse(layer_stack_report["hardwareValidated"])
        self.assertFalse(layer_stack_report["foundryCalibrated"])
        self.assertFalse(layer_stack_report["measuredTransferMatrixAvailable"])
        self.assertFalse(layer_stack_report["productionInferenceReady"])
        self.assertIn("layer-stack-error-analysis", reports)
        layer_stack_analysis = reports["layer-stack-error-analysis"]
        self.assertEqual(layer_stack_analysis["stage"], 2)
        self.assertEqual(layer_stack_analysis["stageStatus"], "complete")
        self.assertEqual(layer_stack_analysis["evidenceLevel"], "abstract_layer_stack_error_analysis")
        self.assertFalse(layer_stack_analysis["hardwareValidated"])
        self.assertFalse(layer_stack_analysis["foundryCalibrated"])
        self.assertFalse(layer_stack_analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(layer_stack_analysis["productionInferenceReady"])
        self.assertIn("model-weight-import-demo", reports)
        model_weight_report = reports["model-weight-import-demo"]
        self.assertEqual(model_weight_report["stage"], 2)
        self.assertEqual(model_weight_report["stageStatus"], "complete")
        self.assertEqual(model_weight_report["evidenceLevel"], "model_weight_manifest_import_simulation")
        self.assertFalse(model_weight_report["hardwareValidated"])
        self.assertFalse(model_weight_report["foundryCalibrated"])
        self.assertFalse(model_weight_report["measuredTransferMatrixAvailable"])
        self.assertFalse(model_weight_report["productionInferenceReady"])
        self.assertIn("model-weight-eligibility-analysis", reports)
        model_weight_analysis = reports["model-weight-eligibility-analysis"]
        self.assertEqual(model_weight_analysis["stage"], 2)
        self.assertEqual(model_weight_analysis["stageStatus"], "complete")
        self.assertEqual(model_weight_analysis["evidenceLevel"], "model_weight_manifest_eligibility_analysis")
        self.assertFalse(model_weight_analysis["hardwareValidated"])
        self.assertFalse(model_weight_analysis["foundryCalibrated"])
        self.assertFalse(model_weight_analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(model_weight_analysis["productionInferenceReady"])
        self.assertIn("model-suitability-profile", reports)
        suitability_profile = reports["model-suitability-profile"]
        self.assertEqual(suitability_profile["stage"], 2)
        self.assertEqual(suitability_profile["stageStatus"], "complete")
        self.assertEqual(suitability_profile["evidenceLevel"], "model_suitability_profile_simulation")
        self.assertFalse(suitability_profile["hardwareValidated"])
        self.assertFalse(suitability_profile["foundryCalibrated"])
        self.assertFalse(suitability_profile["measuredTransferMatrixAvailable"])
        self.assertFalse(suitability_profile["productionInferenceReady"])
        self.assertIn("model-suitability-analysis", reports)
        suitability_analysis = reports["model-suitability-analysis"]
        self.assertEqual(suitability_analysis["stage"], 2)
        self.assertEqual(suitability_analysis["stageStatus"], "complete")
        self.assertEqual(suitability_analysis["evidenceLevel"], "model_suitability_analysis")
        self.assertFalse(suitability_analysis["hardwareValidated"])
        self.assertFalse(suitability_analysis["foundryCalibrated"])
        self.assertFalse(suitability_analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(suitability_analysis["productionInferenceReady"])
        self.assertIn("scaling-benchmark", reports)
        scaling_report = reports["scaling-benchmark"]
        self.assertEqual(scaling_report["stage"], 2)
        self.assertEqual(scaling_report["stageStatus"], "complete")
        self.assertEqual(scaling_report["evidenceLevel"], "abstract_scaling_benchmark_simulation")
        self.assertFalse(scaling_report["hardwareValidated"])
        self.assertFalse(scaling_report["foundryCalibrated"])
        self.assertFalse(scaling_report["measuredTransferMatrixAvailable"])
        self.assertFalse(scaling_report["productionInferenceReady"])
        self.assertIn("scaling-analysis", reports)
        scaling_analysis = reports["scaling-analysis"]
        self.assertEqual(scaling_analysis["stage"], 2)
        self.assertEqual(scaling_analysis["stageStatus"], "complete")
        self.assertEqual(scaling_analysis["evidenceLevel"], "abstract_scaling_analysis")
        self.assertFalse(scaling_analysis["hardwareValidated"])
        self.assertFalse(scaling_analysis["foundryCalibrated"])
        self.assertFalse(scaling_analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(scaling_analysis["productionInferenceReady"])
        for report_id in [
            "hardware-scenario-estimates",
            "hardware-scenario-analysis",
            "hardware-requirements-envelope",
            "hardware-requirements-analysis",
            "error-budget-report",
            "calibration-plan",
            "transfer-matrix-assimilation-plan",
            "model-to-hrm-decision-report",
            "model-portfolio-benchmark",
            "model-portfolio-ranking",
            "model-export-adapter-demo",
            "model-export-adapter-validation",
            "hardware-design-space-sweep",
            "hardware-design-space-analysis",
            "transfer-matrix-ingestion-sandbox",
            "v0.1.0-rc1-readiness",
        ]:
            self.assertIn(report_id, reports)
            report = reports[report_id]
            self.assertFalse(report["hardwareValidated"])
            self.assertFalse(report["foundryCalibrated"])
            self.assertFalse(report["measuredTransferMatrixAvailable"])
            self.assertFalse(report["productionInferenceReady"])

    def test_artifacts_sha256_covers_all_generated_json_reports(self):
        json_reports = {
            path.relative_to(ROOT).as_posix()
            for path in REPORT_DIR.glob("*.json")
            if path.is_file()
        }
        hashed_reports = set()
        for line in (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].endswith(".json"):
                hashed_reports.add(parts[1])
        self.assertEqual(json_reports - hashed_reports, set())
        self.assertIn("reports/future-work/hrm-neural-mapping/rectangular-matrix-support.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/complex-unitary-mesh-support.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/matrix-family-benchmark.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/matrix-family-analysis.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/layer-stack-inference-demo.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/layer-stack-error-analysis.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-weight-import-demo.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-weight-eligibility-analysis.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-suitability-profile.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-suitability-analysis.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/scaling-benchmark.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/scaling-analysis.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-scenario-estimates.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-scenario-analysis.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-requirements-envelope.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-requirements-analysis.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/error-budget-report.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/calibration-plan.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/transfer-matrix-assimilation-plan.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-to-hrm-decision-report.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-portfolio-benchmark.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-portfolio-ranking.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-export-adapter-demo.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-export-adapter-validation.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-design-space-sweep.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-design-space-analysis.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/transfer-matrix-ingestion-sandbox.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/v0.1.0-rc1-readiness.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/review-pack-summary.json", hashed_reports)
        self.assertIn("reports/future-work/hrm-neural-mapping/release-readiness-v0.1.0.json", hashed_reports)
        artifact_text = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("reports/future-work/hrm-neural-mapping/review-pack.md", artifact_text)
        self.assertIn("reports/future-work/hrm-neural-mapping/review-pack-metrics.csv", artifact_text)
        self.assertIn("reports/future-work/hrm-neural-mapping/release-readiness-v0.1.0.md", artifact_text)
        self.assertIn("reports/future-work/hrm-neural-mapping/error-budget-analysis.md", artifact_text)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-to-hrm-decision-report.md", artifact_text)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-portfolio-decision-summary.md", artifact_text)
        self.assertIn("reports/future-work/hrm-neural-mapping/hardware-design-space-pareto.md", artifact_text)
        self.assertIn("reports/future-work/hrm-neural-mapping/v0.1.0-rc1-readiness.md", artifact_text)
        self.assertIn("docs/future-work/transfer-matrix-assimilation-protocol.md", artifact_text)
        self.assertIn("docs/future-work/model-export-adapter-protocol.md", artifact_text)
        self.assertIn("docs/ROADMAP-v0.2.md", artifact_text)
        self.assertIn("docs/QUICKSTART.md", artifact_text)
        self.assertIn("docs/REVIEWER_GUIDE.md", artifact_text)
        self.assertIn("dashboard/index.html", artifact_text)
        self.assertIn("fixtures/model-export-adapter/tiny-linear-export-example.json", artifact_text)
        self.assertIn("fixtures/transfer-matrix-sandbox/synthetic-transfer-matrix.json", artifact_text)

    def test_evidence_ledger_includes_review_pack(self):
        ledger = json.loads((ROOT / "docs" / "future-work" / "evidence-ledger.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in ledger["entries"]
        }
        self.assertIn("review-pack-summary", reports)
        report = reports["review-pack-summary"]
        self.assertEqual(report["stage"], 0)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "simulation_review_pack")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])

    def test_evidence_ledger_includes_release_readiness(self):
        ledger = json.loads((ROOT / "docs" / "future-work" / "evidence-ledger.json").read_text(encoding="utf-8"))
        reports = {
            report["id"]: report
            for report in ledger["entries"]
        }
        self.assertIn("release-readiness-v0.1.0", reports)
        report = reports["release-readiness-v0.1.0"]
        self.assertEqual(report["stage"], 0)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "release_candidate_hardening_audit")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])

    def test_readme_rectangular_support_is_current(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(readme.split())
        self.assertIn("rectangular-matrix-support.json", normalized)
        self.assertIn("complex-unitary-mesh-support.json", normalized)
        self.assertIn("matrix-family-benchmark.json", normalized)
        self.assertIn("matrix-family-analysis.json", normalized)
        self.assertIn("layer-stack-inference-demo.json", normalized)
        self.assertIn("layer-stack-error-analysis.json", normalized)
        self.assertIn("model-weight-import-demo.json", normalized)
        self.assertIn("model-weight-eligibility-analysis.json", normalized)
        self.assertIn("model-weight-manifest-schema.md", normalized)
        self.assertIn("model-suitability-profile.json", normalized)
        self.assertIn("model-suitability-analysis.json", normalized)
        self.assertIn("scaling-benchmark.json", normalized)
        self.assertIn("scaling-analysis.json", normalized)
        self.assertIn("review-pack-summary.json", normalized)
        self.assertIn("review-pack.md", normalized)
        self.assertIn("review-pack-metrics.csv", normalized)
        self.assertIn("release-readiness-v0.1.0.json", normalized)
        self.assertIn("release-readiness-v0.1.0.md", normalized)
        self.assertIn("hardware-scenario-estimates.json", normalized)
        self.assertIn("hardware-scenario-analysis.json", normalized)
        self.assertIn("hardware-requirements-envelope.json", normalized)
        self.assertIn("hardware-requirements-analysis.json", normalized)
        self.assertIn("error-budget-report.json", normalized)
        self.assertIn("error-budget-analysis.md", normalized)
        self.assertIn("calibration-plan.json", normalized)
        self.assertIn("transfer-matrix-assimilation-plan.json", normalized)
        self.assertIn("transfer-matrix-assimilation-protocol.md", normalized)
        self.assertIn("model-to-hrm-decision-report.json", normalized)
        self.assertIn("model-to-hrm-decision-report.md", normalized)
        self.assertIn("model-portfolio-benchmark.json", normalized)
        self.assertIn("model-portfolio-ranking.json", normalized)
        self.assertIn("model-portfolio-decision-summary.md", normalized)
        self.assertIn("model-export-adapter-demo.json", normalized)
        self.assertIn("model-export-adapter-validation.json", normalized)
        self.assertIn("model-export-adapter-protocol.md", normalized)
        self.assertIn("hardware-design-space-sweep.json", normalized)
        self.assertIn("hardware-design-space-analysis.json", normalized)
        self.assertIn("hardware-design-space-pareto.md", normalized)
        self.assertIn("transfer-matrix-ingestion-sandbox.json", normalized)
        self.assertIn("dashboard/index.html", normalized)
        self.assertIn("v0.1.0-rc1-readiness.json", normalized)
        self.assertIn("v0.1.0-rc1-readiness.md", normalized)
        self.assertIn("ROADMAP-v0.2.md", normalized)
        self.assertIn("QUICKSTART.md", normalized)
        self.assertIn("REVIEWER_GUIDE.md", normalized)
        self.assertIn("v0.2.0-alpha.2", normalized)
        self.assertIn("supplemental rectangular support exists", normalized)
        self.assertIn("physical complex/unitary mesh layout", normalized)
        self.assertIn("ReLU remains a classical activation outside the optical mesh", normalized)
        self.assertIn("PyTorch is not a required dependency", readme)
        self.assertIn("heuristic simulation-only planning score", normalized)
        self.assertIn("not a hardware performance claim", normalized)
        self.assertIn("simulation-only review pack", normalized)
        self.assertIn("claim-boundary guard", normalized)
        self.assertIn("still no hardware validation", normalized)
        self.assertIn("parametric estimates, not measured hardware performance", normalized)
        self.assertIn("simulation-derived requirement envelope", normalized)
        self.assertIn("simulation-only decision report", normalized)
        self.assertNotIn("no rectangular neural layer support", normalized)
        self.assertNotIn("square matrix only", normalized)

    def test_hardware_evidence_gates_remain_blocked(self):
        reports = [
            foundry_calibration_gate(None),
            measured_transfer_matrix_gate(None),
            hardware_benchmark_gate(None),
        ]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])
        for report in reports:
            self.assertFalse(report["hardwareValidated"])
            self.assertFalse(report["foundryCalibrated"])
            self.assertFalse(report["measuredTransferMatrixAvailable"])
            self.assertFalse(report["productionInferenceReady"])


if __name__ == "__main__":
    unittest.main()
