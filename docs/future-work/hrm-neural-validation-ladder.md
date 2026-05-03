# HRM Neural Validation Ladder

This ladder records the evidence levels for the HRM neural weight-to-phase
mapping future-work track. It is intentionally separate from hardware readiness.

| Stage | Status Target | Evidence Level | Completion Rule |
| --- | --- | --- | --- |
| 0 | complete | theoretical_extension | Specification exists and includes explicit claim boundaries. |
| 1 | complete | numerical_simulation | Deterministic SVD reconstruction passes tests with passive singular-value normalization. |
| 2 | complete | abstract_mesh_simulation | Deterministic abstract phase/coupler parameterization is implemented and tested without claiming physical phase synthesis, a foundry layout, or a real chip mesh. |
| 3 | complete | uncalibrated_perturbation_simulation | Deterministic perturbation models run and report deltas without physical-accuracy claims. |
| 4 | complete | synthetic_calibration_simulation | Simulation-only calibration improves or does not worsen a synthetic transfer estimate using an oracle target available only in simulation. |
| 5 | blocked | foundry_calibration_gate | Requires foundry-calibrated S-parameters or equivalent calibrated device models. |
| 6 | blocked | measured_transfer_matrix_gate | Requires measured HRM transfer-matrix artifacts with provenance. |
| 7 | blocked | hardware_benchmark_gate | Requires an end-to-end measured hardware inference benchmark package. |

Blocked gates are successful schema outcomes, not completed hardware milestones.
They identify the missing evidence needed before any stronger claim can be made.

The generated summary is `reports/future-work/hrm-neural-mapping/validation-ladder-summary.json`.

Stage 2 is complete only as an abstract mesh simulation. It is currently scoped
to a small square matrix, real-valued orthogonal approximation, deterministic
quantized Givens rotations, and abstract phase/coupler parameter records. It
does not implement a complex unitary mesh, rectangular neural layer support,
Clements/Reck physical interferometer layout, foundry layout synthesis, physical
phase synthesis, or physical coupler synthesis.

Stage 4 is synthetic/oracle calibration. It does not use measured transfer
matrices and does not claim hardware calibration.

Stage 3 also emits a supplemental deterministic sweep report:
`reports/future-work/hrm-neural-mapping/stage-3-perturbation-sweep.json`.
The sweep varies one uncalibrated perturbation parameter at a time and keeps all
hardware-readiness flags false.
