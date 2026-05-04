"""Model-weight manifest import for HRM neural future work.

This module validates deterministic model-weight manifests and classifies layer
eligibility for the simulation-only HRM mapping path. It intentionally avoids a
PyTorch dependency and does not execute full models or claim hardware readiness.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "fixtures" / "model-weights" / "tiny-mlp-manifest.json"

TOP_LEVEL_REQUIRED_FIELDS = [
    "modelId",
    "modelType",
    "sourceFramework",
    "exportFormat",
    "exportDate",
    "provenance",
    "layerList",
    "claimBoundary",
]

LAYER_REQUIRED_FIELDS = [
    "layerId",
    "layerType",
    "shape",
    "dtype",
    "activationAfterLayer",
    "mappingEligible",
    "mappingLimitations",
    "claimBoundary",
]

WEIGHT_LAYER_TYPES = {"linear", "rectangular_linear", "complex_linear", "convolution", "embedding"}
ELIGIBLE_LAYER_TYPES = {"linear", "rectangular_linear", "complex_linear"}
CLASSICAL_ONLY_LAYER_TYPES = {"normalization", "activation", "bias"}
INELIGIBLE_LAYER_TYPES = {"convolution", "attention_softmax", "embedding"}
ALLOWED_DTYPES = {"float64", "float32", "float16"}
LOCAL_PATH_FRAGMENTS = [
    "/" + "Users" + "/",
    "/" + "home" + "/",
    "Desktop" + "/",
    "file:" + "//",
]


@dataclass(frozen=True)
class ManifestValidationError(ValueError):
    errors: List[dict]

    def __str__(self) -> str:
        return json.dumps(self.errors, sort_keys=True)


def run_model_weight_import_demo_report(
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict:
    imported = import_model_weight_manifest(manifest_path or DEFAULT_MANIFEST, repo_root=repo_root or ROOT)
    primary = imported["manifest"]
    return {
        "id": "model-weight-import-demo",
        "title": "Model weight manifest import demo",
        "stage": 2,
        "evidenceLevel": "model_weight_manifest_import_simulation",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only model-weight manifest import; no hardware validation, foundry calibration, measured transfer matrix, production inference readiness, optical nonlinearity, full model acceleration, transformer acceleration, or PyTorch execution is claimed.",
        "modelId": primary["modelId"],
        "manifestPath": {
            "configured": _repo_relative_path(imported["manifestPath"], imported["repoRoot"]),
            "exists": imported["manifestPath"].is_file(),
        },
        "layerCount": imported["layerCount"],
        "eligibleLayerCount": imported["eligibleLayerCount"],
        "ineligibleLayerCount": imported["ineligibleLayerCount"],
        "classicalLayerCount": imported["classicalLayerCount"],
        "loadedWeightArtifacts": imported["loadedWeightArtifacts"],
        "hashValidationPassed": True,
        "pathValidationPassed": True,
        "mappingPlan": imported["mappingPlan"],
        "unsupportedLayerTypes": imported["unsupportedLayerTypes"],
        "limitations": [
            "deterministic JSON fixture import only",
            "no PyTorch dependency or PyTorch model execution",
            "no transformer execution or acceleration claim",
            "bias additions remain classical outside the optical mesh",
            "activations remain classical outside the optical mesh",
            "eligible linear layers are mapped only as abstract simulation candidates",
            "no hardware validation, foundry calibration, measured transfer matrix, timing, or energy evidence",
        ],
        "blockers": [
            "no_external_model_export_adapter",
            "no_full_model_execution",
            "no_measured_transfer_matrix",
            "no_hardware_benchmark",
        ],
        "nextValidationGates": [
            "scaling_and_larger_layer_benchmarks",
            "review_pack",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_model_weight_eligibility_analysis_report(
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict:
    imported = import_model_weight_manifest(manifest_path or DEFAULT_MANIFEST, repo_root=repo_root or ROOT)
    return {
        "id": "model-weight-eligibility-analysis",
        "title": "Model weight mapping eligibility analysis",
        "stage": 2,
        "evidenceLevel": "model_weight_manifest_eligibility_analysis",
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only model-weight eligibility analysis; no hardware validation, foundry calibration, measured transfer matrix, production inference readiness, optical nonlinearity, full model acceleration, transformer acceleration, or PyTorch execution is claimed.",
        "modelId": imported["manifest"]["modelId"],
        "eligibleLinearLayerCount": imported["eligibleLinearLayerCount"],
        "eligibleRectangularLayerCount": imported["eligibleRectangularLayerCount"],
        "eligibleComplexLayerCount": imported["eligibleComplexLayerCount"],
        "ineligibleLayerCount": imported["ineligibleLayerCount"],
        "classicalOnlyLayerCount": imported["classicalOnlyLayerCount"],
        "unsupportedLayerTypes": imported["unsupportedLayerTypes"],
        "eligibilityByLayer": imported["eligibilityByLayer"],
        "mappingLimitations": _collect_mapping_limitations(imported["eligibilityByLayer"]),
        "blockers": [
            "no_external_model_export_adapter",
            "no_full_model_execution",
            "no_measured_transfer_matrix",
            "no_hardware_benchmark",
        ],
        "nextValidationGates": [
            "scaling_and_larger_layer_benchmarks",
            "review_pack",
            "foundry_calibrated_device_model_gate",
        ],
    }


def import_model_weight_manifest(manifest_path: Path, repo_root: Path | None = None) -> dict:
    repo_root = (repo_root or ROOT).resolve()
    manifest_path = manifest_path.resolve()
    manifest = _load_json(manifest_path)
    errors = _validate_manifest_schema(manifest)
    errors.extend(_validate_iso_date_field(manifest, "exportDate"))

    layers = manifest.get("layerList", [])
    artifact_reports: List[dict] = []
    eligibility: List[dict] = []
    mapping_plan: List[dict] = []

    if not errors:
        for layer in layers:
            layer_report, layer_errors = _validate_layer(layer, repo_root)
            errors.extend(layer_errors)
            artifact_reports.extend(layer_report["artifacts"])
            layer_eligibility = _eligibility_report(layer, layer_report)
            eligibility.append(layer_eligibility)
            if layer_eligibility["mappingEligible"]:
                mapping_plan.append(_mapping_plan_entry(layer, layer_eligibility))

    if errors:
        raise ManifestValidationError(errors)

    unsupported = sorted({
        row["layerType"]
        for row in eligibility
        if row["classification"] == "ineligible"
    })
    return {
        "repoRoot": repo_root,
        "manifestPath": manifest_path,
        "manifest": manifest,
        "layerCount": len(layers),
        "eligibleLayerCount": sum(1 for row in eligibility if row["mappingEligible"]),
        "eligibleLinearLayerCount": sum(1 for row in eligibility if row["layerType"] == "linear" and row["mappingEligible"]),
        "eligibleRectangularLayerCount": sum(1 for row in eligibility if row["layerType"] == "rectangular_linear" and row["mappingEligible"]),
        "eligibleComplexLayerCount": sum(1 for row in eligibility if row["layerType"] == "complex_linear" and row["mappingEligible"]),
        "ineligibleLayerCount": sum(1 for row in eligibility if row["classification"] == "ineligible"),
        "classicalOnlyLayerCount": _classical_only_count(layers),
        "classicalLayerCount": _classical_component_count(layers),
        "loadedWeightArtifacts": artifact_reports,
        "mappingPlan": mapping_plan,
        "unsupportedLayerTypes": unsupported,
        "eligibilityByLayer": eligibility,
    }


def classify_layer_type(layer_type: str, shape: List[int] | None = None) -> dict:
    if layer_type == "linear":
        return {
            "classification": "eligible",
            "mappingEligible": True,
            "mappingMode": "abstract_square_real_mesh" if shape and len(shape) == 2 and shape[0] == shape[1] else "abstract_real_linear_mesh",
            "reason": "linear layer is eligible for abstract simulation mapping",
        }
    if layer_type == "rectangular_linear":
        return {
            "classification": "eligible",
            "mappingEligible": True,
            "mappingMode": "abstract_rectangular_orthogonal_completion_mesh",
            "reason": "rectangular linear layer is eligible for abstract rectangular simulation mapping",
        }
    if layer_type == "complex_linear":
        return {
            "classification": "eligible",
            "mappingEligible": True,
            "mappingMode": "complex_qr_unitary_factor",
            "reason": "complex linear layer is eligible only through current complex/unitary simulation support",
        }
    if layer_type in CLASSICAL_ONLY_LAYER_TYPES:
        return {
            "classification": "classical_only",
            "mappingEligible": False,
            "mappingMode": "classical_outside_optical_mesh",
            "reason": f"{layer_type} remains classical outside the optical mesh",
        }
    if layer_type in INELIGIBLE_LAYER_TYPES:
        return {
            "classification": "ineligible",
            "mappingEligible": False,
            "mappingMode": "not_implemented",
            "reason": f"{layer_type} mapping is not implemented",
        }
    return {
        "classification": "ineligible",
        "mappingEligible": False,
        "mappingMode": "unsupported_layer_type",
        "reason": f"{layer_type} is not supported by the manifest importer",
    }


def _validate_manifest_schema(manifest: Dict[str, Any]) -> List[dict]:
    errors = _missing_field_errors(manifest, TOP_LEVEL_REQUIRED_FIELDS, "manifest")
    layer_list = manifest.get("layerList")
    if "layerList" in manifest and (not isinstance(layer_list, list) or not layer_list):
        errors.append({"field": "layerList", "reason": "layerList must be a non-empty list"})
    if isinstance(layer_list, list):
        for index, layer in enumerate(layer_list):
            if not isinstance(layer, dict):
                errors.append({"field": f"layerList[{index}]", "reason": "layer entry must be an object"})
                continue
            errors.extend(_missing_field_errors(layer, LAYER_REQUIRED_FIELDS, f"layerList[{index}]"))
            if layer.get("layerType") in WEIGHT_LAYER_TYPES:
                errors.extend(_missing_field_errors(layer, ["weightArtifactReference", "weightArtifactSha256"], f"layerList[{index}]"))
            if "biasArtifactReference" in layer and "biasArtifactSha256" not in layer:
                errors.append({"field": f"layerList[{index}].biasArtifactSha256", "reason": "bias hash is required when bias artifact is present"})
            if "mappingLimitations" in layer and not isinstance(layer["mappingLimitations"], list):
                errors.append({"field": f"layerList[{index}].mappingLimitations", "reason": "mappingLimitations must be a list"})
            if "shape" in layer and not _valid_shape_metadata(layer["shape"]):
                errors.append({"field": f"layerList[{index}].shape", "reason": "shape must be a non-empty list of positive integers"})
            if "dtype" in layer and layer["dtype"] not in ALLOWED_DTYPES:
                errors.append({"field": f"layerList[{index}].dtype", "reason": "unsupported dtype"})
    return errors


def _validate_layer(layer: dict, repo_root: Path) -> tuple[dict, List[dict]]:
    errors: List[dict] = []
    artifacts: List[dict] = []
    if layer["layerType"] in WEIGHT_LAYER_TYPES:
        weight, weight_errors = _load_artifact(
            layer["weightArtifactReference"],
            layer["weightArtifactSha256"],
            repo_root,
            field_prefix=f"{layer['layerId']}.weightArtifactReference",
        )
        errors.extend(weight_errors)
        if weight is not None:
            errors.extend(_validate_weight_artifact(layer, weight, f"{layer['layerId']}.weightArtifactReference"))
            artifacts.append(_artifact_report(layer["layerId"], "weight", layer["weightArtifactReference"], weight))

    if "biasArtifactReference" in layer:
        bias, bias_errors = _load_artifact(
            layer["biasArtifactReference"],
            layer["biasArtifactSha256"],
            repo_root,
            field_prefix=f"{layer['layerId']}.biasArtifactReference",
        )
        errors.extend(bias_errors)
        if bias is not None:
            errors.extend(_validate_bias_artifact(layer, bias, f"{layer['layerId']}.biasArtifactReference"))
            artifacts.append(_artifact_report(layer["layerId"], "bias", layer["biasArtifactReference"], bias))

    return {"artifacts": artifacts}, errors


def _load_artifact(reference: str, expected_hash: str, repo_root: Path, field_prefix: str) -> tuple[dict | None, List[dict]]:
    errors = _validate_artifact_reference(reference, field_prefix)
    if errors:
        return None, errors
    path = repo_root / reference
    if not path.is_file():
        return None, [{"field": field_prefix, "reason": "artifact file does not exist", "reference": reference}]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_hash:
        return None, [{
            "field": field_prefix.replace("Reference", "Sha256"),
            "reason": "sha256 mismatch",
            "expected": expected_hash,
            "actual": digest,
        }]
    return _load_json(path), []


def _validate_artifact_reference(reference: str, field: str) -> List[dict]:
    errors: List[dict] = []
    if not isinstance(reference, str) or not reference:
        return [{"field": field, "reason": "artifact reference must be a non-empty string"}]
    path = Path(reference)
    if path.is_absolute() or ".." in path.parts:
        errors.append({"field": field, "reason": "artifact reference must be repo-relative", "reference": reference})
    if any(fragment in reference for fragment in LOCAL_PATH_FRAGMENTS) or _looks_like_windows_drive(reference):
        errors.append({"field": field, "reason": "artifact reference contains a local path fragment", "reference": reference})
    return errors


def _validate_weight_artifact(layer: dict, artifact: dict, field: str) -> List[dict]:
    errors = _artifact_common_errors(layer, artifact, field)
    values = artifact.get("values")
    if _shape_from_values(values) != layer["shape"]:
        errors.append({"field": field, "reason": "weight artifact shape does not match manifest layer shape"})
    return errors


def _validate_bias_artifact(layer: dict, artifact: dict, field: str) -> List[dict]:
    errors = _artifact_common_errors(layer, artifact, field)
    values = artifact.get("values")
    expected = [layer["shape"][0]] if len(layer["shape"]) == 2 else layer["shape"]
    if _shape_from_values(values) != expected:
        errors.append({"field": field, "reason": "bias artifact shape does not match layer output dimension"})
    return errors


def _artifact_common_errors(layer: dict, artifact: dict, field: str) -> List[dict]:
    errors = _missing_field_errors(artifact, ["dtype", "shape", "values"], field)
    if not errors and artifact["dtype"] != layer["dtype"]:
        errors.append({"field": f"{field}.dtype", "reason": "artifact dtype does not match manifest dtype"})
    if not errors and artifact["shape"] != _shape_from_values(artifact["values"]):
        errors.append({"field": f"{field}.shape", "reason": "artifact shape metadata does not match values"})
    return errors


def _eligibility_report(layer: dict, layer_report: dict) -> dict:
    classification = classify_layer_type(layer["layerType"], shape=layer["shape"])
    activation = layer.get("activationAfterLayer", "none")
    return {
        "layerId": layer["layerId"],
        "layerType": layer["layerType"],
        "shape": layer["shape"],
        "dtype": layer["dtype"],
        "classification": classification["classification"],
        "mappingEligible": classification["mappingEligible"],
        "manifestMappingEligible": bool(layer["mappingEligible"]),
        "mappingMode": classification["mappingMode"],
        "classificationReason": classification["reason"],
        "activationAfterLayer": activation,
        "activationClassicalOutsideOpticalMesh": activation not in ("none", None),
        "biasClassicalOutsideOpticalMesh": "biasArtifactReference" in layer,
        "loadedArtifactCount": len(layer_report["artifacts"]),
        "mappingLimitations": layer["mappingLimitations"],
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _mapping_plan_entry(layer: dict, eligibility: dict) -> dict:
    return {
        "layerId": layer["layerId"],
        "layerType": layer["layerType"],
        "shape": layer["shape"],
        "dtype": layer["dtype"],
        "mappingMode": eligibility["mappingMode"],
        "weightArtifactReference": layer.get("weightArtifactReference"),
        "biasHandling": "classical_outside_optical_mesh" if "biasArtifactReference" in layer else "none",
        "activationHandling": (
            "classical_outside_optical_mesh"
            if layer.get("activationAfterLayer") not in ("none", None)
            else "none"
        ),
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _artifact_report(layer_id: str, role: str, reference: str, artifact: dict) -> dict:
    return {
        "layerId": layer_id,
        "role": role,
        "artifactReference": reference,
        "shape": artifact["shape"],
        "dtype": artifact["dtype"],
    }


def _classical_only_count(layers: List[dict]) -> int:
    return sum(1 for layer in layers if layer.get("layerType") in CLASSICAL_ONLY_LAYER_TYPES)


def _classical_component_count(layers: List[dict]) -> int:
    bias_count = sum(1 for layer in layers if "biasArtifactReference" in layer)
    activation_count = sum(1 for layer in layers if layer.get("activationAfterLayer") not in ("none", None))
    classical_layers = _classical_only_count(layers)
    return bias_count + activation_count + classical_layers


def _collect_mapping_limitations(rows: List[dict]) -> List[str]:
    limitations = sorted({
        limitation
        for row in rows
        for limitation in row.get("mappingLimitations", [])
    })
    limitations.extend([
        "PyTorch export can generate this manifest format externally in future work",
        "PyTorch is not a required dependency",
    ])
    return limitations


def _missing_field_errors(data: Dict[str, Any], fields: List[str], prefix: str) -> List[dict]:
    return [
        {"field": f"{prefix}.{field}", "reason": "missing required field"}
        for field in fields
        if field not in data
    ]


def _validate_iso_date_field(data: Dict[str, Any], field: str) -> List[dict]:
    if field not in data:
        return []
    try:
        date.fromisoformat(data[field])
    except (TypeError, ValueError):
        return [{"field": field, "reason": "must be an ISO date string"}]
    return []


def _valid_shape_metadata(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, int) and item > 0 for item in value)


def _shape_from_values(value: Any) -> List[int]:
    if isinstance(value, list) and value and all(isinstance(row, list) for row in value):
        width = len(value[0])
        if any(not isinstance(row, list) or len(row) != width for row in value):
            return []
        return [len(value), width]
    if isinstance(value, list):
        return [len(value)]
    return []


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _looks_like_windows_drive(value: str) -> bool:
    return len(value) >= 3 and value[1] == ":" and value[2] in ("\\", "/")
