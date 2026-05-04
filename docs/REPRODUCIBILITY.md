# Reproducibility

This document describes how to reproduce the simulation-only reports. It is not
a hardware validation protocol.

## Commands

```bash
python3 -m pip install -e .
make check
python3 scripts/hrmwtp.py --help
python3 scripts/hrmwtp.py doctor
python3 scripts/hrmwtp.py summary
python3 scripts/hrmwtp.py decision
python3 scripts/hrmwtp.py portfolio
python3 scripts/hrmwtp.py list-reports
sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256
python3 scripts/check_artifact_hash_coverage.py
python3 scripts/check_no_local_paths.py
python3 scripts/check_claim_boundary.py
git diff --check
```

## Expected Results

- Unit tests pass.
- JSON reports validate.
- Artifact hashes verify.
- Artifact hash coverage passes.
- Local-path hygiene passes.
- Claim-boundary guard passes.
- Stage 5 remains blocked.
- Stage 6 remains blocked.
- Stage 7 remains blocked.

## Dashboard

The static dashboard is generated at `dashboard/index.html` by:

```bash
python3 scripts/run_hrm_neural_validation_ladder.py
```

The dashboard summarizes simulation-only artifacts. It is not hardware
evidence.
