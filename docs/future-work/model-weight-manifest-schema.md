# Model Weight Manifest Schema

This schema defines a future-work input format for importing model-weight
artifacts into the simulation-only HRM weight-to-phase validation ladder.

The schema is not a hardware evidence format. It does not provide foundry
calibration, measured transfer matrices, production inference readiness,
optical nonlinearities, full model acceleration, transformer acceleration, or
hardware validation.

## Manifest Fields

Required top-level fields:

- `modelId`
- `modelType`
- `sourceFramework`
- `exportFormat`
- `exportDate`
- `provenance`
- `layerList`
- `claimBoundary`

`exportDate` must be an ISO date string. `layerList` must be a non-empty list.

## Layer Fields

Required fields for every layer entry:

- `layerId`
- `layerType`
- `shape`
- `dtype`
- `activationAfterLayer`
- `mappingEligible`
- `mappingLimitations`
- `claimBoundary`

Required fields for weight-bearing layer entries:

- `weightArtifactReference`
- `weightArtifactSha256`

Optional fields for weight-bearing layer entries:

- `biasArtifactReference`
- `biasArtifactSha256`

Artifact references must be repository-relative paths. Absolute paths, file
URIs, desktop-local paths, and home-directory paths are invalid.

## Supported Classification

Mapping eligibility is simulation-only:

- `linear`: eligible
- `rectangular_linear`: eligible
- `complex_linear`: eligible when the current complex/unitary simulation path applies
- `convolution`: ineligible, not implemented
- `attention_softmax`: ineligible, not implemented
- `embedding`: ineligible, not implemented
- `normalization`: classical / outside optical mesh
- `activation`: classical / outside optical mesh
- `bias`: classical / outside optical mesh

Eligible linear layers produce a mapping plan. Bias, activation, normalization,
and other non-linear or stateful operations remain outside the optical mesh.

Future PyTorch export support can generate this manifest format externally.
PyTorch is not a dependency of this repository.
