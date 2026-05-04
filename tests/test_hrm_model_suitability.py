import copy
import json
import tempfile
import unittest
from pathlib import Path

from oqp.future_work.model_suitability import (
    profile_model_suitability,
    run_model_suitability_analysis_report,
    run_model_suitability_profile_report,
)
from oqp.future_work.model_weight_manifest import DEFAULT_MANIFEST
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmModelSuitabilityTest(unittest.TestCase):
    def test_profile_counts_fixture_components(self):
        profile = profile_model_suitability(DEFAULT_MANIFEST)
        self.assertEqual(profile["modelId"], "tiny_mlp_manifest_4_6_3")
        self.assertEqual(profile["totalLayerCount"], 5)
        self.assertEqual(profile["mappableLayerCount"], 2)
        self.assertEqual(profile["classicalLayerCount"], 3)
        self.assertEqual(profile["unsupportedLayerCount"], 0)
        self.assertEqual(profile["mappableParameterShare"], 0.823529411765)
        self.assertEqual(profile["rectangularLayerShare"], 1.0)
        self.assertEqual(profile["complexLayerShare"], 0.0)
        self.assertEqual(profile["suitabilityClass"], "good_candidate")
        self.assertGreaterEqual(profile["modelSuitabilityScore"], 0.0)
        self.assertLessEqual(profile["modelSuitabilityScore"], 100.0)

    def test_profile_classifies_bias_and_activation_as_classical(self):
        profile = profile_model_suitability(DEFAULT_MANIFEST)
        classifications = {row["componentId"]: row["classification"] for row in profile["layerClassification"]}
        self.assertEqual(classifications["linear_1.weight"], "optically_mappable_rectangular_linear")
        self.assertEqual(classifications["linear_1.bias"], "classical_bias")
        self.assertEqual(classifications["linear_1.activation"], "classical_activation")
        self.assertEqual(classifications["linear_2.weight"], "optically_mappable_rectangular_linear")
        self.assertEqual(classifications["linear_2.bias"], "classical_bias")

    def test_unsupported_layers_are_counted(self):
        manifest = self._manifest_copy()
        manifest["layerList"][0]["layerType"] = "convolution"
        manifest["layerList"][0]["mappingEligible"] = False
        profile = profile_model_suitability(self._write_temp_manifest(manifest))
        self.assertEqual(profile["mappableLayerCount"], 1)
        self.assertEqual(profile["unsupportedLayerCount"], 1)
        self.assertEqual(profile["unsupportedReasonCounts"], {
            "convolution mapping is not implemented": 1,
        })
        classifications = {row["componentId"]: row["classification"] for row in profile["layerClassification"]}
        self.assertEqual(classifications["linear_1.weight"], "unsupported_convolution")

    def test_profile_report_schema_and_claim_flags(self):
        report = run_model_suitability_profile_report()
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["id"], "model-suitability-profile")
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "model_suitability_profile_simulation")
        self.assertEqual(report["mappableLayerCount"], 2)
        self.assertEqual(report["classicalLayerCount"], 3)
        self.assertEqual(report["unsupportedLayerCount"], 0)
        self.assertEqual(report["scoreLabels"]["modelSuitabilityScore"], "heuristic_simulation_only_not_hardware_validated")
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])
        for row in report["layerClassification"]:
            self.assertFalse(row["hardwareValidated"])
            self.assertFalse(row["foundryCalibrated"])
            self.assertFalse(row["measuredTransferMatrixAvailable"])
            self.assertFalse(row["productionInferenceReady"])

    def test_analysis_report_is_deterministic(self):
        first = run_model_suitability_analysis_report()
        second = run_model_suitability_analysis_report()
        self.assertEqual(first, second)
        json.dumps(first, sort_keys=True)
        self.assertEqual(first["id"], "model-suitability-analysis")
        self.assertEqual(first["modelId"], "tiny_mlp_manifest_4_6_3")
        self.assertEqual(len(first["topMappableLayers"]), 2)
        self.assertEqual(first["topUnsupportedLayers"], [])
        self.assertIn("most fixture parameters are in mappable linear weights", first["suitabilityDrivers"])
        self.assertFalse(first["hardwareValidated"])
        self.assertFalse(first["foundryCalibrated"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertFalse(first["productionInferenceReady"])

    def test_generated_reports_are_hash_covered(self):
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        self.assertIn("reports/future-work/hrm-neural-mapping/model-suitability-profile.json", artifacts)
        self.assertIn("reports/future-work/hrm-neural-mapping/model-suitability-analysis.json", artifacts)

    def test_hardware_evidence_gates_remain_blocked(self):
        self.assertEqual(foundry_calibration_gate(None)["stageStatus"], "blocked")
        self.assertEqual(measured_transfer_matrix_gate(None)["stageStatus"], "blocked")
        self.assertEqual(hardware_benchmark_gate(None)["stageStatus"], "blocked")

    def _manifest_copy(self) -> dict:
        return copy.deepcopy(json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8")))

    def _write_temp_manifest(self, manifest: dict) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        path = Path(tempdir.name) / "tiny-mlp-manifest.json"
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
