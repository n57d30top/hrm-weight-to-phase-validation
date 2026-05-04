# Hardware Evidence Checklist

This checklist defines what future external evidence would need to contain. It
does not imply that the evidence exists today.

## Stage 5: Foundry-Calibrated Device Model

- Manifest uses the required Stage 5 schema.
- Evidence class is `foundry_calibrated_device_model`.
- Artifact paths are repository-relative.
- Referenced artifacts exist.
- SHA-256 hashes match.
- Source version and source date are present.
- Provenance, uncertainty, operator/source, and claim boundary are present.

## Stage 6: Measured HRM Transfer Matrix

- Manifest uses the required Stage 6 schema.
- Raw and processed artifacts exist.
- SHA-256 hashes match.
- Measurement conditions are documented.
- Matrix shape and real/complex convention are documented.
- Calibration procedure and uncertainty estimate are present.
- Provenance and claim boundary are present.

## Stage 7: End-To-End Hardware Benchmark

- Stage 6 is complete first.
- Benchmark package uses the required Stage 7 schema.
- Dataset, software baseline, input encoding, and output readout are documented.
- Control path and detector/readout characterization are documented.
- Accuracy, latency, energy, and drift/recalibration metrics are documented.
- Raw and processed benchmark hashes match.
- Provenance and claim boundary are present.

## Current Status

Stages 5, 6, and 7 remain blocked. The repository does not claim hardware
validation, foundry calibration, measured transfer matrices, or production
inference readiness.
