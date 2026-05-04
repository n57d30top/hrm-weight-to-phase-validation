"""Optional model-export adapter protocol and validation demo."""

from __future__ import annotations

from typing import Any, Dict, List


EVIDENCE_LEVEL = "model_export_adapter_protocol"
VALIDATION_EVIDENCE_LEVEL = "model_export_adapter_validation"
CLAIM_BOUNDARY = (
    "Optional export-adapter protocol only; this does not claim PyTorch model execution, "
    "full model acceleration, hardware validation, foundry calibration, measured transfer matrices, "
    "production inference readiness, quantum advantage, hardware-native intelligence, or power-free computation."
)


def run_model_export_adapter_demo_report() -> Dict[str, Any]:
    manifest = _example_generated_manifest()
    return {
        "id": "model-export-adapter-demo",
        "title": "Optional model export adapter protocol demo",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "adapterProtocolVersion": "model-export-adapter.v1",
        "pyTorchHardDependency": False,
        "exampleModelId": manifest["modelId"],
        "generatedManifestPreview": manifest,
        "supportedExportSteps": [
            "external framework exports weights into JSON artifacts",
            "adapter writes model-weight manifest fields",
            "existing manifest importer validates paths, hashes, shapes, and dtype metadata",
        ],
        "unsupportedExecutionClaims": [
            "no framework execution is performed",
            "no transformer acceleration is claimed",
            "no optical nonlinearities are implemented",
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": [
            "no_runtime_framework_adapter_dependency",
            "no_foundry_calibrated_device_model",
            "no_measured_transfer_matrix",
        ],
        "nextValidationGates": [
            "generated_manifest_validation",
            "larger_model_manifest_fixtures",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_model_export_adapter_validation_report() -> Dict[str, Any]:
    manifest = _example_generated_manifest()
    findings = _validate_generated_manifest(manifest)
    valid = not findings
    return {
        "id": "model-export-adapter-validation",
        "title": "Generated model manifest validation for optional export adapter",
        "stage": 2,
        "evidenceLevel": VALIDATION_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "generatedManifestValid": valid,
        "validationFindings": findings,
        "layerCount": len(manifest["layerList"]),
        "eligibleLinearLayerCount": sum(1 for layer in manifest["layerList"] if layer["layerType"] in {"linear", "rectangular_linear"}),
        "unsupportedLayerTypes": sorted({
            layer["layerType"]
            for layer in manifest["layerList"]
            if layer["layerType"] not in {"linear", "rectangular_linear", "complex_linear"}
        }),
        "pyTorchHardDependency": False,
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": [
            "no_runtime_framework_adapter_dependency",
            "no_foundry_calibrated_device_model",
            "no_measured_transfer_matrix",
        ],
        "nextValidationGates": [
            "model_portfolio_benchmark",
            "model_weight_manifest_import",
            "foundry_calibrated_device_model_gate",
        ],
    }


def render_model_export_adapter_protocol() -> str:
    return "\n".join([
        "# Model Export Adapter Protocol",
        "",
        "This protocol describes optional exporter behavior. It is not framework execution and not hardware evidence.",
        "",
        "## Adapter Contract",
        "",
        "- external frameworks may export weights into repository-relative JSON artifacts",
        "- exporter output must use the existing model-weight manifest schema",
        "- every weight artifact must have a SHA-256 hash",
        "- generated manifests must be validated by the existing importer before mapping analysis",
        "- PyTorch is not a required dependency",
        "",
        "## Optional Example",
        "",
        "`fixtures/model-export-adapter/tiny-linear-export-example.json` shows the adapter input shape.",
        "",
        "## Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
    ])


def _example_generated_manifest() -> Dict[str, Any]:
    return {
        "modelId": "adapter_tiny_linear_demo",
        "modelType": "mlp",
        "sourceFramework": "external_manifest_exporter",
        "exportFormat": "json_manifest",
        "exportDate": "2026-05-04",
        "provenance": "deterministic optional exporter example",
        "layerList": [
            {
                "layerId": "dense_1",
                "layerType": "rectangular_linear",
                "shape": [3, 4],
                "dtype": "float64",
                "weightArtifactReference": "fixtures/model-weights/tiny-mlp-w2.json",
                "weightArtifactSha256": "placeholder_hash_supplied_by_external_exporter",
                "activationAfterLayer": "none",
                "mappingEligible": True,
                "mappingLimitations": ["abstract rectangular mapping only"],
                "claimBoundary": "simulation-only manifest entry",
            }
        ],
        "claimBoundary": "simulation-only generated manifest preview",
    }


def _validate_generated_manifest(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    required = ["modelId", "modelType", "sourceFramework", "exportFormat", "exportDate", "provenance", "layerList", "claimBoundary"]
    findings: List[Dict[str, Any]] = [
        {"field": field, "reason": "missing_required_field"}
        for field in required
        if not manifest.get(field)
    ]
    for layer in manifest.get("layerList", []):
        for field in ["layerId", "layerType", "shape", "dtype", "weightArtifactReference", "weightArtifactSha256"]:
            if not layer.get(field):
                findings.append({"layerId": layer.get("layerId"), "field": field, "reason": "missing_required_layer_field"})
        reference = str(layer.get("weightArtifactReference", ""))
        if reference.startswith("/") or ".." in reference.split("/"):
            findings.append({"layerId": layer.get("layerId"), "field": "weightArtifactReference", "reason": "path_must_be_repo_relative"})
    return findings
