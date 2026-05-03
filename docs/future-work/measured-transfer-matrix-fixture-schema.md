# Measured Transfer Matrix Fixture Schema

This schema defines the required fields for a future Stage 6 measured HRM
transfer-matrix evidence fixture.

It does not provide measured data, does not claim that measured data exists,
and does not unblock Stage 6. Stage 6 remains blocked until a real measured
transfer-matrix artifact with provenance is supplied.

## Required Fields

| Field | Requirement |
| --- | --- |
| `artifactId` | Stable identifier for the measured transfer-matrix fixture. |
| `measurementDate` | Date when the measurement was performed. |
| `deviceId` | Identifier of the measured device or die. |
| `setupDescription` | Measurement setup, instrumentation, and relevant configuration. |
| `wavelength` | Wavelength or wavelength range used for the measurement. |
| `temperatureOrOperatingCondition` | Temperature and operating condition during measurement. |
| `matrixShape` | Matrix dimensions and ordering convention. |
| `matrixConvention` | Whether the matrix is real or complex, including phase/amplitude convention. |
| `calibrationProcedure` | Procedure used to calibrate instruments and normalize the matrix. |
| `rawArtifactReference` | Reference to the immutable raw measurement artifact. |
| `processedArtifactReference` | Reference to the processed matrix artifact used by the gate. |
| `sha256Hash` | SHA-256 hash for the processed artifact, and raw artifact when available. |
| `provenance` | Provenance chain for measurement, processing, and storage. |
| `uncertaintyOrErrorEstimate` | Measurement uncertainty, reconstruction error, or equivalent error estimate. |
| `operatorOrSource` | Operator, lab, instrument source, or other accountable source. |
| `claimBoundary` | Statement that the fixture is measured evidence only and does not by itself claim production inference readiness. |

## Gate Behavior

The Stage 6 gate must remain blocked unless all required fields are present and
the referenced artifacts are real measured HRM transfer-matrix artifacts with
provenance.

The presence of this schema file is not evidence of a measured transfer matrix.

