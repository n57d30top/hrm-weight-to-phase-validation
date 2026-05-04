This is a simulation-only decision report. It is not hardware evidence.

# Model-to-HRM Decision Report

Model: `tiny_mlp_manifest_4_6_3`

## Decision

- Decision class: `blocked_by_missing_hardware_evidence`
- Suitability score: 87.647
- Suitability class: `good_candidate`

## Layer Summary

- Mappable layers: 2
- Classical components: 3
- Unsupported components: 0

## Error Budget

- Dominant contributor: perturbationError
- RSS envelope: 0.413071539277794

## Missing Evidence

- foundry-calibrated device model
- measured transfer matrix
- hardware benchmark

## Recommended Next Actions

- keep model linear weights in the manifest path for simulation planning
- measure transfer matrices before considering Stage 6 complete
- collect hardware benchmark packages before considering Stage 7 complete
- use the requirements envelope to prioritize phase, drift, and loss measurements

## Claim Boundary

This is a simulation-only decision report. It is not hardware evidence. It does not claim hardware validation, foundry calibration, measured transfer matrices, production inference readiness, real hardware latency, real hardware energy efficiency, quantum advantage, hardware-native intelligence, or power-free computation.
