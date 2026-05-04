# v0.1.0 Release-Candidate Readiness

This v0.1.0 readiness report is simulation-only. It does not claim hardware validation, foundry calibration, measured transfer matrices, production inference readiness, physical accuracy, hardware latency, hardware energy efficiency, quantum advantage, or a completed hardware benchmark.

## Completed Simulation Stages

| Stage | Report | Status | Evidence Level |
| --- | --- | --- | --- |
| 0 | `stage-0-specification` | complete | theoretical_extension |
| 1 | `stage-1-svd-demo` | complete | numerical_simulation |
| 2 | `stage-2-mesh-constrained` | complete | abstract_mesh_simulation |
| 3 | `stage-3-perturbation-model` | complete | uncalibrated_perturbation_simulation |
| 4 | `stage-4-simulated-calibration` | complete | synthetic_calibration_simulation |

## Supplemental Reports

- `calibration-plan` (calibration_plan_only)
- `complex-unitary-mesh-support` (abstract_complex_unitary_mesh_simulation)
- `error-budget-report` (simulation_error_budget)
- `external-review-checklist` (external_review_checklist)
- `hardware-design-space-analysis` (hardware_design_space_analysis)
- `hardware-design-space-sweep` (hardware_design_space_sweep_simulation)
- `hardware-requirements-analysis` (simulation_derived_hardware_requirements_analysis)
- `hardware-requirements-envelope` (simulation_derived_hardware_requirements)
- `hardware-scenario-analysis` (parametric_hardware_scenario_analysis)
- `hardware-scenario-estimates` (parametric_hardware_scenario_estimate)
- `layer-stack-error-analysis` (abstract_layer_stack_error_analysis)
- `layer-stack-inference-demo` (abstract_layer_stack_inference_simulation)
- `matrix-family-analysis` (abstract_matrix_family_analysis)
- `matrix-family-benchmark` (abstract_matrix_family_benchmark_simulation)
- `model-export-adapter-demo` (model_export_adapter_protocol)
- `model-export-adapter-validation` (model_export_adapter_validation)
- `model-portfolio-benchmark` (model_portfolio_benchmark_simulation)
- `model-portfolio-ranking` (model_portfolio_ranking_simulation)
- `model-suitability-analysis` (model_suitability_analysis)
- `model-suitability-profile` (model_suitability_profile_simulation)
- `model-to-hrm-decision-report` (simulation_only_model_to_hrm_decision)
- `model-weight-eligibility-analysis` (model_weight_manifest_eligibility_analysis)
- `model-weight-import-demo` (model_weight_manifest_import_simulation)
- `partner-readiness-report` (partner_readiness_review_package)
- `rectangular-matrix-support` (abstract_rectangular_mesh_simulation)
- `reproducibility-capsule` (reproducibility_capsule)
- `review-pack-summary` (simulation_review_pack)
- `scaling-analysis` (abstract_scaling_analysis)
- `scaling-benchmark` (abstract_scaling_benchmark_simulation)
- `solo-completion-audit` (solo_completion_audit)
- `stage-3-perturbation-sweep` (uncalibrated_perturbation_simulation)
- `stage-3-sweep-analysis` (uncalibrated_perturbation_simulation)
- `stage-4-calibration-analysis` (synthetic_calibration_simulation)
- `stage-4-calibration-sweep` (synthetic_calibration_simulation)
- `transfer-matrix-assimilation-plan` (transfer_matrix_assimilation_plan_only)
- `transfer-matrix-ingestion-sandbox` (synthetic_transfer_matrix_ingestion_sandbox)
- `v0.2.0-alpha3-readiness` (v0.2.0_alpha3_readiness)

## Blocked Hardware Gates

- Stage 5 `stage-5-foundry-calibration-gate` remains blocked: no_foundry_calibrated_device_model
- Stage 6 `stage-6-measured-transfer-matrix-gate` remains blocked: no_measured_hrm_transfer_matrix
- Stage 7 `stage-7-hardware-benchmark-gate` remains blocked: no_end_to_end_hardware_benchmark

## Verification Commands

- `make check`
- `jq empty reports/future-work/hrm-neural-mapping/release-readiness-v0.1.0.json`
- `sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256`
- `python3 scripts/check_artifact_hash_coverage.py`
- `python3 scripts/check_no_local_paths.py`
- `python3 scripts/check_claim_boundary.py`
- `git diff --check`

## Known Limitations

- simulation-only research framework
- no foundry-calibrated device model
- no measured HRM transfer matrix
- no end-to-end hardware inference benchmark
- no physical layout synthesis
- no hardware timing, energy, throughput, or physical accuracy measurement
- no production inference readiness

## Recommended Next After v0.1.0

- tag v0.1.0-rc.1 only after alpha.12 review
- keep Stage 5, Stage 6, and Stage 7 blocked until real external evidence exists
- consider optional external model-export adapters without adding a hard framework dependency
- consider larger deterministic benchmark suites while preserving CI runtime
