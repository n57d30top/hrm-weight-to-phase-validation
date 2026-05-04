"""Simulation-only hardware design-space explorer for v0.2 planning."""

from __future__ import annotations

import math
from typing import Any, Dict, List


EVIDENCE_LEVEL = "hardware_design_space_sweep_simulation"
ANALYSIS_EVIDENCE_LEVEL = "hardware_design_space_analysis"
CLAIM_BOUNDARY = (
    "Simulation-only design-space exploration; this does not claim real hardware latency, real hardware "
    "energy efficiency, hardware validation, foundry calibration, measured transfer matrices, production "
    "inference readiness, quantum advantage, hardware-native intelligence, or power-free computation."
)


def run_hardware_design_space_sweep_report() -> Dict[str, Any]:
    rows = [_sweep_row(bits, loss, noise, interval) for bits in [4, 6, 8, 10] for loss in [0.1, 0.5, 1.0] for noise in [0.002, 0.01, 0.03] for interval in [1_000, 10_000, 100_000]]
    return {
        "id": "hardware-design-space-sweep",
        "title": "Simulation-only hardware design-space sweep",
        "stage": 2,
        "evidenceLevel": EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "rowCount": len(rows),
        "phaseBitsValues": [4, 6, 8, 10],
        "lossDbValues": [0.1, 0.5, 1.0],
        "phaseNoiseSigmaRadValues": [0.002, 0.01, 0.03],
        "calibrationIntervalValues": [1_000, 10_000, 100_000],
        "parametricEstimateOnly": True,
        "measuredHardwarePerformance": False,
        "noHardwarePerformanceClaim": True,
        "rows": rows,
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
            "transfer_matrix_ingestion_sandbox",
            "measured_transfer_matrix_gate",
            "hardware_benchmark_gate",
        ],
    }


def run_hardware_design_space_analysis_report() -> Dict[str, Any]:
    sweep = run_hardware_design_space_sweep_report()
    rows = sweep["rows"]
    by_error = sorted(rows, key=lambda row: (row["estimatedOutputRelativeError"], row["estimatedLatencyProxy"], row["estimatedEnergyProxy"]))
    by_bottleneck = _bottleneck_ranking(rows)
    pareto = _pareto_candidates(rows)
    return {
        "id": "hardware-design-space-analysis",
        "title": "Simulation-only hardware design-space analysis",
        "stage": 2,
        "evidenceLevel": ANALYSIS_EVIDENCE_LEVEL,
        "stageStatus": "complete",
        "rowCount": sweep["rowCount"],
        "bestErrorCandidate": by_error[0],
        "worstErrorCandidate": by_error[-1],
        "paretoCandidateCount": len(pareto),
        "paretoCandidates": pareto,
        "bottleneckRanking": by_bottleneck,
        "designSpaceNotes": [
            "phase resolution dominates low-bit configurations",
            "phase noise dominates high-noise configurations",
            "calibration interval is a deterministic planning proxy",
            "latency and energy proxies are not measured hardware performance",
        ],
        "parametricEstimateOnly": True,
        "measuredHardwarePerformance": False,
        "noHardwarePerformanceClaim": True,
        "claimBoundary": CLAIM_BOUNDARY,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
        "blockers": sweep["blockers"],
        "nextValidationGates": sweep["nextValidationGates"],
    }


def render_hardware_design_space_pareto(report: Dict[str, Any]) -> str:
    lines = [
        "# Hardware Design-Space Pareto Candidates",
        "",
        "This is a simulation-only design-space report. It is not measured hardware performance.",
        "",
        "| Candidate | Error | Latency Proxy | Energy Proxy | Phase Bits | Loss dB | Noise | Calibration Interval |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["paretoCandidates"]:
        lines.append(
            f"| `{row['candidateId']}` | {row['estimatedOutputRelativeError']} | "
            f"{row['estimatedLatencyProxy']} | {row['estimatedEnergyProxy']} | "
            f"{row['phaseResolutionBits']} | {row['insertionLossDb']} | "
            f"{row['phaseNoiseSigmaRad']} | {row['calibrationIntervalInferences']} |"
        )
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        report["claimBoundary"],
        "",
    ])
    return "\n".join(lines)


def _sweep_row(bits: int, loss: float, noise: float, interval: int) -> Dict[str, Any]:
    baseline = 0.019640136609986
    quantization = 1.5 / (2 ** bits)
    loss_error = loss * 0.02
    noise_error = noise * 2.0
    calibration_error = 2.5 / math.sqrt(interval)
    error = baseline + quantization + loss_error + noise_error + calibration_error
    latency_proxy = 1.0 + bits * 0.12 + (100_000 / interval) * 0.04
    energy_proxy = 1.0 + loss * 0.7 + bits * 0.08 + (100_000 / interval) * 0.03
    contributors = {
        "phase_quantization": quantization,
        "insertion_loss": loss_error,
        "phase_noise": noise_error,
        "calibration_interval": calibration_error,
    }
    return {
        "candidateId": f"bits{bits}_loss{str(loss).replace('.', 'p')}_noise{str(noise).replace('.', 'p')}_cal{interval}",
        "phaseResolutionBits": bits,
        "insertionLossDb": loss,
        "phaseNoiseSigmaRad": noise,
        "calibrationIntervalInferences": interval,
        "estimatedOutputRelativeError": round(error, 15),
        "estimatedLatencyProxy": round(latency_proxy, 6),
        "estimatedEnergyProxy": round(energy_proxy, 6),
        "dominantBottleneck": max(contributors, key=contributors.get),
        "parametricEstimateOnly": True,
        "measuredHardwarePerformance": False,
        "hardwareValidated": False,
        "foundryCalibrated": False,
        "measuredTransferMatrixAvailable": False,
        "productionInferenceReady": False,
    }


def _pareto_candidates(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    pareto = []
    for row in rows:
        dominated = any(
            other is not row
            and other["estimatedOutputRelativeError"] <= row["estimatedOutputRelativeError"]
            and other["estimatedLatencyProxy"] <= row["estimatedLatencyProxy"]
            and other["estimatedEnergyProxy"] <= row["estimatedEnergyProxy"]
            and (
                other["estimatedOutputRelativeError"] < row["estimatedOutputRelativeError"]
                or other["estimatedLatencyProxy"] < row["estimatedLatencyProxy"]
                or other["estimatedEnergyProxy"] < row["estimatedEnergyProxy"]
            )
            for other in rows
        )
        if not dominated:
            pareto.append(row)
    return sorted(pareto, key=lambda item: (item["estimatedOutputRelativeError"], item["estimatedLatencyProxy"]))[:12]


def _bottleneck_ranking(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["dominantBottleneck"]] = counts.get(row["dominantBottleneck"], 0) + 1
    return [
        {"bottleneck": bottleneck, "count": count}
        for bottleneck, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]
