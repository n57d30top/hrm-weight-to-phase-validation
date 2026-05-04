# Model Portfolio Decision Summary

This is a simulation-only portfolio summary. It is not hardware evidence.

Best simulation candidate: `low_rank_adapter_demo`
Worst simulation candidate: `transformer_block_manifest_only`

## Ranking

| Rank | Model | Score | Class | Unsupported Layers |
| --- | --- | --- | --- | --- |
| 1 | `low_rank_adapter_demo` | 95.882 | good_candidate | 0 |
| 2 | `projection_chain` | 92.222 | good_candidate | 0 |
| 3 | `tiny_mlp` | 87.647 | good_candidate | 0 |
| 4 | `sparse_linear_demo` | 61.0 | partial_candidate | 1 |
| 5 | `transformer_block_manifest_only` | 53.333 | partial_candidate | 4 |

## Claim Boundary

Simulation-only model portfolio planning; this does not claim hardware validation, foundry calibration, measured transfer matrices, production inference readiness, full model acceleration, quantum advantage, hardware-native intelligence, or power-free computation.
