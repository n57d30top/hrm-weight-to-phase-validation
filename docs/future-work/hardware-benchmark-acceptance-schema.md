# Hardware Benchmark Acceptance Schema

This schema defines the required fields for a future Stage 7 end-to-end
hardware inference benchmark evidence package.

It does not provide benchmark data, does not claim that benchmark data exists,
and does not unblock Stage 7. Stage 7 remains blocked until a real measured
hardware benchmark package with provenance is supplied.

## Required Fields

| Field | Requirement |
| --- | --- |
| `benchmarkId` | Stable identifier for the hardware benchmark package. |
| `deviceId` | Identifier of the measured device or system under test. |
| `measuredTransferMatrixReference` | Reference to the measured transfer-matrix artifact used by the benchmark. |
| `dataset` | Dataset, split, task, and preprocessing definition. |
| `softwareBaseline` | Software baseline implementation and version used for comparison. |
| `inputEncoding` | Input encoding method, scale, precision, and data path into the device. |
| `outputReadout` | Output readout method, detector mapping, decoding, and postprocessing. |
| `controlPathCharacterization` | DAC, ADC, phase-control, thermal-control, or equivalent control-path characterization. |
| `detectorReadoutCharacterization` | Detector and readout characterization, including noise and dynamic range. |
| `accuracyMetric` | Accuracy or task-quality metric with comparison against the software baseline. |
| `latencyMetric` | End-to-end latency metric, including control, conversion, readout, and orchestration overhead. |
| `energyMetric` | End-to-end energy metric, including optical, electronic, control, conversion, and thermal components. |
| `driftRecalibrationMetric` | Drift, stability, and recalibration cadence or cost. |
| `environment` | Operating environment, including temperature, wavelength, packaging, and relevant conditions. |
| `rawResultsHash` | SHA-256 hash for immutable raw benchmark results. |
| `processedResultsHash` | SHA-256 hash for processed benchmark summaries. |
| `provenance` | Provenance chain for benchmark execution, processing, and storage. |
| `claimBoundary` | Statement that the benchmark package is measured evidence and does not imply broader production readiness beyond its measured scope. |

## Gate Behavior

The Stage 7 gate must remain blocked unless all required fields are present and
the referenced artifacts are a real end-to-end measured hardware inference
benchmark package with provenance.

The presence of this schema file is not evidence of a hardware benchmark.

