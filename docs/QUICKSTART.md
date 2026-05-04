# Quickstart

This quickstart reproduces the simulation-only HRM photonic AI planning reports.
It is not a hardware validation workflow.

## Install

From the repository root:

```bash
python3 -m pip install -e .
```

Requirements:

- Python 3.10 or newer
- `jq`
- `sha256sum`
- `make`

## Run The Full Check

```bash
make check
```

This regenerates reports, runs tests, validates JSON, checks hashes, enforces
hash coverage, checks for local path fragments, and runs the claim-boundary
guard.

## Use The CLI

```bash
python3 scripts/hrmwtp.py --help
python3 scripts/hrmwtp.py doctor
python3 scripts/hrmwtp.py summary
python3 scripts/hrmwtp.py decision
python3 scripts/hrmwtp.py portfolio
python3 scripts/hrmwtp.py model-card low_rank_adapter_demo
python3 scripts/hrmwtp.py list-reports
```

Installed entry point:

```bash
hrmwtp summary
hrmwtp decision
```

The CLI prints a simulation-only disclaimer for every command. JSON outputs are
printed on stdout.

## Open The Dashboard

The static dashboard is generated at:

```text
dashboard/index.html
```

It links to key reports, stage status, portfolio summaries, hardware gate
blockers, and the claim boundary.

## Partner/Reviewer Docs

- `docs/REVIEWER_GUIDE.md`
- `docs/PARTNER_READINESS.md`
- `docs/LAB_DATA_REQUEST.md`
- `docs/FOUNDRY_DATA_REQUEST.md`
- `docs/HARDWARE_EVIDENCE_CHECKLIST.md`
- `docs/EXTERNAL_REVIEW_CHECKLIST.md`
- `docs/REPRODUCIBILITY.md`

## Verify Artifacts

```bash
sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256
```

The project remains simulation-only. Stage 5, Stage 6, and Stage 7 remain
blocked until real external evidence exists.
