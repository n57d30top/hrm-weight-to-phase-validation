# Lab Data Request

This document lists the measurement package a photonic test lab would need to
provide before Stage 6 could be considered. It is a request template only. It is
not measured data and it is not hardware evidence.

## Required Measurement Context

- Device identifier.
- Measurement date.
- Operator or source.
- Wavelength condition.
- Temperature or operating condition.
- Input basis.
- Output readout convention.
- Matrix convention: real or complex.
- Calibration procedure.
- Drift monitoring plan.
- Uncertainty or error estimate.
- Provenance.
- Claim boundary.

## Required Artifacts

- Raw measurement artifact reference.
- Processed transfer-matrix artifact reference.
- SHA-256 hash for each artifact.
- Shape and dtype metadata.
- Notes on normalization and alignment.

## Stage 6 Boundary

Stage 6 remains blocked until a real measured HRM transfer-matrix package is
provided and passes manifest, path, hash, provenance, and claim-boundary checks.
Synthetic fixtures do not unblock Stage 6.
