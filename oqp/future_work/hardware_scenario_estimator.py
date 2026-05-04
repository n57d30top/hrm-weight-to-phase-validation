"""Parametric hardware scenario estimates for HRM neural future work.

The estimates in this module are deterministic planning calculations. They are
not measured hardware performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


EVIDENCE_LEVEL = "parametric_hardware_scenario_estimate"
ANALYSIS_EVIDENCE_LEVEL = "parametric_hardware_scenario_analysis"
WARNING = "These are parametric estimates, not measured hardware performance."
CLAIM_BOUNDARY = (
    "Parametric estimate only; no real hardware latency, real hardware energy efficiency, "
    "hardware validation, foundry calibration, measured transfer matrices, production inference "
    "readiness, quantum advantage, hardware-native intelligence, or power-free computation is claimed."
)


@dataclass(frozen=True)
class ScenarioInput:
    scenario_id: str
    optical_propagation_delay_ps: float
    modulator_latency_ns: float
    detector_latency_ns: float
    dac_latency_ns: float
    adc_latency_ns: float
    control_loop_latency_ns: float
    calibration_interval_inferences: int
    laser_power_mw: float
    modulator_energy_pj: float
    detector_energy_pj: float
    dac_adc_energy_pj: float
    thermal_tuning_power_mw: float
    insertion_loss_db: float
    mesh_size: int
    batch_size: int
    assumptions: List[str]
    limitations: List[str]


def deterministic_hardware_scenarios() -> List[ScenarioInput]:
    return [
        ScenarioInput(
            "ideal_optical_core_only",
            25.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1_000_000,
            5.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.5,
            64,
            1,
            ["optical core only", "no readout or control stack included"],
            ["not an end-to-end estimate", "not measured hardware performance"],
        ),
        ScenarioInput(
            "optical_core_plus_readout",
            25.0,
            0.0,
            2.0,
            0.0,
            4.0,
            0.0,
            250_000,
            8.0,
            0.0,
            0.35,
            1.2,
            0.0,
            1.2,
            64,
            1,
            ["detector and ADC readout included", "control stack excluded"],
            ["readout parameters are assumed", "not measured hardware performance"],
        ),
        ScenarioInput(
            "full_electro_optical_control_stack",
            25.0,
            5.0,
            2.0,
            6.0,
            4.0,
            15.0,
            100_000,
            12.0,
            0.8,
            0.35,
            1.2,
            2.0,
            2.0,
            64,
            1,
            ["DAC, modulator, detector, ADC, and control-loop terms included"],
            ["control-loop values are assumed", "not a hardware benchmark"],
        ),
        ScenarioInput(
            "pessimistic_lossy_mesh",
            40.0,
            8.0,
            4.0,
            8.0,
            6.0,
            25.0,
            50_000,
            20.0,
            1.2,
            0.6,
            1.8,
            5.0,
            8.0,
            128,
            1,
            ["lossy larger mesh with higher control overhead"],
            ["loss and control assumptions are not calibrated to hardware"],
        ),
        ScenarioInput(
            "calibration_heavy_operation",
            30.0,
            6.0,
            3.0,
            8.0,
            5.0,
            40.0,
            1_000,
            15.0,
            1.0,
            0.5,
            1.5,
            4.0,
            3.0,
            96,
            1,
            ["frequent calibration amortized over a small inference interval"],
            ["calibration cost is a planning proxy only", "not measured hardware performance"],
        ),
    ]


def run_hardware_scenario_estimates_report() -> Dict[str, Any]:
    rows = [_scenario_estimate(scenario) for scenario in deterministic_hardware_scenarios()]
    return {
        "id": "hardware-scenario-estimates",
        "title": "Parametric hardware scenario estimates",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "scenarioCount": len(rows),
        "parametricEstimateOnly": True,
        "measuredHardwarePerformance": False,
        "warning": WARNING,
        "scenarios": rows,
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": [
            "no_measured_hardware_latency",
            "no_measured_hardware_energy",
            "no_foundry_calibrated_device_model",
            "no_measured_transfer_matrix",
        ],
        "nextValidationGates": [
            "hardware_requirements_generator",
            "error_budget_report",
            "hardware_benchmark_gate",
        ],
    }


def run_hardware_scenario_analysis_report() -> Dict[str, Any]:
    estimates = run_hardware_scenario_estimates_report()
    rows = estimates["scenarios"]
    best_latency = min(rows, key=lambda row: row["estimatedEndToEndLatencyNs"])
    worst_latency = max(rows, key=lambda row: row["estimatedEndToEndLatencyNs"])
    best_energy = min(rows, key=lambda row: row["estimatedEnergyPerInferencePj"])
    worst_energy = max(rows, key=lambda row: row["estimatedEnergyPerInferencePj"])
    return {
        "id": "hardware-scenario-analysis",
        "title": "Parametric hardware scenario bottleneck analysis",
        "stage": 2,
        "evidenceLevel": ANALYSIS_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "scenarioCount": estimates["scenarioCount"],
        "parametricEstimateOnly": True,
        "measuredHardwarePerformance": False,
        "warning": WARNING,
        "bestLatencyScenario": _scenario_summary(best_latency),
        "worstLatencyScenario": _scenario_summary(worst_latency),
        "bestEnergyScenario": _scenario_summary(best_energy),
        "worstEnergyScenario": _scenario_summary(worst_energy),
        "dominantBottleneckByScenario": [
            {
                "scenarioId": row["scenarioId"],
                "dominantLatencyContributor": row["dominantLatencyContributor"],
                "dominantEnergyContributor": row["dominantEnergyContributor"],
            }
            for row in rows
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": estimates["blockers"],
        "nextValidationGates": estimates["nextValidationGates"],
    }


def _scenario_estimate(scenario: ScenarioInput) -> Dict[str, Any]:
    optical_latency = scenario.optical_propagation_delay_ps / 1000.0
    readout_latency = scenario.detector_latency_ns + scenario.adc_latency_ns
    control_latency = scenario.modulator_latency_ns + scenario.dac_latency_ns + scenario.control_loop_latency_ns
    end_to_end_latency = optical_latency + readout_latency + control_latency
    active_energy = scenario.mesh_size * (
        scenario.modulator_energy_pj
        + scenario.detector_energy_pj
        + scenario.dac_adc_energy_pj
    )
    optical_energy = scenario.laser_power_mw * end_to_end_latency
    thermal_energy = scenario.thermal_tuning_power_mw * end_to_end_latency
    calibration_amortization = _calibration_amortization_pj(scenario)
    loss_penalty = max(1.0, 1.0 + scenario.insertion_loss_db / 20.0)
    energy = (active_energy + optical_energy + thermal_energy + calibration_amortization) * loss_penalty
    latency_components = {
        "optical_core": optical_latency,
        "readout": readout_latency,
        "control": control_latency,
    }
    energy_components = {
        "active_io": active_energy,
        "laser": optical_energy,
        "thermal_tuning": thermal_energy,
        "calibration_amortization": calibration_amortization,
    }
    return {
        "scenarioId": scenario.scenario_id,
        "parametricEstimateOnly": True,
        "measuredHardwarePerformance": False,
        "inputParameters": {
            "opticalPropagationDelayPs": scenario.optical_propagation_delay_ps,
            "modulatorLatencyNs": scenario.modulator_latency_ns,
            "detectorLatencyNs": scenario.detector_latency_ns,
            "dacLatencyNs": scenario.dac_latency_ns,
            "adcLatencyNs": scenario.adc_latency_ns,
            "controlLoopLatencyNs": scenario.control_loop_latency_ns,
            "calibrationIntervalInferences": scenario.calibration_interval_inferences,
            "laserPowerMw": scenario.laser_power_mw,
            "modulatorEnergyPj": scenario.modulator_energy_pj,
            "detectorEnergyPj": scenario.detector_energy_pj,
            "dacAdcEnergyPj": scenario.dac_adc_energy_pj,
            "thermalTuningPowerMw": scenario.thermal_tuning_power_mw,
            "insertionLossDb": scenario.insertion_loss_db,
            "meshSize": scenario.mesh_size,
            "batchSize": scenario.batch_size,
        },
        "estimatedOpticalCoreLatencyNs": round(optical_latency, 6),
        "estimatedReadoutLatencyNs": round(readout_latency, 6),
        "estimatedControlLatencyNs": round(control_latency, 6),
        "estimatedEndToEndLatencyNs": round(end_to_end_latency, 6),
        "estimatedEnergyPerInferencePj": round(energy / scenario.batch_size, 6),
        "calibrationAmortizationPj": round(calibration_amortization, 6),
        "dominantLatencyContributor": max(latency_components, key=latency_components.get),
        "dominantEnergyContributor": max(energy_components, key=energy_components.get),
        "assumptions": scenario.assumptions,
        "limitations": scenario.limitations,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _calibration_amortization_pj(scenario: ScenarioInput) -> float:
    calibration_energy = scenario.mesh_size * (scenario.modulator_energy_pj + scenario.dac_adc_energy_pj) * 10.0
    return calibration_energy / max(1, scenario.calibration_interval_inferences)


def _scenario_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "scenarioId": row["scenarioId"],
        "estimatedEndToEndLatencyNs": row["estimatedEndToEndLatencyNs"],
        "estimatedEnergyPerInferencePj": row["estimatedEnergyPerInferencePj"],
        "parametricEstimateOnly": row["parametricEstimateOnly"],
        "measuredHardwarePerformance": row["measuredHardwarePerformance"],
    }
