import copy
import json
import tempfile
import unittest
from pathlib import Path

from oqp.future_work.model_weight_manifest import (
    DEFAULT_MANIFEST,
    ManifestValidationError,
    classify_layer_type,
    import_model_weight_manifest,
    run_model_weight_eligibility_analysis_report,
    run_model_weight_import_demo_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


ROOT = Path(__file__).resolve().parents[1]


class HrmModelWeightManifestTest(unittest.TestCase):
    def test_valid_tiny_mlp_manifest_imports(self):
        imported = import_model_weight_manifest(DEFAULT_MANIFEST)
        self.assertEqual(imported["manifest"]["modelId"], "tiny_mlp_manifest_4_6_3")
        self.assertEqual(imported["layerCount"], 2)
        self.assertEqual(imported["eligibleLayerCount"], 2)
        self.assertEqual(imported["eligibleRectangularLayerCount"], 2)
        self.assertEqual(imported["eligibleComplexLayerCount"], 0)
        self.assertEqual(imported["ineligibleLayerCount"], 0)
        self.assertEqual(imported["classicalLayerCount"], 3)
        self.assertEqual(len(imported["loadedWeightArtifacts"]), 4)
        self.assertEqual([row["layerId"] for row in imported["mappingPlan"]], ["linear_1", "linear_2"])

    def test_missing_required_fields_fail(self):
        manifest = self._manifest_copy()
        del manifest["modelId"]
        with self.assertRaises(ManifestValidationError) as context:
            import_model_weight_manifest(self._write_temp_manifest(manifest))
        self.assertIn("manifest.modelId", {error["field"] for error in context.exception.errors})

    def test_wrong_artifact_hash_fails(self):
        manifest = self._manifest_copy()
        manifest["layerList"][0]["weightArtifactSha256"] = "0" * 64
        with self.assertRaises(ManifestValidationError) as context:
            import_model_weight_manifest(self._write_temp_manifest(manifest))
        self.assertTrue(any(error["reason"] == "sha256 mismatch" for error in context.exception.errors))

    def test_absolute_artifact_paths_fail(self):
        manifest = self._manifest_copy()
        manifest["layerList"][0]["weightArtifactReference"] = "/tmp/tiny-mlp-w1.json"
        with self.assertRaises(ManifestValidationError) as context:
            import_model_weight_manifest(self._write_temp_manifest(manifest))
        self.assertTrue(any("repo-relative" in error["reason"] for error in context.exception.errors))

    def test_local_path_fragments_fail(self):
        manifest = self._manifest_copy()
        manifest["layerList"][0]["weightArtifactReference"] = "Desktop" + "/tiny-mlp-w1.json"
        with self.assertRaises(ManifestValidationError) as context:
            import_model_weight_manifest(self._write_temp_manifest(manifest))
        self.assertTrue(any("local path fragment" in error["reason"] for error in context.exception.errors))

    def test_layer_shape_validation_fails_on_mismatch(self):
        manifest = self._manifest_copy()
        manifest["layerList"][0]["shape"] = [4, 6]
        with self.assertRaises(ManifestValidationError) as context:
            import_model_weight_manifest(self._write_temp_manifest(manifest))
        self.assertTrue(any("shape does not match" in error["reason"] for error in context.exception.errors))

    def test_unsupported_layer_types_are_classified_ineligible(self):
        manifest = self._manifest_copy()
        manifest["layerList"][0]["layerType"] = "convolution"
        manifest["layerList"][0]["mappingEligible"] = False
        imported = import_model_weight_manifest(self._write_temp_manifest(manifest))
        self.assertEqual(imported["eligibleLayerCount"], 1)
        self.assertEqual(imported["ineligibleLayerCount"], 1)
        self.assertEqual(imported["unsupportedLayerTypes"], ["convolution"])
        self.assertEqual(classify_layer_type("attention_softmax")["classification"], "ineligible")
        self.assertEqual(classify_layer_type("embedding")["classification"], "ineligible")

    def test_bias_and_activation_are_classical_outside_optical_mesh(self):
        imported = import_model_weight_manifest(DEFAULT_MANIFEST)
        first = imported["eligibilityByLayer"][0]
        second = imported["eligibilityByLayer"][1]
        self.assertTrue(first["biasClassicalOutsideOpticalMesh"])
        self.assertTrue(first["activationClassicalOutsideOpticalMesh"])
        self.assertTrue(second["biasClassicalOutsideOpticalMesh"])
        self.assertFalse(second["activationClassicalOutsideOpticalMesh"])
        self.assertEqual(classify_layer_type("activation")["mappingMode"], "classical_outside_optical_mesh")
        self.assertEqual(classify_layer_type("bias")["mappingMode"], "classical_outside_optical_mesh")

    def test_import_report_is_deterministic_and_serializable(self):
        first = run_model_weight_import_demo_report()
        second = run_model_weight_import_demo_report()
        self.assertEqual(first, second)
        json.dumps(first, sort_keys=True)
        self.assertEqual(first["id"], "model-weight-import-demo")
        self.assertEqual(first["layerCount"], 2)
        self.assertEqual(first["eligibleLayerCount"], 2)
        self.assertEqual(first["ineligibleLayerCount"], 0)
        self.assertEqual(first["classicalLayerCount"], 3)
        self.assertTrue(first["hashValidationPassed"])
        self.assertTrue(first["pathValidationPassed"])
        self.assertFalse(first["hardwareValidated"])
        self.assertFalse(first["foundryCalibrated"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertFalse(first["productionInferenceReady"])

    def test_eligibility_analysis_is_deterministic_and_serializable(self):
        first = run_model_weight_eligibility_analysis_report()
        second = run_model_weight_eligibility_analysis_report()
        self.assertEqual(first, second)
        json.dumps(first, sort_keys=True)
        self.assertEqual(first["id"], "model-weight-eligibility-analysis")
        self.assertEqual(first["eligibleLinearLayerCount"], 0)
        self.assertEqual(first["eligibleRectangularLayerCount"], 2)
        self.assertEqual(first["eligibleComplexLayerCount"], 0)
        self.assertEqual(first["ineligibleLayerCount"], 0)
        self.assertEqual(first["classicalOnlyLayerCount"], 0)
        self.assertEqual(first["unsupportedLayerTypes"], [])
        self.assertFalse(first["hardwareValidated"])
        self.assertFalse(first["foundryCalibrated"])
        self.assertFalse(first["measuredTransferMatrixAvailable"])
        self.assertFalse(first["productionInferenceReady"])

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
