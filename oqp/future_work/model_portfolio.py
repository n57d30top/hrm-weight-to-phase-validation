"""Deterministic model-portfolio planning reports for v0.2 work."""

from __future__ import annotations

from typing import Any, Dict, List


EVIDENCE_LEVEL = "model_portfolio_benchmark_simulation"
RANKING_EVIDENCE_LEVEL = "model_portfolio_ranking_simulation"
CLAIM_BOUNDARY = (
    "Simulation-only model portfolio planning; this does not claim hardware validation, "
    "foundry calibration, measured transfer matrices, production inference readiness, "
    "full model acceleration, quantum advantage, hardware-native intelligence, or power-free computation."
)


def run_model_portfolio_benchmark_report() -> Dict[str, Any]:
    rows = [_portfolio_row(model) for model in _portfolio_models()]
    return {
        "id": "model-portfolio-benchmark",
        "title": "Model portfolio benchmark for HRM mapping suitability",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "modelCount": len(rows),
        "models": rows,
        "portfolioFixtures": [row["modelId"] for row in rows],
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": [
            "no_foundry_calibrated_device_model",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": [
            "model_export_adapter_protocol",
            "hardware_design_space_explorer",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_model_portfolio_ranking_report() -> Dict[str, Any]:
    benchmark = run_model_portfolio_benchmark_report()
    ranked = sorted(
        benchmark["models"],
        key=lambda row: (-row["modelSuitabilityScore"], row["unsupportedLayerCount"], row["modelId"]),
    )
    return {
        "id": "model-portfolio-ranking",
        "title": "Model portfolio ranking for simulation-only HRM planning",
        "stage": 2,
        "evidenceLevel": RANKING_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "modelCount": benchmark["modelCount"],
        "bestSimulationCandidate": ranked[0],
        "worstSimulationCandidate": ranked[-1],
        "ranking": [
            {
                "rank": index + 1,
                "modelId": row["modelId"],
                "modelSuitabilityScore": row["modelSuitabilityScore"],
                "suitabilityClass": row["suitabilityClass"],
                "mappableParameterShare": row["mappableParameterShare"],
                "unsupportedLayerCount": row["unsupportedLayerCount"],
            }
            for index, row in enumerate(ranked)
        ],
        "portfolioDecisionSummary": [
            f"{ranked[0]['modelId']} is the best simulation candidate in this deterministic portfolio.",
            f"{ranked[-1]['modelId']} is the weakest simulation candidate because unsupported components dominate.",
            "All portfolio decisions remain simulation-only planning labels.",
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": benchmark["blockers"],
        "nextValidationGates": benchmark["nextValidationGates"],
    }


def render_model_portfolio_decision_summary(report: Dict[str, Any]) -> str:
    lines = [
        "# Model Portfolio Decision Summary",
        "",
        "This is a simulation-only portfolio summary. It is not hardware evidence.",
        "",
        f"Best simulation candidate: `{report['bestSimulationCandidate']['modelId']}`",
        f"Worst simulation candidate: `{report['worstSimulationCandidate']['modelId']}`",
        "",
        "## Ranking",
        "",
        "| Rank | Model | Score | Class | Unsupported Layers |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["ranking"]:
        lines.append(
            f"| {row['rank']} | `{row['modelId']}` | {row['modelSuitabilityScore']} | "
            f"{row['suitabilityClass']} | {row['unsupportedLayerCount']} |"
        )
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        report["claimBoundary"],
        "",
    ])
    return "\n".join(lines)


def _portfolio_models() -> List[Dict[str, Any]]:
    return [
        {
            "modelId": "tiny_mlp",
            "modelType": "mlp",
            "layerCount": 5,
            "mappableLayerCount": 2,
            "classicalLayerCount": 3,
            "unsupportedLayerCount": 0,
            "mappableParameterShare": 0.823529411765,
            "rectangularLayerShare": 1.0,
            "complexLayerShare": 0.0,
            "fixtureKind": "manifest_fixture",
            "notes": ["existing tiny MLP manifest fixture"],
        },
        {
            "modelId": "projection_chain",
            "modelType": "projection_chain",
            "layerCount": 4,
            "mappableLayerCount": 2,
            "classicalLayerCount": 2,
            "unsupportedLayerCount": 0,
            "mappableParameterShare": 0.888888888889,
            "rectangularLayerShare": 1.0,
            "complexLayerShare": 0.0,
            "fixtureKind": "portfolio_fixture",
            "notes": ["rectangular projection chain"],
        },
        {
            "modelId": "low_rank_adapter_demo",
            "modelType": "adapter",
            "layerCount": 6,
            "mappableLayerCount": 4,
            "classicalLayerCount": 2,
            "unsupportedLayerCount": 0,
            "mappableParameterShare": 0.941176470588,
            "rectangularLayerShare": 1.0,
            "complexLayerShare": 0.0,
            "fixtureKind": "portfolio_fixture",
            "notes": ["low-rank adapter-style linear factors"],
        },
        {
            "modelId": "sparse_linear_demo",
            "modelType": "sparse_linear",
            "layerCount": 5,
            "mappableLayerCount": 2,
            "classicalLayerCount": 2,
            "unsupportedLayerCount": 1,
            "mappableParameterShare": 0.642857142857,
            "rectangularLayerShare": 0.5,
            "complexLayerShare": 0.0,
            "fixtureKind": "portfolio_fixture",
            "notes": ["sparse mask remains classical or unsupported"],
        },
        {
            "modelId": "transformer_block_manifest_only",
            "modelType": "transformer_block_manifest_only",
            "layerCount": 12,
            "mappableLayerCount": 4,
            "classicalLayerCount": 4,
            "unsupportedLayerCount": 4,
            "mappableParameterShare": 0.571428571429,
            "rectangularLayerShare": 1.0,
            "complexLayerShare": 0.0,
            "fixtureKind": "manifest_only",
            "notes": ["attention softmax, embedding, and normalization remain outside optical mesh"],
        },
    ]


def _portfolio_row(model: Dict[str, Any]) -> Dict[str, Any]:
    unsupported_share = model["unsupportedLayerCount"] / max(1, model["layerCount"])
    score = round(
        max(
            0.0,
            min(
                100.0,
                100.0 * (
                    0.70 * model["mappableParameterShare"]
                    + 0.20 * (1.0 - unsupported_share)
                    + 0.10 * (1.0 if model["unsupportedLayerCount"] == 0 else 0.0)
                ),
            ),
        ),
        3,
    )
    row = dict(model)
    row.update({
        "modelSuitabilityScore": score,
        "suitabilityClass": _suitability_class(score),
        "simulationOnly": True,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    })
    return row


def _suitability_class(score: float) -> str:
    if score >= 75.0:
        return "good_candidate"
    if score >= 40.0:
        return "partial_candidate"
    return "poor_candidate"
