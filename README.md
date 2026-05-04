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
- rectangular neural layer simulation via orthogonal completion and rectangular
  singular-value transfer cores
- complex-valued unitary-factor simulation with phase-aware error metrics
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
| 2 | complete | abstract_mesh_simulation | Abstract phase/coupler parameterization exists for the square demo case, with supplemental rectangular and complex/unitary support. |
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
- `complex-unitary-mesh-support.json`
- `layer-stack-inference-demo.json`
- `layer-stack-error-analysis.json`
- `matrix-family-benchmark.json`
- `matrix-family-analysis.json`
- `model-weight-import-demo.json`
- `model-weight-eligibility-analysis.json`
- `rectangular-matrix-support.json`
- `review-pack-summary.json`
- `review-pack.md`
- `review-pack-metrics.csv`
- `review-pack-stage-table.md`
- `review-pack-limitations.md`
- `scaling-benchmark.json`
- `scaling-analysis.json`
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

Schema documentation for future hardware evidence gates:

- `docs/future-work/foundry-calibrated-device-model-schema.md`
- `docs/future-work/measured-transfer-matrix-fixture-schema.md`
- `docs/future-work/hardware-benchmark-acceptance-schema.md`
- `docs/future-work/model-weight-manifest-schema.md`

## Stage 2 Interpretation

Stage 2 is complete only as an abstract mesh simulation.

It implements deterministic quantized Givens rotations and abstract
phase/coupler setting records for the current small square demo matrix,
supplemental rectangular-matrix simulation, and supplemental complex/unitary
factor simulation. It does not implement a real HRM layout, a foundry-calibrated
photonic mesh, a measured transfer matrix, or a production phase synthesis
pipeline.

Current Stage 2 scope:

- small deterministic square main demo matrix
- rectangular supplemental cases for 6x4, 4x6, and rank-deficient 5x3 matrices
- complex/unitary supplemental cases for 2x2 and 4x4 complex matrices
- main demo remains a real-valued orthogonal approximation
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

## Complex/Unitary Mesh Support

The supplemental report `complex-unitary-mesh-support.json` extends the
simulation-only mapping path to complex-valued matrices and unitary-factor
handling.

The representation is:

```text
complex W
-> complex QR unitary factorization
-> abstract phase-quantized unitary factor
-> residual factor reconstruction
-> relative, phase-aware, and amplitude-aware error metrics
```

This is not a full complex SVD pipeline and not a physical phase-synthesis
implementation. It does not define a Clements/Reck physical interferometer
layout, a foundry layout, a measured transfer matrix, or a production inference
path.

The report includes a 2x2 unitary-like case, a deterministic 4x4 complex case,
and a phase-dominant 4x4 case. All hardware evidence flags remain false.

## Matrix-Family Benchmark

The supplemental reports `matrix-family-benchmark.json` and
`matrix-family-analysis.json` compare the current abstract mapping paths across
small deterministic matrix families.

The benchmark covers:

- identity 4x4
- diagonal dynamic-range 4x4
- low-rank 6x4
- rank-deficient 5x3
- ill-conditioned 4x4
- sparse-like 6x6
- dense seeded 4x4
- rectangular tall 8x4
- rectangular wide 4x8
- complex phase-dominant 4x4
- unitary-like 4x4

Square real cases use the abstract real-valued mesh path, rectangular cases use
orthogonal completion and rectangular singular-value transfer cores, and complex
cases use complex QR unitary-factor handling. The analysis report summarizes
best/worst cases, maximum error delta, average mesh-constrained error, and
rankings by reconstruction error and condition-sensitivity proxy.

This remains a small deterministic simulation benchmark. It is not a sampled
training distribution, not a large-model benchmark, not a physical layout, not
a measured transfer matrix, and not a hardware benchmark.

## Multi-Layer Toy Inference

The supplemental reports `layer-stack-inference-demo.json` and
`layer-stack-error-analysis.json` compose mapped linear layers into tiny
deterministic toy inference paths.

The primary model is:

```text
input dimension 4
-> Linear 4x6 mapped through the abstract HRM simulation path
-> classical ReLU outside the optical mesh
-> Linear 6x3 mapped through the abstract HRM simulation path
-> output dimension 3
```

The report also includes a rectangular projection chain:

```text
4 -> 8 -> classical ReLU -> 4
```

Only linear layers are mapped through the abstract HRM transfer simulation.
Bias additions remain classical outside the optical mesh. ReLU remains a
classical activation outside the optical mesh. No optical nonlinearity,
full neural-network acceleration, production inference readiness, timing,
energy, measured transfer matrix, or hardware validation is claimed.

The analysis report identifies the worst layer by relative error, summarizes
cumulative error trends, and records activation-boundary notes for the toy
models.

## Model Weight Manifest Import

The supplemental reports `model-weight-import-demo.json` and
`model-weight-eligibility-analysis.json` validate a deterministic JSON manifest
for external model-weight artifacts.

The fixture model is:

```text
tiny_mlp_manifest_4_6_3
-> rectangular_linear 6x4 with bias and classical ReLU after the layer
-> rectangular_linear 3x6 with bias
```

The importer checks required manifest fields, ISO export date, repository-
relative artifact references, SHA-256 hashes, dtype metadata, and layer shapes.
It rejects absolute paths, local path fragments, missing fields, and wrong
hashes. PyTorch is not a required dependency; a future exporter can generate
this manifest format externally.

Mapping eligibility is schema-driven:

- `linear`, `rectangular_linear`, and supported `complex_linear` layers are
  eligible for abstract simulation mapping.
- `convolution`, `attention_softmax`, and `embedding` are ineligible and not
  implemented.
- bias additions, activations, normalization, and other non-linear operations
  remain classical outside the optical mesh.

This is an import and eligibility layer only. It does not execute a PyTorch
model, does not accelerate a full model, does not implement optical
nonlinearities, and does not claim hardware validation.

## Scaling Benchmark

The supplemental reports `scaling-benchmark.json` and `scaling-analysis.json`
test how the simulation-only mapping behaves as matrix sizes and layer shapes
grow within a CI-light deterministic suite.

The suite includes:

- square 4x4, 8x8, and 16x16 real matrices
- rectangular tall 8x4 and 16x8 matrices
- rectangular wide 4x8 and 8x16 matrices
- low-rank 16x8 and rank-deficient 12x6 matrices
- dense seeded 16x16 matrix
- phase-dominant complex 8x8 matrix

The analysis reports best/worst cases, average and maximum mesh-constrained
error, error by shape family, and error by matrix size. `estimatedOperationScale`
is a deterministic size proxy only. It is not a runtime measurement and not a
hardware performance claim.

The scaling reports do not claim hardware latency, hardware throughput, hardware
energy efficiency, accelerator performance, foundry calibration, measured
transfer matrices, or production inference readiness.

## Review Pack

The review pack collects the existing simulation-only reports into concise
review artifacts:

- `review-pack-summary.json`
- `review-pack.md`
- `review-pack-metrics.csv`
- `review-pack-stage-table.md`
- `review-pack-limitations.md`

The Markdown report states: "This is a simulation-only review pack. It is not
hardware evidence."

The review pack summarizes stage status, supplemental report coverage, key
reconstruction and error metrics, perturbation sensitivity, synthetic
calibration improvement, blocked hardware gates, limitations, and a reviewer
checklist. It does not add new physics, does not change any report metric, and
does not unblock Stage 5, Stage 6, or Stage 7.

## Rectangular Matrix Support

The supplemental report `rectangular-matrix-support.json` extends the
simulation-only mapping path from square toy matrices to rectangular neural
layer shapes.

The main Stage 2 demo remains small square, and supplemental rectangular support exists for 6x4, 4x6, and rank-deficient 5x3 cases.

The representation is:

```text
W in R^(m x n)
-> compact SVD
-> full left/right orthogonal completion
-> rectangular Sigma transfer core
-> abstract square left/right mesh approximations
```

This is a numerical simulation convention. It uses padding through orthogonal
completion and a zero-padded rectangular singular-value core. It is not a
physical HRM layout, not a Clements/Reck interferometer layout, not a measured
transfer matrix, and not a production phase synthesis pipeline.

There is still no physical complex/unitary mesh layout, still no Clements/Reck
physical interferometer layout, still no foundry layout synthesis, and still no
hardware validation.

The report includes tall, wide, and rank-deficient deterministic cases and
keeps all hardware evidence flags false.

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

Stage 5, Stage 6, and Stage 7 schema docs define required fields for future
evidence packages. They are not evidence, do not contain foundry or measured
data, and do not unblock any hardware gate.

Stage 5 gates validate foundry evidence class, relative artifact references,
hashes, source date format, non-empty provenance, uncertainty, source, and
claim-boundary fields.

Stage 6 and Stage 7 gates validate artifact references, hashes, date format,
allowed matrix conventions, non-empty provenance fields, and the Stage 7
dependency on a completed Stage 6 measured-transfer-matrix gate.

## Claim Boundary

This future-work track does not improve hardware readiness and does not claim
hardware-native intelligence, autonomous cognition, quantum consciousness,
power-free computation, quantum advantage, hardware validation, foundry
calibration, measured transfer matrices, production inference readiness, or a
completed hardware benchmark.

## Roadmap

Completed alpha milestones:

- `v0.1.0-alpha.1`: public simulation-gated baseline.
- `v0.1.0-alpha.2`: deterministic Stage 3 perturbation sweeps and sensitivity analysis.
- `v0.1.0-alpha.3`: deterministic Stage 4 synthetic calibration sweeps and analysis.

Completed post-alpha.3 main work:

- foundry-calibrated device-model schema documented and enforced by Stage 5 gate acceptance criteria.
- foundry-calibrated manifest validation hardened with artifact, hash, source-date, evidence-class, provenance, uncertainty, and claim-boundary checks.
- measured-transfer-matrix fixture schema documented and enforced by Stage 6 gate acceptance criteria.
- hardware benchmark acceptance schema documented and enforced by Stage 7 gate acceptance criteria.
- measured-transfer-matrix manifest validation hardened with artifact, hash, date, convention, and provenance checks.
- hardware benchmark manifest validation hardened with artifact, hash, dependency, metric, characterization, and provenance checks.

Completed post-alpha.4 main work:

- rectangular matrix support added as a supplemental simulation report for tall, wide, and rank-deficient neural layer shapes.

Completed post-alpha.5 main work:

- complex/unitary support added as a supplemental simulation report for unitary-like, general complex, and phase-dominant cases.

Completed post-alpha.6 main work:

- matrix-family benchmark and analysis reports added for identity, dynamic-range, low-rank, rank-deficient, ill-conditioned, sparse-like, dense, rectangular, complex phase-dominant, and unitary-like deterministic cases.

Completed post-alpha.7 main work:

- multi-layer toy inference reports added for a 4-to-6-to-3 tiny MLP and a 4-to-8-to-4 projection chain, with classical ReLU boundaries and layer-wise/cumulative error reporting.

Completed post-alpha.8 main work:

- model-weight manifest import and eligibility analysis added with repo-relative artifact paths, SHA-256 validation, dtype/shape checks, and simulation-only mapping plans.

Completed post-alpha.9 main work:

- scaling and larger-layer benchmark reports added for square, rectangular, low-rank, rank-deficient, dense, and complex phase-dominant deterministic cases up to 16x16 and 8x16/16x8.

Completed post-alpha.10 main work:

- simulation-only review pack added with summary JSON, Markdown, metrics CSV, stage table, limitations, reviewer checklist, and hash-covered artifacts.

Near-term:

- keep CI green for report generation, JSON validation, hashes, and tests
- complex SVD pipeline
- release-candidate hardening

Later, only when evidence exists:

- supply real Stage 5 foundry-calibrated model artifacts
- connect Stage 6 to measured transfer-matrix artifacts
- connect Stage 7 to an end-to-end measured hardware benchmark

## License

MIT.
