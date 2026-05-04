# Reviewer Guide

This guide is for reviewers who want to reproduce and inspect the
simulation-only HRM photonic AI planning toolkit.

This repository is not hardware evidence. It does not claim hardware
validation, foundry calibration, measured transfer matrices, production
inference readiness, physical accuracy, real hardware latency, real hardware
energy efficiency, quantum advantage, hardware-native intelligence, or
power-free computation.

## Reproduce The Reports

From the repository root:

```bash
python3 -m pip install -e .
make check
```

The `make check` target regenerates reports, runs unit tests, validates JSON,
verifies SHA-256 hashes, checks report hash coverage, checks local-path hygiene,
runs the claim-boundary guard, and checks whitespace.

For CLI-oriented review:

```bash
python3 scripts/hrmwtp.py --help
python3 scripts/hrmwtp.py doctor
python3 scripts/hrmwtp.py summary
python3 scripts/hrmwtp.py decision
python3 scripts/hrmwtp.py portfolio
python3 scripts/hrmwtp.py model-card low_rank_adapter_demo
python3 scripts/hrmwtp.py list-reports
```

Each command prints a simulation-only disclaimer. JSON-producing commands keep
the JSON on stdout and put the disclaimer on stderr.

## Reports That Matter First

Start with these files:

- `reports/future-work/hrm-neural-mapping/validation-ladder-summary.json`
- `reports/future-work/hrm-neural-mapping/model-to-hrm-decision-report.json`
- `reports/future-work/hrm-neural-mapping/review-pack.md`
- `reports/future-work/hrm-neural-mapping/model-portfolio-ranking.json`
- `reports/future-work/hrm-neural-mapping/model-portfolio-explainer.md`
- `reports/future-work/hrm-neural-mapping/model-cards/`
- `reports/future-work/hrm-neural-mapping/partner-readiness-report.json`
- `reports/future-work/hrm-neural-mapping/external-review-checklist.json`
- `reports/future-work/hrm-neural-mapping/reproducibility-capsule.json`
- `reports/future-work/hrm-neural-mapping/solo-completion-audit.json`
- `reports/future-work/hrm-neural-mapping/hardware-design-space-analysis.json`
- `reports/future-work/hrm-neural-mapping/transfer-matrix-ingestion-sandbox.json`
- `reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256`
- `dashboard/index.html`

The dashboard is a static index over generated reports. It is not hardware
evidence.

## Read The Decision Report

The decision report answers a narrow planning question: whether the current
model fixture is a good simulation candidate for HRM-style mapping and what
evidence is still missing.

Important fields:

- `simulationOnly`
- `decisionIsNotHardwareValidation`
- `decision`
- `suitabilityScore`
- `missingEvidence`
- `recommendedNextActions`

The expected decision remains `blocked_by_missing_hardware_evidence` because
foundry models, measured transfer matrices, and hardware benchmark packages are
not present.

## Why Stages 5, 6, And 7 Are Blocked

Stage 5 is blocked until a real foundry-calibrated device-model package is
provided with provenance, relative artifact references, and matching hashes.

Stage 6 is blocked until a real measured HRM transfer-matrix package is
provided with measurement conditions, provenance, uncertainty or error
estimates, relative artifact references, and matching hashes.

Stage 7 is blocked until a real end-to-end hardware inference benchmark package
is provided. Stage 7 also depends on Stage 6, so it cannot complete while the
measured transfer-matrix gate remains blocked.

Synthetic fixtures and planning proxies do not unblock hardware gates.

## Verify Hashes

Run:

```bash
sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256
python3 scripts/check_artifact_hash_coverage.py
```

The first command verifies the listed artifacts. The second command ensures
every generated JSON report under `reports/future-work/hrm-neural-mapping/` is
covered by `ARTIFACTS.sha256`.

## Reviewer Checklist

- Run `make check`.
- Confirm `validation-ladder-summary.json` keeps Stages 5, 6, and 7 blocked.
- Confirm all public generated reports keep the hardware claim flags false.
- Inspect `model-to-hrm-decision-report.json`.
- Inspect `ARTIFACTS.sha256`.
- Inspect `dashboard/index.html`.
- Confirm the transfer-matrix sandbox says `syntheticFixtureOnly=true` and
  `publicMeasuredEvidence=false`.
- Inspect the partner readiness report and external review checklist.
- Inspect the solo completion audit and confirm hardware validation remains 0.
