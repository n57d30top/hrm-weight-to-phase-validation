import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from oqp.future_work.validation_gates import (
    HARDWARE_BENCHMARK_REQUIRED_FIELDS,
    MEASURED_TRANSFER_MATRIX_REQUIRED_FIELDS,
    foundry_calibration_gate,
    hardware_benchmark_gate,
    measured_transfer_matrix_gate,
    stage_0_specification_gate,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HrmValidationGatesTest(unittest.TestCase):
    def test_foundry_gate_blocks_without_foundry_data(self):
        report = foundry_calibration_gate(None)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertFalse(report["foundryCalibrated"])
        self.assertEqual(report["blockerReason"], "no_foundry_calibrated_device_model")

    def test_measured_transfer_matrix_gate_blocks_without_measured_data(self):
        report = measured_transfer_matrix_gate(None)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertEqual(report["blockerReason"], "no_measured_hrm_transfer_matrix")
        self.assertIn("artifactId", report["missingEvidence"])
        self.assertIn("claimBoundary", report["missingEvidence"])
        self.assertEqual(report["invalidEvidence"], [])
        self.assertEqual(report["hashMismatches"], [])
        self.assertEqual(report["missingArtifactReferences"], [])

    def test_hardware_benchmark_gate_blocks_without_required_evidence(self):
        report = hardware_benchmark_gate(None)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertFalse(report["productionInferenceReady"])
        self.assertEqual(report["blockerReason"], "no_end_to_end_hardware_benchmark")
        self.assertIn("benchmarkId", report["missingEvidence"])
        self.assertIn("claimBoundary", report["missingEvidence"])
        self.assertEqual(report["blockedByDependency"], "stage_6_measured_transfer_matrix_gate_not_complete")

    def test_measured_transfer_matrix_schema_matches_future_fixture_doc_fields(self):
        expected = {
            "artifactId",
            "measurementDate",
            "deviceId",
            "setupDescription",
            "wavelength",
            "temperatureOrOperatingCondition",
            "matrixShape",
            "matrixConvention",
            "calibrationProcedure",
            "rawArtifactReference",
            "processedArtifactReference",
            "sha256Hash",
            "provenance",
            "uncertaintyOrErrorEstimate",
            "operatorOrSource",
            "claimBoundary",
        }
        self.assertEqual(set(MEASURED_TRANSFER_MATRIX_REQUIRED_FIELDS), expected)

    def test_hardware_benchmark_schema_matches_acceptance_doc_fields(self):
        expected = {
            "benchmarkId",
            "deviceId",
            "measuredTransferMatrixReference",
            "dataset",
            "softwareBaseline",
            "inputEncoding",
            "outputReadout",
            "controlPathCharacterization",
            "detectorReadoutCharacterization",
            "accuracyMetric",
            "latencyMetric",
            "energyMetric",
            "driftRecalibrationMetric",
            "environment",
            "rawResultsHash",
            "processedResultsHash",
            "provenance",
            "claimBoundary",
        }
        self.assertEqual(set(HARDWARE_BENCHMARK_REQUIRED_FIELDS), expected)

    def test_measured_transfer_matrix_manifest_with_missing_artifacts_blocks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "stage6-manifest.json"
            manifest_path.write_text(json.dumps(self._stage_6_manifest()), encoding="utf-8")
            report = measured_transfer_matrix_gate(manifest_path)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertEqual(report["missingEvidence"], [])
        self.assertGreaterEqual(len(report["missingArtifactReferences"]), 2)

    def test_measured_transfer_matrix_manifest_with_wrong_hash_blocks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "raw.json").write_text('{"raw": true}\n', encoding="utf-8")
            (root / "processed.json").write_text('{"matrix": [[1.0]]}\n', encoding="utf-8")
            manifest = self._stage_6_manifest(sha256_hash="0" * 64)
            manifest_path = root / "stage6-manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = measured_transfer_matrix_gate(manifest_path)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertFalse(report["measuredTransferMatrixAvailable"])
        self.assertEqual(report["missingArtifactReferences"], [])
        self.assertEqual(report["hashMismatches"][0]["field"], "sha256Hash")

    def test_measured_transfer_matrix_valid_fixture_can_pass_in_temp_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = self._write_valid_stage_6_fixture(Path(tmpdir))
            report = measured_transfer_matrix_gate(manifest_path)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertTrue(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["hardwareValidated"])
        self.assertEqual(report["missingEvidence"], [])
        self.assertEqual(report["invalidEvidence"], [])
        self.assertEqual(report["hashMismatches"], [])
        self.assertEqual(report["missingArtifactReferences"], [])

    def test_hardware_benchmark_manifest_with_missing_artifacts_blocks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "stage7-manifest.json"
            manifest_path.write_text(json.dumps(self._stage_7_manifest()), encoding="utf-8")
            report = hardware_benchmark_gate(manifest_path)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertGreaterEqual(len(report["missingArtifactReferences"]), 3)

    def test_hardware_benchmark_blocks_when_stage_6_dependency_is_not_complete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stage_6_manifest = self._write_valid_stage_6_fixture(root)
            stage_7_manifest = self._write_valid_stage_7_fixture(root, stage_6_manifest)
            incomplete_stage_6 = measured_transfer_matrix_gate(None)
            report = hardware_benchmark_gate(stage_7_manifest, measured_transfer_matrix_report=incomplete_stage_6)
        self.assertEqual(report["stageStatus"], "blocked")
        self.assertEqual(report["blockedByDependency"], "stage_6_measured_transfer_matrix_gate_not_complete")
        self.assertFalse(report["productionInferenceReady"])

    def test_hardware_benchmark_valid_fixture_can_pass_only_with_stage_6_dependency(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stage_6_manifest = self._write_valid_stage_6_fixture(root)
            stage_6_report = measured_transfer_matrix_gate(stage_6_manifest)
            stage_7_manifest = self._write_valid_stage_7_fixture(root, stage_6_manifest)
            report = hardware_benchmark_gate(stage_7_manifest, measured_transfer_matrix_report=stage_6_report)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertTrue(report["measuredTransferMatrixAvailable"])
        self.assertFalse(report["hardwareValidated"])
        self.assertFalse(report["productionInferenceReady"])
        self.assertIsNone(report["blockedByDependency"])
        self.assertEqual(report["missingEvidence"], [])
        self.assertEqual(report["invalidEvidence"], [])
        self.assertEqual(report["hashMismatches"], [])
        self.assertEqual(report["missingArtifactReferences"], [])

    def test_stage_0_gate_requires_claim_boundaries_and_forbidden_phrase_absence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "spec.md"
            path.write_text(
                "\n".join([
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
                ]),
                encoding="utf-8",
            )
            report = stage_0_specification_gate(path)
        self.assertEqual(report["stageStatus"], "complete")
        self.assertFalse(report["forbiddenHardwareCompilationPhrasePresent"])
        self.assertFalse(report["hardwareValidated"])

    def _stage_6_manifest(self, sha256_hash: str = "f" * 64) -> dict:
        return {
            "artifactId": "stage6-test-fixture",
            "measurementDate": "2026-05-03",
            "deviceId": "test-device",
            "setupDescription": "test setup",
            "wavelength": "1550 nm",
            "temperatureOrOperatingCondition": "295 K",
            "matrixShape": [1, 1],
            "matrixConvention": "real",
            "calibrationProcedure": "test calibration procedure",
            "rawArtifactReference": "raw.json",
            "processedArtifactReference": "processed.json",
            "sha256Hash": sha256_hash,
            "provenance": "test provenance",
            "uncertaintyOrErrorEstimate": "test uncertainty",
            "operatorOrSource": "test operator",
            "claimBoundary": "test fixture only",
        }

    def _stage_7_manifest(self) -> dict:
        return {
            "benchmarkId": "stage7-test-fixture",
            "deviceId": "test-device",
            "measuredTransferMatrixReference": "stage6-manifest.json",
            "dataset": "test dataset",
            "softwareBaseline": "test software baseline",
            "inputEncoding": "test input encoding",
            "outputReadout": "test output readout",
            "controlPathCharacterization": "test control path characterization",
            "detectorReadoutCharacterization": "test detector readout characterization",
            "accuracyMetric": "test accuracy metric",
            "latencyMetric": "test latency metric",
            "energyMetric": "test energy metric",
            "driftRecalibrationMetric": "test drift metric",
            "environment": "test environment",
            "rawResultsHash": {"artifactReference": "raw-results.json", "sha256": "f" * 64},
            "processedResultsHash": {"artifactReference": "processed-results.json", "sha256": "f" * 64},
            "provenance": "test provenance",
            "claimBoundary": "test fixture only",
        }

    def _write_valid_stage_6_fixture(self, root: Path) -> Path:
        (root / "raw.json").write_text('{"raw": true}\n', encoding="utf-8")
        processed = root / "processed.json"
        processed.write_text('{"matrix": [[1.0]]}\n', encoding="utf-8")
        manifest = self._stage_6_manifest(sha256_hash=_sha256(processed))
        manifest_path = root / "stage6-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path

    def _write_valid_stage_7_fixture(self, root: Path, stage_6_manifest: Path) -> Path:
        raw_results = root / "raw-results.json"
        processed_results = root / "processed-results.json"
        raw_results.write_text('{"rawResults": true}\n', encoding="utf-8")
        processed_results.write_text('{"processedResults": true}\n', encoding="utf-8")
        manifest = self._stage_7_manifest()
        manifest["measuredTransferMatrixReference"] = stage_6_manifest.name
        manifest["rawResultsHash"] = {
            "artifactReference": raw_results.name,
            "sha256": _sha256(raw_results),
        }
        manifest["processedResultsHash"] = {
            "artifactReference": processed_results.name,
            "sha256": _sha256(processed_results),
        }
        manifest_path = root / "stage7-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path


if __name__ == "__main__":
    unittest.main()
