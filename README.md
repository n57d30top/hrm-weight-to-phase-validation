# HRM Weight-to-Phase Validation

This repository contains a simulation-gated future-work validation ladder for HRM neural weight-to-phase mapping.

It does not claim hardware-native intelligence, autonomous cognition, quantum consciousness, power-free computation, quantum advantage, foundry calibration, measured hardware validation, production inference readiness, or an end-to-end hardware benchmark.

This future-work track explores whether selected neural-network weight matrices can be compiled into HRM-style photonic transfer functions. Current evidence is limited to simulation and synthetic calibration.

## Scope

- Stage 0: future-work specification.
- Stage 1: numerical SVD mapping demo.
- Stage 2: deterministic abstract mesh-constrained transfer-matrix approximation.
- Stage 3: quantization, phase noise, drift, loss, coupler imbalance, and detector-noise placeholder model.
- Stage 4: synthetic simulation-only calibration loop.
- Stage 5: foundry-calibrated device-model gate.
- Stage 6: measured HRM transfer-matrix gate.
- Stage 7: end-to-end hardware inference benchmark gate.

Stages 5 through 7 remain blocked unless real foundry-calibrated models, measured transfer matrices, and benchmark evidence are provided.

## Verification

```bash
python3 scripts/run_hrm_neural_mapping_demo.py
python3 scripts/run_hrm_neural_validation_ladder.py
python3 -m unittest discover -s tests -v
jq empty docs/future-work/evidence-ledger.json
jq empty reports/future-work/hrm-neural-mapping/validation-ladder-summary.json
sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256
git diff --check
```
