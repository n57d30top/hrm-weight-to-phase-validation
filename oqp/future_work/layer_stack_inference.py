"""Multi-layer toy inference for HRM neural future work.

This module composes multiple abstract mapped linear layers around classical
activation boundaries. It is a tiny deterministic inference simulation only;
it does not implement optical nonlinearities, hardware inference, timing, or
energy measurement.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List

from .mesh_mapping import build_mesh_transfer_model
from .neural_mapping import Matrix, matmul, relative_frobenius_error, scalar_multiply, svd_decompose
from .rectangular_mapping import build_rectangular_mesh_transfer_model


EVIDENCE_LEVEL = "abstract_layer_stack_inference_simulation"
ANALYSIS_EVIDENCE_LEVEL = "abstract_layer_stack_error_analysis"


@dataclass(frozen=True)
class ToyLayerStack:
    model_id: str
    input_vector: List[float]
    first_weight: Matrix
    first_bias: List[float]
    second_weight: Matrix
    second_bias: List[float]
    description: str


def deterministic_layer_stack_models() -> List[ToyLayerStack]:
    return [
        ToyLayerStack(
            model_id="tiny_mlp_4_6_3",
            input_vector=[0.60, -0.40, 0.25, 0.80],
            first_weight=[
                [0.42, -0.11, 0.28, 0.07],
                [-0.23, 0.51, 0.16, -0.32],
                [0.35, 0.09, -0.41, 0.22],
                [0.12, -0.37, 0.44, 0.18],
                [-0.31, 0.26, 0.05, 0.49],
                [0.08, 0.33, -0.19, -0.27],
            ],
            first_bias=[0.03, -0.02, 0.01, 0.04, -0.03, 0.02],
            second_weight=[
                [0.31, -0.18, 0.42, 0.07, -0.22, 0.15],
                [-0.28, 0.55, 0.11, -0.34, 0.21, 0.09],
                [0.17, 0.24, -0.46, 0.38, 0.06, -0.29],
            ],
            second_bias=[0.015, -0.025, 0.010],
            description="tiny deterministic MLP with 4 input features, 6 hidden units, and 3 outputs",
        ),
        ToyLayerStack(
            model_id="projection_chain_4_8_4",
            input_vector=[0.50, -0.25, 0.75, -0.10],
            first_weight=[
                [0.22, -0.31, 0.14, 0.07],
                [-0.18, 0.49, 0.25, -0.36],
                [0.41, 0.05, -0.33, 0.19],
                [0.09, -0.27, 0.52, 0.13],
                [-0.35, 0.21, 0.08, 0.44],
                [0.16, 0.38, -0.23, -0.29],
                [0.28, -0.12, 0.37, -0.18],
                [-0.24, 0.32, 0.11, 0.26],
            ],
            first_bias=[0.01, -0.03, 0.02, 0.00, -0.01, 0.025, -0.015, 0.005],
            second_weight=[
                [0.17, -0.24, 0.36, 0.05, -0.19, 0.31, 0.08, -0.12],
                [-0.28, 0.47, 0.09, -0.33, 0.18, 0.06, -0.22, 0.27],
                [0.39, 0.12, -0.44, 0.25, 0.04, -0.35, 0.16, 0.21],
                [0.11, -0.08, 0.29, 0.14, -0.41, 0.23, -0.17, 0.34],
            ],
            second_bias=[0.02, -0.015, 0.01, -0.005],
            description="rectangular projection chain with 4-to-8 and 8-to-4 linear maps",
        ),
    ]


def run_layer_stack_inference_demo_report(phase_levels: int = 64) -> dict:
    models = [_simulate_model(model, phase_levels=phase_levels) for model in deterministic_layer_stack_models()]
    primary = models[0]
    worst = max(models, key=lambda row: row["outputRelativeError"])
    return {
        "id": "layer-stack-inference-demo",
        "title": "Multi-layer toy inference through abstract HRM-mapped linear layers",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only multi-layer toy inference; no hardware validation, foundry calibration, measured transfer matrix, optical nonlinearity, full neural-network acceleration, or production inference readiness is claimed.",
        "phaseLevels": phase_levels,
        "modelCount": len(models),
        "modelId": primary["modelId"],
        "layerCount": primary["layerCount"],
        "linearLayerCount": primary["linearLayerCount"],
        "classicalActivationCount": primary["classicalActivationCount"],
        "opticalNonlinearityImplemented": False,
        "baselineOutput": primary["baselineOutput"],
        "mappedOutput": primary["mappedOutput"],
        "outputRelativeError": primary["outputRelativeError"],
        "layerWiseErrors": primary["layerWiseErrors"],
        "cumulativeError": primary["cumulativeError"],
        "outputRelativeErrorMax": worst["outputRelativeError"],
        "cumulativeErrorMax": worst["cumulativeError"],
        "worstModelId": worst["modelId"],
        "models": models,
        "limitations": [
            "tiny deterministic toy models only",
            "linear layers are mapped through abstract simulation transfer matrices",
            "bias additions remain classical outside the optical mesh",
            "ReLU remains a classical activation outside the optical mesh",
            "no real dataset",
            "no optical nonlinearities",
            "no hardware timing",
            "no energy measurement",
            "no measured transfer matrix",
        ],
        "blockers": [
            "no_real_dataset",
            "no_optical_nonlinearity_model",
            "no_measured_transfer_matrix",
            "no_hardware_timing_or_energy_measurement",
        ],
        "nextValidationGates": [
            "model_weight_manifest_import",
            "larger_layer_stack_benchmarks",
            "foundry_calibrated_device_model_gate",
        ],
    }


def run_layer_stack_error_analysis_report(phase_levels: int = 64) -> dict:
    demo = run_layer_stack_inference_demo_report(phase_levels=phase_levels)
    models = demo["models"]
    all_layers = [
        layer | {"modelId": model["modelId"]}
        for model in models
        for layer in model["layerWiseErrors"]
    ]
    worst_layer = max(all_layers, key=lambda row: row["relativeError"])
    worst_model = max(models, key=lambda row: row["outputRelativeError"])
    return {
        "id": "layer-stack-error-analysis",
        "title": "Multi-layer toy inference error analysis",
        "stage": 2,
        "evidenceLevel": ANALYSIS_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "claimBoundary": "Simulation-only layer-stack error analysis; no hardware validation, foundry calibration, measured transfer matrix, optical nonlinearity, full neural-network acceleration, or production inference readiness is claimed.",
        "demoReport": "layer-stack-inference-demo.json",
        "modelCount": len(models),
        "worstModelByOutputError": _model_summary(worst_model),
        "worstLayerByError": _layer_summary(worst_layer),
        "cumulativeErrorTrend": [
            {
                "modelId": model["modelId"],
                "layerErrors": [
                    {
                        "layerId": layer["layerId"],
                        "relativeError": layer["relativeError"],
                    }
                    for layer in model["layerWiseErrors"]
                ],
                "outputRelativeError": model["outputRelativeError"],
                "cumulativeError": model["cumulativeError"],
            }
            for model in models
        ],
        "errorsCompoundAcrossLayers": any(
            model["outputRelativeError"] > max(layer["relativeError"] for layer in model["layerWiseErrors"])
            for model in models
        ),
        "activationBoundaryNotes": [
            "ReLU is evaluated classically after the first mapped linear layer.",
            "No optical activation or optical nonlinearity is implemented.",
            "Activation boundaries can clip or propagate mapped linear-layer deviations depending on the sign pattern.",
        ],
        "limitations": [
            "tiny toy model only",
            "no real dataset",
            "no optical nonlinearities",
            "no hardware timing",
            "no energy measurement",
            "no measured transfer matrix",
        ],
        "blockers": demo["blockers"],
        "nextValidationGates": demo["nextValidationGates"],
    }


def _simulate_model(model: ToyLayerStack, phase_levels: int) -> dict:
    baseline_first_linear = _linear(model.first_weight, model.input_vector, model.first_bias)
    mapped_first_weight, first_weight_error, first_mode = _mapped_weight_matrix(
        model.first_weight,
        phase_levels=phase_levels,
        case_id=f"{model.model_id}_linear_1",
    )
    mapped_first_linear = _linear(mapped_first_weight, model.input_vector, model.first_bias)

    baseline_activation = _relu(baseline_first_linear)
    mapped_activation = _relu(mapped_first_linear)

    baseline_output = _linear(model.second_weight, baseline_activation, model.second_bias)
    mapped_second_weight, second_weight_error, second_mode = _mapped_weight_matrix(
        model.second_weight,
        phase_levels=phase_levels,
        case_id=f"{model.model_id}_linear_2",
    )
    mapped_output = _linear(mapped_second_weight, mapped_activation, model.second_bias)

    layer_errors = [
        _layer_error_report(
            layer_id="linear_1",
            layer_type="linear",
            baseline=baseline_first_linear,
            mapped=mapped_first_linear,
            hrm_mapped=True,
            classical_activation=False,
            mapping_mode=first_mode,
            weight_relative_error=first_weight_error,
        ),
        _layer_error_report(
            layer_id="relu_1",
            layer_type="classical_relu",
            baseline=baseline_activation,
            mapped=mapped_activation,
            hrm_mapped=False,
            classical_activation=True,
            mapping_mode="classical_relu_outside_optical_mesh",
            weight_relative_error=None,
        ),
        _layer_error_report(
            layer_id="linear_2",
            layer_type="linear",
            baseline=baseline_output,
            mapped=mapped_output,
            hrm_mapped=True,
            classical_activation=False,
            mapping_mode=second_mode,
            weight_relative_error=second_weight_error,
        ),
    ]
    output_error = _relative_vector_error(baseline_output, mapped_output)
    return {
        "modelId": model.model_id,
        "description": model.description,
        "inputDimension": len(model.input_vector),
        "hiddenDimension": len(model.first_bias),
        "outputDimension": len(model.second_bias),
        "layerCount": 3,
        "linearLayerCount": 2,
        "classicalActivationCount": 1,
        "opticalNonlinearityImplemented": False,
        "biasHandling": "classical_bias_addition_outside_optical_mesh",
        "activationHandling": "classical_relu_outside_optical_mesh",
        "inputVector": _round_vector(model.input_vector),
        "baselineOutput": _round_vector(baseline_output),
        "mappedOutput": _round_vector(mapped_output),
        "outputRelativeError": round(output_error, 15),
        "layerWiseErrors": layer_errors,
        "cumulativeError": round(output_error, 15),
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _mapped_weight_matrix(weight: Matrix, phase_levels: int, case_id: str) -> tuple[Matrix, float, str]:
    rows = len(weight)
    cols = len(weight[0]) if weight else 0
    svd = svd_decompose(weight)
    scale = max(svd.singular_values) if svd.singular_values else 0.0
    if rows == cols:
        model = build_mesh_transfer_model(weight, phase_levels=phase_levels)
        mapped = scalar_multiply(model.transfer_matrix, scale)
        return mapped, relative_frobenius_error(weight, mapped), "abstract_square_real_mesh"
    model = build_rectangular_mesh_transfer_model(weight, case_id=case_id, phase_levels=phase_levels)
    mapped = scalar_multiply(model.transfer_matrix, scale)
    return mapped, relative_frobenius_error(weight, mapped), "abstract_rectangular_orthogonal_completion_mesh"


def _linear(weight: Matrix, vector: List[float], bias: List[float]) -> List[float]:
    column = [[value] for value in vector]
    product = matmul(weight, column)
    return [row[0] + bias[index] for index, row in enumerate(product)]


def _relu(vector: List[float]) -> List[float]:
    return [max(0.0, value) for value in vector]


def _relative_vector_error(target: List[float], candidate: List[float]) -> float:
    numerator = math.sqrt(sum((left - right) ** 2 for left, right in zip(target, candidate)))
    denominator = math.sqrt(sum(value * value for value in target))
    if denominator <= 1e-12:
        return 0.0 if numerator <= 1e-12 else math.inf
    return numerator / denominator


def _layer_error_report(
    layer_id: str,
    layer_type: str,
    baseline: List[float],
    mapped: List[float],
    hrm_mapped: bool,
    classical_activation: bool,
    mapping_mode: str,
    weight_relative_error: float | None,
) -> dict:
    return {
        "layerId": layer_id,
        "layerType": layer_type,
        "hrmMapped": hrm_mapped,
        "classicalActivation": classical_activation,
        "mappingMode": mapping_mode,
        "baselineOutput": _round_vector(baseline),
        "mappedOutput": _round_vector(mapped),
        "relativeError": round(_relative_vector_error(baseline, mapped), 15),
        "weightRelativeError": None if weight_relative_error is None else round(weight_relative_error, 15),
        "opticalNonlinearityImplemented": False,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _model_summary(model: dict) -> dict:
    return {
        "modelId": model["modelId"],
        "outputRelativeError": model["outputRelativeError"],
        "cumulativeError": model["cumulativeError"],
    }


def _layer_summary(layer: dict) -> dict:
    return {
        "modelId": layer["modelId"],
        "layerId": layer["layerId"],
        "layerType": layer["layerType"],
        "relativeError": layer["relativeError"],
        "mappingMode": layer["mappingMode"],
    }


def _round_vector(vector: List[float]) -> List[float]:
    return [round(value, 12) for value in vector]
