# Foundry-Calibrated Device Model Schema

This schema defines the required fields for a future Stage 5
foundry-calibrated device-model evidence package.

It does not provide foundry data, does not claim that foundry-calibrated data
exists, and does not unblock Stage 5. Stage 5 remains blocked until real
foundry-calibrated S-parameters or equivalent calibrated device-model artifacts
with provenance are supplied.

## Required Fields

| Field | Requirement |
| --- | --- |
| `artifactId` | Stable identifier for the foundry-calibrated evidence package. |
| `evidenceClass` | Must be `foundry_calibrated_device_model`. |
| `foundryOrPdkSource` | Foundry, PDK, vendor, lab, or source that produced the calibrated model. |
| `sourceVersion` | Version, release, lot, or revision identifier for the source package. |
| `sourceDate` | ISO date for the source package, model release, or calibration source. |
| `deviceScope` | Device, process, die, component family, or operating scope covered by the model. |
| `sParameterArtifacts` | Non-empty list of hash references for S-parameter artifacts. |
| `calibratedCompactModelArtifacts` | Non-empty list of hash references for calibrated compact-model artifacts. |
| `calibratedLossModelArtifact` | Hash reference for the calibrated loss model artifact. |
| `calibratedCrosstalkModelArtifact` | Hash reference for the calibrated crosstalk model artifact. |
| `calibratedPhaseShifterModelArtifact` | Hash reference for the calibrated phase-shifter model artifact. |
| `wavelengthRange` | Wavelength range covered by the calibrated model. |
| `temperatureOrOperatingCondition` | Temperature and operating condition covered by the model. |
| `calibrationProcedure` | Procedure used to calibrate, fit, validate, or release the model. |
| `provenance` | Provenance chain for source data, model generation, processing, and storage. |
| `uncertaintyOrErrorEstimate` | Uncertainty, fit residuals, calibration error, or equivalent model error estimate. |
| `operatorOrSource` | Operator, lab, foundry, vendor, or accountable source for the evidence package. |
| `claimBoundary` | Statement that the package is foundry-model evidence only and does not by itself claim measured transfer matrices, hardware validation, or production inference readiness. |

## Hash References

Artifact references use relative paths and SHA-256 digests:

```json
{
  "artifactReference": "relative/path/to/artifact",
  "sha256": "64_hex_character_sha256_digest"
}
```

Lists such as `sParameterArtifacts` and `calibratedCompactModelArtifacts` must
contain one or more hash-reference objects. Single artifacts use one
hash-reference object.

## Gate Behavior

The Stage 5 gate must remain blocked unless all required fields are present,
the evidence class is correct, `sourceDate` is a valid ISO date, every artifact
reference is relative, every referenced artifact file exists, every SHA-256
hash matches, and provenance, uncertainty, source, and claim-boundary fields are
non-empty.

The presence of this schema file is not evidence of a foundry-calibrated device
model.
