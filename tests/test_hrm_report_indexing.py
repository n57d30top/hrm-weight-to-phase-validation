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

    def test_readme_rectangular_support_is_current(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(readme.split())
        self.assertIn("rectangular-matrix-support.json", normalized)
        self.assertIn("complex-unitary-mesh-support.json", normalized)
        self.assertIn("matrix-family-benchmark.json", normalized)
        self.assertIn("matrix-family-analysis.json", normalized)
        self.assertIn("layer-stack-inference-demo.json", normalized)
        self.assertIn("layer-stack-error-analysis.json", normalized)
        self.assertIn("supplemental rectangular support exists", normalized)
        self.assertIn("physical complex/unitary mesh layout", normalized)
        self.assertIn("ReLU remains a classical activation outside the optical mesh", normalized)
        self.assertIn("still no hardware validation", normalized)
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
