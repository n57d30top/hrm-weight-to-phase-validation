# Model Export Adapter Protocol

This protocol describes optional exporter behavior. It is not framework execution and not hardware evidence.

## Adapter Contract

- external frameworks may export weights into repository-relative JSON artifacts
- exporter output must use the existing model-weight manifest schema
- every weight artifact must have a SHA-256 hash
- generated manifests must be validated by the existing importer before mapping analysis
- PyTorch is not a required dependency

## Optional Example

`fixtures/model-export-adapter/tiny-linear-export-example.json` shows the adapter input shape.

## Claim Boundary

Optional export-adapter protocol only; this does not claim PyTorch model execution, full model acceleration, hardware validation, foundry calibration, measured transfer matrices, production inference readiness, quantum advantage, hardware-native intelligence, or power-free computation.
