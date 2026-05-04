# Model Card: low_rank_adapter_demo

This model card is simulation-only. It is not hardware evidence.

- modelId: `low_rank_adapter_demo`
- model type: `adapter`
- rank in portfolio: `1`
- suitability score: `95.882`
- suitability class: `good_candidate`
- layer summary: `6` total layers
- mappable layers: `4`
- classical layers: `2`
- unsupported layers: `0`

## Why It Ranks Here

It ranks first because it has the highest mappable parameter share and no unsupported layers in this deterministic portfolio.

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
