import json
import math
import unittest

from oqp.future_work.layer_stack_inference import (
    deterministic_layer_stack_models,
    run_layer_stack_error_analysis_report,
    run_layer_stack_inference_demo_report,
)
from oqp.future_work.validation_gates import (
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
)


class HrmLayerStackInferenceTest(unittest.TestCase):
    def test_toy_models_are_deterministic(self):
        models = deterministic_layer_stack_models()
        self.assertEqual([model.model_id for model in models], ["tiny_mlp_4_6_3", "projection_chain_4_8_4"])
        first = run_layer_stack_inference_demo_report(phase_levels=64)
        second = run_layer_stack_inference_demo_report(phase_levels=64)
        self.assertEqual(first, second)

    def test_inference_demo_report_schema_and_claim_flags(self):
        report = run_layer_stack_inference_demo_report(phase_levels=64)
        json.dumps(report, sort_keys=True)
        self.assertEqual(report["id"], "layer-stack-inference-demo")
        self.assertEqual(report["stage"], 2)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertEqual(report["evidenceLevel"], "abstract_layer_stack_inference_simulation")
        self.assertEqual(report["modelId"], "tiny_mlp_4_6_3")
        self.assertEqual(report["modelCount"], 2)
        self.assertEqual(report["layerCount"], 3)
        self.assertEqual(report["linearLayerCount"], 2)
        self.assertEqual(report["classicalActivationCount"], 1)
        self.assertFalse(report["opticalNonlinearityImplemented"])
        self.assertEqual(len(report["baselineOutput"]), 3)
        self.assertEqual(len(report["mappedOutput"]), 3)
        self.assertTrue(math.isfinite(report["outputRelativeError"]))
        self.assertEqual(report["outputRelativeError"], report["cumulativeError"])
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["foundryCalibrated"])
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["productionInferenceReady"])

    def test_layer_wise_errors_and_classical_relu_boundary(self):
        report = run_layer_stack_inference_demo_report(phase_levels=64)
        for model in report["models"]:
            layer_errors = model["layerWiseErrors"]
            self.assertEqual([row["layerId"] for row in layer_errors], ["linear_1", "relu_1", "linear_2"])
            self.assertEqual([row["hrmMapped"] for row in layer_errors], [True, False, True])
            relu = layer_errors[1]
            self.assertEqual(relu["layerType"], "classical_relu")
            self.assertTrue(relu["classicalActivation"])
            self.assertFalse(relu["opticalNonlinearityImplemented"])
            self.assertEqual(relu["mappingMode"], "classical_relu_outside_optical_mesh")
            self.assertIsNone(relu["weightRelativeError"])
            for row in layer_errors:
                self.assertTrue(math.isfinite(row["relativeError"]))
                self.assertFalse(row["hardwareValidated"])
                self.assertFalse(row["foundryCalibrated"])
                self.assertFalse(row["measuredTransferMatrixAvailable"])
                self.assertFalse(row["productionInferenceReady"])

    def test_error_analysis_matches_demo_report(self):
        demo = run_layer_stack_inference_demo_report(phase_levels=64)
        analysis = run_layer_stack_error_analysis_report(phase_levels=64)
        all_layers = [
            layer | {"modelId": model["modelId"]}
            for model in demo["models"]
            for layer in model["layerWiseErrors"]
        ]
        worst_layer = max(all_layers, key=lambda row: row["relativeError"])
        worst_model = max(demo["models"], key=lambda row: row["outputRelativeError"])
        self.assertEqual(analysis["id"], "layer-stack-error-analysis")
        self.assertEqual(analysis["modelCount"], demo["modelCount"])
        self.assertEqual(analysis["worstLayerByError"]["modelId"], worst_layer["modelId"])
        self.assertEqual(analysis["worstLayerByError"]["layerId"], worst_layer["layerId"])
        self.assertEqual(analysis["worstModelByOutputError"]["modelId"], worst_model["modelId"])
        self.assertIn("cumulativeErrorTrend", analysis)
        self.assertIn("activationBoundaryNotes", analysis)
        self.assertFalse(analysis["hardwareValidated"])
        self.assertFalse(analysis["foundryCalibrated"])
        self.assertFalse(analysis["measuredTransferMatrixAvailable"])
        self.assertFalse(analysis["productionInferenceReady"])

    def test_hardware_evidence_gates_remain_blocked(self):
        self.assertEqual(foundry_calibration_gate(None)["stageStatus"], "blocked")
        self.assertEqual(measured_transfer_matrix_gate(None)["stageStatus"], "blocked")
        self.assertEqual(hardware_benchmark_gate(None)["stageStatus"], "blocked")


if __name__ == "__main__":
    unittest.main()
