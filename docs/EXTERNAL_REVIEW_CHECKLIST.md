# External Review Checklist

This checklist is for future external reviewers. It does not imply that review
has already happened.

Allowed reviewer statuses:

- pass
- needs clarification
- blocked by missing evidence

## Reproduction Checklist

- Run `make check`.
- Run `python3 scripts/hrmwtp.py doctor`.
- Confirm reports regenerate deterministically.

## Claim-Boundary Checklist

- Confirm public reports keep hardware claim flags false.
- Confirm Stage 5, Stage 6, and Stage 7 remain blocked.
- Confirm synthetic fixtures are not described as measured evidence.

## Report And Hash Checklist

- Run `sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256`.
- Run `python3 scripts/check_artifact_hash_coverage.py`.
- Inspect `validation-ladder-summary.json`.

## Model Suitability Checklist

- Inspect `model-suitability-profile.json`.
- Inspect `model-portfolio-ranking.json`.
- Inspect model cards under `reports/future-work/hrm-neural-mapping/model-cards/`.

## Hardware Gate Checklist

- Inspect Stage 5, Stage 6, and Stage 7 gate reports.
- Verify blocker reasons are still present.

## Calibration Plan Checklist

- Inspect `calibration-plan.json`.
- Inspect `transfer-matrix-assimilation-plan.json`.
- Confirm these are plan-only artifacts.

## Transfer-Matrix Evidence Checklist

- Confirm no real measured transfer-matrix package is included.
- Confirm the ingestion sandbox is marked synthetic-only.

## Benchmark Evidence Checklist

- Confirm no end-to-end hardware benchmark package is included.
- Confirm hardware benchmark gate remains blocked.
