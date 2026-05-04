# Simulation Error Budget

This is a simulation-only error budget. It is not a hardware accuracy claim.

## Components

| Component | Error | Source |
| --- | --- | --- |
| baselineMappingError | 0.019640136609986 | `stage-2-mesh-constrained.json` |
| rectangularMappingError | 0.091134277782103 | `rectangular-matrix-support.json` |
| complexUnitaryApproximationError | 0.021020525022447 | `complex-unitary-mesh-support.json` |
| perturbationError | 0.370308698767234 | `stage-3-sweep-analysis.json` |
| calibrationResidualError | 0.024641168630069 | `stage-4-calibration-analysis.json` |
| layerStackOutputError | 0.061296868009442 | `layer-stack-inference-demo.json` |
| scalingWorstCaseError | 0.141428486997061 | `scaling-analysis.json` |

## Combined Envelope

- Additive model: 0.729470161818342
- RSS model: 0.413071539277794
- Conservative max model: 0.370308698767234

## Dominant Contributors

- Dominant: perturbationError
- Secondary: scalingWorstCaseError

## What To Improve First

- reduce the largest simulated scaling and perturbation terms before interpreting smaller residuals
- use measured transfer matrices to replace simulation-only uncertainty terms when real data exists

## Claim Boundary

Simulation-only error budget; no physical accuracy, hardware validation, foundry calibration, measured transfer matrices, production inference readiness, real hardware latency, or real hardware energy efficiency is claimed.
