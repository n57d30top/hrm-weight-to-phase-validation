# Addendum: Neural Weight-to-Phase Mapping for HRM Photonic Inference

## Claim Boundary

This addendum does not claim hardware-native intelligence, autonomous cognition,
quantum consciousness, power-free computation, or a demonstrated quantum
advantage.

It also does not claim that the current HRM design has been validated as a
neural-network accelerator in hardware.

Strict future-work boundaries:

- Do not claim hardware-native intelligence.
- Do not claim autonomous cognition.
- Do not claim quantum consciousness.
- Do not claim power-free computation.
- Do not claim quantum advantage.
- Do not claim production inference readiness.
- Do not claim hardware validation unless measured hardware data is present.
- Do not claim foundry calibration unless foundry-calibrated S-parameters or equivalent foundry device models are present.
- Do not claim measured transfer matrices unless real measured transfer-matrix artifacts are present.
- Do not promote this future-work track into the main hardware readiness score.
- Do not modify generated hardware evidence reports.
- Do not modify reports/node-alpha artifacts.
- Do not modify core quantum architecture claims.

This document describes a proposed, validation-gated compilation protocol for
mapping trained neural-network weight matrices to programmable photonic phase,
coupling, attenuation, and scaling settings in an HRM-style photonic mesh.

The proposed mapping should be interpreted as a theoretical and simulation-level
extension until supported by measured transfer matrices, calibrated device
models, packaging constraints, and end-to-end hardware benchmarks.

## Evidence Level

Current evidence level:

```text
theoretical_extension: true
simulation_protocol_defined: true
hardware_validated: false
measured_transfer_matrix_available: false
foundry_calibrated: false
production_inference_ready: false
```

This addendum is therefore suitable for future-work documentation, not for core
architecture readiness claims.

The current reproducible simulation-only demo report is:

```text
reports/future-work/hrm-neural-mapping/validation-ladder-summary.json
```

The current ladder demonstrates compact SVD reconstruction, passive
singular-value normalization, deterministic abstract mesh phase/coupler
parameterization, perturbation stress testing, and synthetic calibration. It
does not implement a real chip mesh, foundry-calibrated model, measured transfer
matrix, hardware calibration, or production inference path.

## 1. Hybrid Electro-Optical Inference Paradigm

An HRM-style photonic mesh would not run a neural network in the traditional
software sense.

Instead, selected linear layers of a neural network may be compiled into
physical optical transfer functions. During inference, optical propagation
through the configured mesh implements the corresponding linear transformation.

The system remains strictly hybrid:

| Subsystem | Role |
| --- | --- |
| Electronic control | Programs and stabilizes phase shifters, couplers, attenuators, and calibration states |
| Optical propagation | Implements the linear optical transfer function |
| Detectors and electronics | Perform readout, digitization, memory movement, non-linear activations, normalization, routing, and orchestration |
| Classical software | Handles model export, quantization, calibration, validation, scheduling, and error compensation |

The HRM mesh should therefore be treated as a candidate physical accelerator for
selected linear inference blocks, not as a self-contained artificial
intelligence system.

Optical propagation may provide low physical propagation latency for the optical
portion of the transform. End-to-end latency remains bounded by modulation,
detection, conversion, memory movement, thermal control, calibration cadence,
and orchestration overhead.

## 2. Technical Compilation Pipeline

The proposed mapping pipeline is:

```text
trained model layer
-> weight matrix extraction
-> normalization / quantization
-> matrix decomposition
-> photonic mesh parameter synthesis
-> calibration against transfer matrix
-> numerical validation
-> system-level benchmark
```

### 2.1 Export

Extract a trained weight matrix `W` from a model framework such as PyTorch or
TensorFlow.

Examples:

```text
linear layer:      y = W x + b
attention block:   QK^T, projection matrices, MLP projections
convolution:       lowered or transformed into equivalent matrix blocks
```

Bias terms, normalization, residual paths, and non-linear activations remain
outside the passive optical mesh unless separately implemented.

### 2.2 Normalization and Quantization

Normalize `W` to fit the supported optical dynamic range.

Required constraints include:

- maximum phase range
- minimum resolvable phase step
- coupler precision
- optical loss budget
- detector dynamic range
- DAC/ADC precision
- thermal drift
- calibration stability

The mapping must report the effective numerical precision, reconstruction
error, and end-to-end model accuracy impact.

### 2.3 Matrix Decomposition

For a dense linear layer, one candidate decomposition is:

```text
W = U Sigma V^dagger
```

where:

```text
U and V^dagger = unitary or approximately unitary transforms
Sigma          = diagonal singular-value scaling
```

In an interferometric photonic mesh, `U` and `V^dagger` may be mapped to
programmable interferometer meshes. `Sigma` may be mapped to attenuation,
normalization, input/output scaling, or explicitly characterized active gain
elements if available.

For passive meshes, singular values should be normalized into the available
optical range and represented using attenuation plus external electronic
scaling. Active gain is only inside the claim boundary if the gain mechanism is
explicitly modeled, characterized, and included in the noise, energy, stability,
and calibration budget.

### 2.4 Hardware Parameter Mapping

The decomposed factors are converted into physical control parameters:

- phase settings
- coupler settings
- attenuator settings
- input/output scaling factors
- calibration targets

The output of this stage should be a machine-readable configuration file, for
example:

```json
{
  "layer": "encoder.mlp.fc1",
  "shape": [768, 3072],
  "decomposition": "svd",
  "mesh": "hrm-interferometer-candidate",
  "evidenceLevel": "simulation_protocol",
  "hardwareValidated": false,
  "settings": {
    "phaseShifters": [],
    "couplers": [],
    "attenuators": [],
    "inputScale": 1.0,
    "outputScale": 1.0
  },
  "validation": {
    "targetRelativeError": null,
    "measuredRelativeError": null,
    "measuredTransferMatrix": null
  }
}
```

### 2.5 Calibration

A hardware implementation requires closed-loop calibration against the measured
physical transfer matrix.

Calibration must compensate for:

- fabrication variation
- thermal drift
- phase-shifter nonlinearity
- coupler imbalance
- insertion loss
- crosstalk
- detector noise
- wavelength dependence
- polarization sensitivity
- package-level instability

Until measured transfer matrices exist, calibration remains a simulation or
planning step.

### 2.6 Validation

Before claiming successful mapping, the following validation gates are required:

| Gate | Required measurement |
| --- | --- |
| Matrix reconstruction | Relative error between target `W` and reconstructed transfer matrix |
| Test-vector equivalence | Error over representative input vectors |
| Layer accuracy | Output deviation versus software layer |
| Model accuracy | End-to-end task accuracy delta |
| Drift stability | Error over time and temperature |
| Energy | Optical, electronic, DAC/ADC, and thermal control energy |
| Latency | Full system latency, not just optical propagation |
| Calibration cost | Time and compute required for recalibration |
| Robustness | Sensitivity to process, voltage, temperature, and optical noise |

A mapping is not considered hardware-validated until these gates are evaluated
on measured hardware or a foundry-calibrated device model.

## 3. Non-Goals

This addendum does not attempt to implement:

- autonomous cognition
- quantum consciousness
- hardware-native intelligence
- power-free inference
- complete neural-network execution inside passive optics
- training inside the HRM mesh
- non-linear activations inside the passive mesh
- memory or KV-cache inside the passive mesh
- production-ready AI acceleration

It only describes a possible mapping for selected linear inference blocks.

## 4. Relationship to Quantum Architecture

This addendum must not be confused with a claim of quantum neural computation.

The proposed mapping is primarily a classical photonic inference concept:

```text
classical neural-network weights
-> classical control parameters
-> photonic transfer function
-> detected classical output
```

If future work explores genuinely quantum degrees of freedom, that work must be
documented separately and assigned a distinct evidence level.

The terms "qubit", "quantum state", and "quantum advantage" should not be used
for this mapping unless a specific quantum-mechanical protocol, noise model,
measurement model, and validation path are provided.

## 5. Expected Value

If validated, HRM-style neural weight-to-phase mapping could support:

- low-latency optical linear transforms
- hybrid electro-optical inference experiments
- model-to-hardware compilation studies
- calibration-aware photonic ML research
- future photonic tensor-core exploration

The expected value is not that the hardware thinks, but that selected numerical
operations may be represented as calibrated physical transfer functions.

## 6. Open Validation Tasks

Required next steps:

1. Define the HRM mesh transfer-matrix model.
2. Implement software export from PyTorch weight matrices.
3. Implement SVD or alternative decomposition pipeline.
4. Generate phase, coupler, and attenuator candidate settings.
5. Validate against simulated transfer matrices.
6. Add quantization and dynamic-range analysis.
7. Add thermal drift and phase-noise perturbation tests.
8. Define hardware calibration protocol.
9. Define measured-transfer-matrix acceptance criteria.
10. Report end-to-end accuracy, energy, latency, and stability.

Until these tasks are completed, this addendum remains a future-work extension.
