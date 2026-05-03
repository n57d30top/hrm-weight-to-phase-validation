# HRM Weight-to-Phase Validation

[![CI](https://github.com/n57d30top/hrm-weight-to-phase-validation/actions/workflows/ci.yml/badge.svg)](https://github.com/n57d30top/hrm-weight-to-phase-validation/actions/workflows/ci.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-future--work--only-blue)
![Hardware validated](https://img.shields.io/badge/hardware_validated-false-red)

Simulation-gated validation ladder for HRM neural weight-to-phase mapping.

This repository explores whether selected neural-network weight matrices can be
mapped into HRM-style photonic transfer-function candidates using deterministic
simulation, abstract phase/coupler parameterization, perturbation testing, and
synthetic calibration gates.

## What This Is

This is a small, dependency-free research harness for one specific question:

Can selected neural-network weight matrices be translated into HRM-style
photonic transfer-function candidates and evaluated along explicit evidence
stages?

The current pipeline covers:

- deterministic test weight matrix generation
- compact SVD reconstruction
- passive singular-value normalization
- abstract real-valued mesh approximation
- abstract phase/coupler parameter records
- deterministic perturbation simulation
- synthetic/oracle calibration simulation
- evidence gates for foundry models, measured transfer matrices, and hardware
  benchmarks
- generated JSON reports and SHA-256 artifact hashes

## What This Is Not

This repository does not claim:

- hardware-native intelligence
- autonomous cognition
- quantum consciousness
- power-free computation
- quantum advantage
- foundry calibration
- measured hardware validation
- measured transfer matrices
- production inference readiness
- an end-to-end hardware benchmark
- a hardware readiness improvement for another project

The current evidence is limited to simulation and synthetic calibration.

## Current Stage Status

| Stage | Status | Evidence Level | Meaning |
| --- | --- | --- | --- |
| 0 | complete | theoretical_extension | Future-work specification and claim boundaries exist. |
| 1 | complete | numerical_simulation | A deterministic SVD mapping demo reconstructs the normalized target. |
| 2 | complete | abstract_mesh_simulation | Abstract phase/coupler parameterization exists for the small square demo case. |
| 3 | complete | uncalibrated_perturbation_simulation | Deterministic perturbation models report error deltas. |
| 4 | complete | synthetic_calibration_simulation | Simulation-only calibration uses a synthetic/oracle target. |
| 5 | blocked | foundry_calibration_gate | Requires foundry-calibrated device models or S-parameters. |
| 6 | blocked | measured_transfer_matrix_gate | Requires measured HRM transfer-matrix artifacts with provenance. |
| 7 | blocked | hardware_benchmark_gate | Requires an end-to-end measured hardware inference benchmark package. |

Blocked gates are successful schema outcomes. They identify missing evidence;
they are not completed hardware milestones.

## How To Reproduce

Requirements:

- Python 3.10 or newer
- `jq`
- `sha256sum`

Install the local package:

```bash
python3 -m pip install -e .
```

Run the full validation check:

```bash
make check
```

Equivalent manual commands:

```bash
python3 scripts/run_hrm_neural_mapping_demo.py
python3 scripts/run_hrm_neural_validation_ladder.py
python3 -m unittest discover -s tests -v
jq empty docs/future-work/evidence-ledger.json
jq empty reports/future-work/hrm-neural-mapping/validation-ladder-summary.json
sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256
git diff --check
```

## Evidence Ladder

The generated ladder is intentionally split into early simulation stages and
late evidence gates.

Stages 0-4 are reproducible local simulation/future-work artifacts. Stages 5-7
remain blocked until external evidence is supplied:

- Stage 5 requires foundry-calibrated device models or equivalent S-parameters.
- Stage 6 requires measured HRM transfer matrices with provenance.
- Stage 7 requires measured end-to-end hardware benchmark evidence.

The summary-level claim flags remain false:

```text
hardwareValidated=false
foundryCalibrated=false
measuredTransferMatrixAvailable=false
productionInferenceReady=false
```

## Reports

Generated reports are written to:

```text
reports/future-work/hrm-neural-mapping/
```

Key files:

- `stage-0-specification.json`
- `stage-1-svd-demo.json`
- `stage-2-mesh-constrained.json`
- `stage-3-perturbation-model.json`
- `stage-3-perturbation-sweep.json`
- `stage-3-sweep-analysis.json`
- `stage-4-simulated-calibration.json`
- `stage-4-calibration-sweep.json`
- `stage-4-calibration-analysis.json`
- `stage-5-foundry-calibration-gate.json`
- `stage-6-measured-transfer-matrix-gate.json`
- `stage-7-hardware-benchmark-gate.json`
- `validation-ladder-summary.json`
- `ARTIFACTS.sha256`

The evidence ledger is written to:

```text
docs/future-work/evidence-ledger.json
```

## Stage 2 Interpretation

Stage 2 is complete only as an abstract mesh simulation.

It implements deterministic quantized Givens rotations and abstract
phase/coupler setting records for the current small square demo matrix. It does
not implement a real HRM layout, a foundry-calibrated photonic mesh, a measured
transfer matrix, or a production phase synthesis pipeline.

Current Stage 2 scope:

- small deterministic matrix
- square matrix only
- real-valued orthogonal approximation
- no complex unitary mesh
- no rectangular neural layer support
- no Clements or Reck physical interferometer layout
- no foundry layout synthesis
- no physical phase synthesis
- no physical coupler synthesis

Important Stage 2 flags:

```text
abstractPhaseParameterizationImplemented=true
abstractCouplerParameterizationImplemented=true
physicalPhaseSynthesisImplemented=false
physicalCouplerSynthesisImplemented=false
foundryLayoutSynthesisImplemented=false
realChipMesh=false
hardwareValidated=false
```

## Stage 4 Interpretation

Stage 4 is synthetic/oracle calibration. It improves a simulated estimate
against a target that is available inside the simulation.

Important Stage 4 flags:

```text
calibrationUsesMeasuredData=false
calibrationUsesSyntheticTarget=true
oracleTargetAvailableInSimulation=true
hardwareCalibrationClaimed=false
measuredTransferMatrixAvailable=false
```

The supplemental Stage 4 calibration sweep report varies synthetic calibration
parameters one at a time, including initial noise, learning rate, calibration
iterations, and mesh phase levels. The companion analysis report summarizes
best/worst cases, improvement ratios, convergence status, and failure cases.
Both reports remain simulation-only and do not claim hardware calibration.

## Stage 3 Sweep Report

The supplemental Stage 3 sweep report evaluates one perturbation parameter at a
time using fixed seeds. It covers phase quantization bits, phase-noise sigma,
insertion loss, coupler imbalance, thermal drift proxy, and detector-noise
placeholder values.

The sweep is still uncalibrated simulation. It does not change any hardware
evidence flags and does not claim physical accuracy.

The companion Stage 3 sweep analysis report summarizes the sweep rows with
per-parameter min/max error, max error delta, best/worst rows, sensitivity
ranking, monotonicity notes, explicit limitations, and an all-perturbations-off
control summary. The one-parameter sweeps keep the fixed baseline perturbation
configuration enabled unless the swept parameter overrides one dimension, so
zero-valued rows are not global no-perturbation controls.

## Blocked Hardware Gates

The blocked stages are the boundary between simulation and hardware evidence.

- Stage 5 is blocked by `no_foundry_calibrated_device_model`.
- Stage 6 is blocked by `no_measured_hrm_transfer_matrix`.
- Stage 7 is blocked by `no_end_to_end_hardware_benchmark`.

These blockers should remain until the required external artifacts exist.

## Claim Boundary

This future-work track does not improve hardware readiness and does not claim
hardware-native intelligence, autonomous cognition, quantum consciousness,
power-free computation, quantum advantage, hardware validation, foundry
calibration, measured transfer matrices, production inference readiness, or a
completed hardware benchmark.

## Roadmap

Near-term:

- keep CI green for report generation, JSON validation, hashes, and tests
- maintain and extend deterministic Stage 3 perturbation sweeps and analysis
- maintain and extend Stage 4 calibration sensitivity sweeps
- document accepted manifest schemas for Stage 5-7 evidence inputs

Later, only when evidence exists:

- connect Stage 5 to foundry-calibrated model artifacts
- connect Stage 6 to measured transfer-matrix artifacts
- connect Stage 7 to an end-to-end measured hardware benchmark

## License

MIT.
