# Model Card: transformer_block_manifest_only

This model card is simulation-only. It is not hardware evidence.

- modelId: `transformer_block_manifest_only`
- model type: `transformer_block_manifest_only`
- rank in portfolio: `5`
- suitability score: `53.333`
- suitability class: `partial_candidate`
- layer summary: `12` total layers
- mappable layers: `4`
- classical layers: `4`
- unsupported layers: `4`

## Why It Ranks Here

It ranks last because unsupported operations dominate relative to the current abstract mapping path.

## Dominant Limitations

- unsupported layer count: `4`
- real foundry/PDK behavior is not included
- measured transfer matrices are not available
- end-to-end hardware benchmarks are not available

## Missing Hardware Evidence

- foundry calibrated device model
- measured HRM transfer matrix
- end-to-end hardware inference benchmark

## Claim Boundary

Simulation-only partner-readiness material; this does not claim hardware validation, foundry calibration, measured transfer matrices, production inference readiness, real hardware latency, real hardware energy efficiency, physical accuracy, quantum advantage, hardware-native intelligence, or power-free computation.
