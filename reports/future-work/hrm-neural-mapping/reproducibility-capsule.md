# Reproducibility Capsule

This capsule reproduces simulation-only artifacts. It is not hardware evidence.

Expected test count: `186`
Expected report count: `48`

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

## Expected Blocked Stages

- Stage 5: blocked (no_foundry_calibrated_device_model)
- Stage 6: blocked (no_measured_hrm_transfer_matrix)
- Stage 7: blocked (no_end_to_end_hardware_benchmark)

## Claim Boundary

Simulation-only partner-readiness material; this does not claim hardware validation, foundry calibration, measured transfer matrices, production inference readiness, real hardware latency, real hardware energy efficiency, physical accuracy, quantum advantage, hardware-native intelligence, or power-free computation.
