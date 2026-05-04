"""Model suitability profiling for HRM neural future work.

The profiler turns a validated model-weight manifest into a deterministic,
simulation-only suitability summary. It classifies mappable linear layers,
classical components, and unsupported layer types without claiming hardware
readiness.
"""

from __future__ import annotations

from collections import Counter
from math import prod
from pathlib import Path
from typing import Any, Dict, List

from .model_weight_manifest import DEFAULT_MANIFEST, ROOT, import_model_weight_manifest


PROFILE_EVIDENCE_LEVEL = "model_suitability_profile_simulation"
ANALYSIS_EVIDENCE_LEVEL = "model_suitability_analysis"
CLAIM_BOUNDARY = (
    "Simulation-only model suitability heuristic; this is not hardware validated and does not claim "
    "foundry calibration, measured transfer matrices, production inference readiness, real hardware "
    "latency, real hardware energy efficiency, quantum advantage, hardware-native intelligence, or "
    "power-free computation."
)


def run_model_suitability_profile_report(
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> Dict[str, Any]:
    profile = profile_model_suitability(manifest_path or DEFAULT_MANIFEST, repo_root=repo_root or ROOT)
    return {
        "id": "model-suitability-profile",
        "title": "Model suitability profile for abstract HRM photonic mapping",
        "stage": 2,
        "evidenceLevel": PROFILE_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": CLAIM_BOUNDARY,
        **profile,
        "scoreLabels": {
            "modelSuitabilityScore": "heuristic_simulation_only_not_hardware_validated",
            "suitabilityClass": "planning_label_only",
        },
        "limitations": [
            "heuristic score only",
            "tiny deterministic fixture model only",
            "bias and activation components remain classical outside the optical mesh",
            "mappability is based on manifest layer types and existing abstract simulation support",
            "no measured transfer matrix, foundry model, hardware timing, or hardware energy evidence",
        ],
        "blockers": [
            "no_foundry_calibrated_device_model",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": [
            "parametric_hardware_scenario_estimator",
            "hardware_requirements_generator",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_model_suitability_analysis_report(
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> Dict[str, Any]:
    profile_report = run_model_suitability_profile_report(manifest_path=manifest_path, repo_root=repo_root)
    mappable = [row for row in profile_report["layerClassification"] if row["classification"].startswith("optically_mappable")]
    unsupported = [row for row in profile_report["layerClassification"] if row["classification"].startswith("unsupported")]
    return {
        "id": "model-suitability-analysis",
        "title": "Model suitability analysis for abstract HRM mapping",
        "stage": 2,
        "evidenceLevel": ANALYSIS_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": CLAIM_BOUNDARY,
        "modelId": profile_report["modelId"],
        "profileReport": "model-suitability-profile.json",
        "topMappableLayers": sorted(mappable, key=lambda row: row["parameterCount"], reverse=True),
        "topUnsupportedLayers": sorted(unsupported, key=lambda row: row["parameterCount"], reverse=True),
        "suitabilityDrivers": _suitability_drivers(profile_report),
        "suitabilityPenalties": _suitability_penalties(profile_report),
        "recommendedNextModelChanges": _recommended_model_changes(profile_report),
        "limitations": profile_report["limitations"],
        "nextValidationGates": profile_report["nextValidationGates"],
        "blockers": profile_report["blockers"],
    }


def profile_model_suitability(manifest_path: Path, repo_root: Path | None = None) -> Dict[str, Any]:
    imported = import_model_weight_manifest(manifest_path, repo_root=repo_root or ROOT)
    manifest = imported["manifest"]
    rows = _classification_rows(manifest["layerList"], imported["eligibilityByLayer"])
    mappable_rows = [row for row in rows if row["classification"].startswith("optically_mappable")]
    classical_rows = [row for row in rows if row["classification"].startswith("classical")]
    unsupported_rows = [row for row in rows if row["classification"].startswith("unsupported")]
    total_parameter_count = sum(row["parameterCount"] for row in rows)
    mappable_parameter_count = sum(row["parameterCount"] for row in mappable_rows)
    total_layer_count = len(rows)
    unsupported_reason_counts = dict(sorted(Counter(row["reason"] for row in unsupported_rows).items()))
    mappable_share = _safe_ratio(len(mappable_rows), total_layer_count)
    unsupported_share = _safe_ratio(len(unsupported_rows), total_layer_count)
    mappable_parameter_share = _safe_ratio(mappable_parameter_count, total_parameter_count)
    rectangular_layer_share = _safe_ratio(
        sum(1 for row in mappable_rows if row["classification"] == "optically_mappable_rectangular_linear"),
        len(mappable_rows),
    )
    complex_layer_share = _safe_ratio(
        sum(1 for row in mappable_rows if row["classification"] == "optically_mappable_complex_linear"),
        len(mappable_rows),
    )
    score = _suitability_score(
        mappable_parameter_share=mappable_parameter_share,
        unsupported_share=unsupported_share,
        unsupported_count=len(unsupported_rows),
    )
    return {
        "modelId": manifest["modelId"],
        "manifestPath": {
            "configured": _repo_relative_path(imported["manifestPath"], imported["repoRoot"]),
            "exists": imported["manifestPath"].is_file(),
        },
        "totalLayerCount": total_layer_count,
        "mappableLayerCount": len(mappable_rows),
        "classicalLayerCount": len(classical_rows),
        "unsupportedLayerCount": len(unsupported_rows),
        "mappableLinearLayerShare": mappable_share,
        "mappableParameterShare": mappable_parameter_share,
        "rectangularLayerShare": rectangular_layer_share,
        "complexLayerShare": complex_layer_share,
        "unsupportedReasonCounts": unsupported_reason_counts,
        "modelSuitabilityScore": score,
        "modelSuitabilityScoreKind": "heuristic_simulation_only",
        "scoreHardwareValidated": False,
        "suitabilityClass": _suitability_class(score),
        "reasons": _profile_reasons(len(mappable_rows), len(classical_rows), len(unsupported_rows), mappable_parameter_share),
        "layerClassification": rows,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _classification_rows(layers: List[dict], eligibility_rows: List[dict]) -> List[dict]:
    eligibility_by_id = {row["layerId"]: row for row in eligibility_rows}
    rows: List[dict] = []
    for layer in layers:
        eligibility = eligibility_by_id[layer["layerId"]]
        weight_parameter_count = _parameter_count(layer["shape"])
        rows.append({
            "componentId": f"{layer['layerId']}.weight",
            "layerId": layer["layerId"],
            "componentRole": "weight",
            "layerType": layer["layerType"],
            "classification": _weight_classification(layer["layerType"], layer["shape"]),
            "mappingMode": eligibility["mappingMode"],
            "parameterCount": weight_parameter_count,
            "shape": layer["shape"],
            "reason": eligibility["classificationReason"],
            "hardwareValidated": False,
            "foundryCalibrated": False,
            "measuredTransferMatrixAvailable": False,
            "productionInferenceReady": False,
        })
        if "biasArtifactReference" in layer:
            rows.append({
                "componentId": f"{layer['layerId']}.bias",
                "layerId": layer["layerId"],
                "componentRole": "bias",
                "layerType": "bias",
                "classification": "classical_bias",
                "mappingMode": "classical_outside_optical_mesh",
                "parameterCount": layer["shape"][0],
                "shape": [layer["shape"][0]],
                "reason": "bias remains classical outside the optical mesh",
                "hardwareValidated": False,
                "foundryCalibrated": False,
                "measuredTransferMatrixAvailable": False,
                "productionInferenceReady": False,
            })
        activation = layer.get("activationAfterLayer")
        if activation not in ("none", None):
            rows.append({
                "componentId": f"{layer['layerId']}.activation",
                "layerId": layer["layerId"],
                "componentRole": "activation",
                "layerType": str(activation),
                "classification": "classical_activation",
                "mappingMode": "classical_outside_optical_mesh",
                "parameterCount": 0,
                "shape": [],
                "reason": f"{activation} remains classical outside the optical mesh",
                "hardwareValidated": False,
                "foundryCalibrated": False,
                "measuredTransferMatrixAvailable": False,
                "productionInferenceReady": False,
            })
    return rows


def _weight_classification(layer_type: str, shape: List[int]) -> str:
    if layer_type == "linear":
        if len(shape) == 2 and shape[0] != shape[1]:
            return "optically_mappable_rectangular_linear"
        return "optically_mappable_linear"
    if layer_type == "rectangular_linear":
        return "optically_mappable_rectangular_linear"
    if layer_type == "complex_linear":
        return "optically_mappable_complex_linear"
    if layer_type == "normalization":
        return "classical_normalization"
    if layer_type == "activation":
        return "classical_activation"
    if layer_type == "bias":
        return "classical_bias"
    if layer_type == "convolution":
        return "unsupported_convolution"
    if layer_type == "attention_softmax":
        return "unsupported_attention_softmax"
    if layer_type == "embedding":
        return "unsupported_embedding"
    return "unsupported_other"


def _suitability_score(
    *,
    mappable_parameter_share: float,
    unsupported_share: float,
    unsupported_count: int,
) -> float:
    score = 100.0 * (
        0.70 * mappable_parameter_share
        + 0.20 * (1.0 if unsupported_count == 0 else 0.0)
        + 0.10 * (1.0 - unsupported_share)
    )
    return round(max(0.0, min(100.0, score)), 3)


def _suitability_class(score: float) -> str:
    if score >= 75.0:
        return "good_candidate"
    if score >= 40.0:
        return "partial_candidate"
    return "poor_candidate"


def _profile_reasons(
    mappable_count: int,
    classical_count: int,
    unsupported_count: int,
    mappable_parameter_share: float,
) -> List[str]:
    reasons = [
        f"{mappable_count} components are mappable through existing abstract simulation paths",
        f"{classical_count} components remain classical outside the optical mesh",
        f"mappable parameter share is {mappable_parameter_share:.3f}",
    ]
    if unsupported_count:
        reasons.append(f"{unsupported_count} components are unsupported by current mapping paths")
    else:
        reasons.append("no unsupported components are present in the fixture manifest")
    return reasons


def _suitability_drivers(profile_report: Dict[str, Any]) -> List[str]:
    drivers = []
    if profile_report["mappableParameterShare"] >= 0.75:
        drivers.append("most fixture parameters are in mappable linear weights")
    if profile_report["unsupportedLayerCount"] == 0:
        drivers.append("no unsupported layer types are present")
    if profile_report["rectangularLayerShare"] > 0:
        drivers.append("rectangular linear layers are covered by existing abstract rectangular support")
    return drivers or ["no strong positive suitability driver identified"]


def _suitability_penalties(profile_report: Dict[str, Any]) -> List[str]:
    penalties = []
    if profile_report["classicalLayerCount"] > 0:
        penalties.append("bias and activation components remain classical outside the optical mesh")
    if profile_report["unsupportedLayerCount"] > 0:
        penalties.append("unsupported layer types reduce suitability")
    if profile_report["complexLayerShare"] == 0:
        penalties.append("fixture does not exercise complex linear mapping")
    return penalties


def _recommended_model_changes(profile_report: Dict[str, Any]) -> List[str]:
    recommendations = [
        "keep linear projection weights in explicit manifest artifacts",
        "keep bias, activation, and normalization operations marked as classical",
    ]
    if profile_report["unsupportedLayerCount"]:
        recommendations.append("replace or isolate unsupported layer types before abstract HRM mapping analysis")
    else:
        recommendations.append("next evaluate larger manifests with unsupported layer types to test partial-candidate behavior")
    return recommendations


def _parameter_count(shape: List[int]) -> int:
    if not shape:
        return 0
    return int(prod(shape))


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 12)


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name
