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
	jq empty reports/future-work/hrm-neural-mapping/complex-unitary-mesh-support.json
	jq empty reports/future-work/hrm-neural-mapping/layer-stack-inference-demo.json
	jq empty reports/future-work/hrm-neural-mapping/layer-stack-error-analysis.json
	jq empty reports/future-work/hrm-neural-mapping/matrix-family-benchmark.json
	jq empty reports/future-work/hrm-neural-mapping/matrix-family-analysis.json
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
