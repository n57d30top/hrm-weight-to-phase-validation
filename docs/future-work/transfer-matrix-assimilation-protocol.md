# Transfer-Matrix Assimilation Protocol

Plan only; no measured transfer matrix is available, no hardware validation is claimed, and Stage 6 remains blocked.

## Required Measurement Fields

- device id
- measurement date
- operator or source
- setup description

## Calibration Sequence

- measure dark/readout baseline
- measure input basis responses
- estimate transfer matrix
- normalize according to declared convention
- validate on held-out vectors
- hash raw and processed artifacts

## Assimilation Steps

- match matrix convention
- normalize global phase or scale according to manifest
- align input and output channel ordering
- fit diagonal phase/scale corrections first
- fit low-order coupling correction only if justified by measured data
- report residual error after correction

## Pass/Fail Criteria

- all referenced artifacts exist and hash-verify
- declared uncertainty is present
- validation vector residuals are below declared threshold
- claim boundary remains explicit
