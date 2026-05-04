.PHONY: demo ladder test json hash hash-coverage-check local-path-check claim-boundary-check check

demo:
	python3 scripts/run_hrm_neural_mapping_demo.py

ladder:
	python3 scripts/run_hrm_neural_validation_ladder.py

test:
	python3 -m unittest discover -s tests -v

json:
	jq empty docs/future-work/evidence-ledger.json
	jq empty reports/future-work/hrm-neural-mapping/stage-0-specification.json
	jq empty reports/future-work/hrm-neural-mapping/stage-1-svd-demo.json
	jq empty reports/future-work/hrm-neural-mapping/stage-2-mesh-constrained.json
	jq empty reports/future-work/hrm-neural-mapping/calibration-plan.json
	jq empty reports/future-work/hrm-neural-mapping/complex-unitary-mesh-support.json
	jq empty reports/future-work/hrm-neural-mapping/error-budget-report.json
	jq empty reports/future-work/hrm-neural-mapping/hardware-design-space-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/hardware-design-space-sweep.json
	jq empty reports/future-work/hrm-neural-mapping/hardware-requirements-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/hardware-requirements-envelope.json
	jq empty reports/future-work/hrm-neural-mapping/hardware-scenario-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/hardware-scenario-estimates.json
	jq empty reports/future-work/hrm-neural-mapping/layer-stack-inference-demo.json
	jq empty reports/future-work/hrm-neural-mapping/layer-stack-error-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/matrix-family-benchmark.json
	jq empty reports/future-work/hrm-neural-mapping/matrix-family-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/model-export-adapter-demo.json
	jq empty reports/future-work/hrm-neural-mapping/model-export-adapter-validation.json
	jq empty reports/future-work/hrm-neural-mapping/model-portfolio-benchmark.json
	jq empty reports/future-work/hrm-neural-mapping/model-portfolio-ranking.json
	jq empty reports/future-work/hrm-neural-mapping/partner-readiness-report.json
	jq empty reports/future-work/hrm-neural-mapping/external-review-checklist.json
	jq empty reports/future-work/hrm-neural-mapping/reproducibility-capsule.json
	jq empty reports/future-work/hrm-neural-mapping/solo-completion-audit.json
	jq empty reports/future-work/hrm-neural-mapping/v0.2.0-alpha3-readiness.json
	jq empty reports/future-work/hrm-neural-mapping/model-to-hrm-decision-report.json
	jq empty reports/future-work/hrm-neural-mapping/model-weight-import-demo.json
	jq empty reports/future-work/hrm-neural-mapping/model-weight-eligibility-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/model-suitability-profile.json
	jq empty reports/future-work/hrm-neural-mapping/model-suitability-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/rectangular-matrix-support.json
	jq empty reports/future-work/hrm-neural-mapping/release-readiness-v0.1.0.json
	jq empty reports/future-work/hrm-neural-mapping/review-pack-summary.json
	jq empty reports/future-work/hrm-neural-mapping/scaling-benchmark.json
	jq empty reports/future-work/hrm-neural-mapping/scaling-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/stage-3-perturbation-model.json
	jq empty reports/future-work/hrm-neural-mapping/stage-3-perturbation-sweep.json
	jq empty reports/future-work/hrm-neural-mapping/stage-3-sweep-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/stage-4-simulated-calibration.json
	jq empty reports/future-work/hrm-neural-mapping/stage-4-calibration-sweep.json
	jq empty reports/future-work/hrm-neural-mapping/stage-4-calibration-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/stage-5-foundry-calibration-gate.json
	jq empty reports/future-work/hrm-neural-mapping/stage-6-measured-transfer-matrix-gate.json
	jq empty reports/future-work/hrm-neural-mapping/stage-7-hardware-benchmark-gate.json
	jq empty reports/future-work/hrm-neural-mapping/transfer-matrix-assimilation-plan.json
	jq empty reports/future-work/hrm-neural-mapping/transfer-matrix-ingestion-sandbox.json
	jq empty reports/future-work/hrm-neural-mapping/v0.1.0-rc1-readiness.json
	jq empty reports/future-work/hrm-neural-mapping/validation-ladder-summary.json

hash:
	sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256

hash-coverage-check:
	python3 scripts/check_artifact_hash_coverage.py

local-path-check:
	python3 scripts/check_no_local_paths.py

claim-boundary-check:
	python3 scripts/check_claim_boundary.py

check: demo ladder test json hash hash-coverage-check local-path-check claim-boundary-check
	git diff --check
