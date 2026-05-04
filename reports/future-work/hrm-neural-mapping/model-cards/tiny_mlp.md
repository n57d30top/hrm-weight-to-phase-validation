# Model Card: tiny_mlp

This model card is simulation-only. It is not hardware evidence.

- modelId: `tiny_mlp`
- model type: `mlp`
- rank in portfolio: `3`
- suitability score: `87.647`
- suitability class: `good_candidate`
- layer summary: `5` total layers
- mappable layers: `2`
- classical layers: `3`
- unsupported layers: `0`

## Why It Ranks Here

It ranks in the middle because it has useful mappable linear structure but less favorable planning metrics than the best candidate.

## Dominant Limitations

- unsupported layer count: `0`
- real foundry/PDK behavior is not included
- measured transfer matrices are not available
- end-to-end hardware benchmarks are not available

## Missing Hardware Evidence

- foundry calibrated device model
- measured HRM transfer matrix
- end-to-end hardware inference benchmark

## Claim Boundary

Simulation-only partner-readiness material; this does not claim hardware validation, foundry calibration, measured transfer matrices, production inference readiness, real hardware latency, real hardware energy efficiency, physical accuracy, quantum advantage, hardware-native intelligence, or power-free computation.
