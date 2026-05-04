# Model Portfolio Explainer

This explainer is simulation-only. It is not hardware evidence.

Best model: `low_rank_adapter_demo` because it combines high mappable parameter share with no unsupported layers.
Worst model: `transformer_block_manifest_only` because unsupported attention, embedding, or normalization-like operations dominate the current mapping limitations.

## Promising Future Study Candidates

- low_rank_adapter_demo
- projection_chain
- tiny_mlp

## Poor Candidates

- none below the poor-candidate threshold in this deterministic portfolio

## Unsupported Operations That Dominate

- attention softmax
- embedding
- normalization
- sparse masks that remain classical or unsupported

## Claim Boundary

Simulation-only model portfolio planning; this does not claim hardware validation, foundry calibration, measured transfer matrices, production inference readiness, full model acceleration, quantum advantage, hardware-native intelligence, or power-free computation.
