import json
import unittest
from pathlib import Path

from oqp.future_work.model_export_adapter import (
    render_model_export_adapter_protocol,
    run_model_export_adapter_demo_report,
    run_model_export_adapter_validation_report,
)
from oqp.future_work.validation_gates import foundry_calibration_gate, hardware_benchmark_gate, measured_transfer_matrix_gate


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "future-work" / "hrm-neural-mapping"


class HrmModelExportAdapterTest(unittest.TestCase):
    def test_export_adapter_reports_are_deterministic(self):
        self.assertEqual(run_model_export_adapter_demo_report(), run_model_export_adapter_demo_report())
        validation = run_model_export_adapter_validation_report()
        self.assertTrue(validation["generatedManifestValid"])
        self.assertFalse(validation["pyTorchHardDependency"])
        self.assertEqual(validation["unsupportedLayerTypes"], [])
        self.assertFalse(validation["hardwareValidated"])

    def test_protocol_and_example_are_present(self):
        protocol = render_model_export_adapter_protocol()
        self.assertIn("PyTorch is not a required dependency", protocol)
        self.assertIn("not hardware evidence", protocol)
        example = json.loads((ROOT / "fixtures" / "model-export-adapter" / "tiny-linear-export-example.json").read_text(encoding="utf-8"))
        self.assertEqual(example["exportAdapterVersion"], "model-export-adapter.v1")

    def test_generated_reports_are_hash_covered(self):
        artifacts = (REPORT_DIR / "ARTIFACTS.sha256").read_text(encoding="utf-8")
        for filename in ["model-export-adapter-demo.json", "model-export-adapter-validation.json"]:
            report = json.loads((REPORT_DIR / filename).read_text(encoding="utf-8"))
            json.dumps(report, sort_keys=True)
            self.assertFalse(report["hardwareValidated"])
            self.assertIn(f"reports/future-work/hrm-neural-mapping/{filename}", artifacts)
        self.assertIn("docs/future-work/model-export-adapter-protocol.md", artifacts)
        self.assertIn("fixtures/model-export-adapter/tiny-linear-export-example.json", artifacts)

    def test_hardware_gates_remain_blocked(self):
        reports = [foundry_calibration_gate(None), measured_transfer_matrix_gate(None), hardware_benchmark_gate(None)]
        self.assertEqual([report["stageStatus"] for report in reports], ["blocked", "blocked", "blocked"])


if __name__ == "__main__":
    unittest.main()
