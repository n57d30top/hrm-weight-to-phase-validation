# Foundry Data Request

This document lists the foundry or PDK package that would be needed before
Stage 5 could be considered. It is a request template only. It is not foundry
calibration and it is not hardware evidence.

## Required Source Metadata

- Artifact identifier.
- Evidence class: `foundry_calibrated_device_model`.
- Foundry or PDK source.
- Source version.
- Source date.
- Device scope.
- Wavelength range.
- Temperature or operating condition.
- Calibration procedure.
- Provenance.
- Uncertainty or error estimate.
- Operator or source.
- Claim boundary.

## Required Artifacts

Each artifact reference should be repository-relative and paired with a SHA-256
hash:

- S-parameter artifacts.
- Calibrated compact-model artifacts.
- Calibrated loss-model artifact.
- Calibrated crosstalk-model artifact.
- Calibrated phase-shifter-model artifact.

## Stage 5 Boundary

Stage 5 remains blocked until a real foundry-calibrated package is supplied and
passes required-field, evidence-class, date, relative-path, artifact-existence,
hash, provenance, uncertainty, and claim-boundary checks.
