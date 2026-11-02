# Readout robustness plan

**Last updated:** 2026-11-01

## Purpose

Test whether the 27-channel readout is stable enough to support later steering. Robustness is separate from raw held-out R²: a probe can fit the calibration rows and still fail under different pooling, thresholds, perspectives, or lexical controls.

## Checks

### 1. Cross-validation

Run per-channel k-fold cross-validation on the contrastive rows. Report mean R², standard deviation, and MAE across folds. This tests whether the probe depends on a particular train/test split.

### 2. Pooling

Compare mean-pooled hidden states with last-token hidden states at the readout layer. If last-token pooling is much weaker, the readout depends on sequence aggregation rather than a single final state.

### 3. Lexical / negative controls

Use the all-zero technical prompts as lexical/negative controls. Measure the mean absolute probe prediction and the false-positive rate against gate thresholds. This checks whether neutral text triggers affect channels.

### 4. Perspective-stratified errors

Report the worst perspective and MAE spread for each channel. A channel that is much harder to read in first-person, third-person, observer, quoted, or neutral perspective is less stable as a control signal.

### 5. Threshold stability

Compare gate thresholds and F1 across BF16, 8-bit, and Q6-dequantized runs. Thresholds should not be copied across backends without recalibration.

### 6. Constrained / isotonic intensity

Fit an isotonic mapping on active rows instead of an unconstrained linear slope. This prevents negative slopes while preserving the binary gate decision.

## Current model-independent results

`experiments/readout/v1/threshold_stability.py` reports:

- mean absolute threshold shift: 8-bit ≈ 0.015, Q6-dequantized ≈ 0.007;
- mean F1 change: 8-bit ≈ −0.011, Q6-dequantized ≈ −0.003;
- largest shifts: interest, anxiety, awkwardness, craving, entrancement, horror.

`experiments/readout/v1/perspective_diagnostics.py` reports:

- mean perspective MAE spread: BF16 ≈ 0.0845, 8-bit ≈ 0.0844, Q6-dequantized ≈ 0.0846;
- largest spreads: sexual_desire, adoration, satisfaction, anxiety, fear, empathetic_pain, admiration.

These suggest that perspective sensitivity is stable across backends, but thresholds and some channels remain backend-sensitive.

## Model-dependent results

`experiments/readout/v1/robustness.py` was run on BF16 Base at layer 14 with 5 folds:

- mean-pooled held-out R² ≈ 0.865, MAE ≈ 0.140;
- last-token R² ≈ 0.813, MAE ≈ 0.158;
- 5-fold cross-validation R² ≈ 0.785, MAE ≈ 0.151;
- lexical/negative-control MAE ≈ 0.182, mean FPR ≈ 0.0024;
- perspective spread ≈ 0.0845.

This supports mean pooling over last-token pooling, but the cross-validation R² is lower than the single train/test split. The split result is therefore somewhat optimistic; cross-validation is the more conservative estimate.

`experiments/readout/v1/constrained_intensity.py` was run on the 8-bit model at layer 19:

- isotonic active MAE ≈ 0.281 vs unconstrained ≈ 0.297;
- absent MAE ≈ 0.0314 vs 0.0316;
- gate recall ≈ 0.743, gate FPR ≈ 0.0429;
- deadzone active MAE ≈ 0.5445.

Isotonic calibration improves the overall active MAE, but some channels worsen slightly. The gate decision remains the same; only the active-row intensity mapping changes.

```bash
poetry run python experiments/readout/v1/robustness.py \
  --model Qwen/Qwen3.5-9B-Base \
  --layer 14 \
  --out-json runs/robustness-base.json \
  --out-csv runs/robustness-base.csv
```

```bash
poetry run python experiments/readout/v1/constrained_intensity.py \
  --model Qwen/Qwen3.5-9B-Base \
  --quantization 8bit \
  --layer 19 \
  --gates runs/gates-base-8bit.json \
  --out-json runs/constrained-intensity-base-8bit.json \
  --out-csv runs/constrained-intensity-base-8bit.csv
```

## Decision gate

The readout is usable for exploratory steering, but not yet control-grade. Mean pooling is better than last-token pooling, lexical false positives are low, and isotonic intensity improves calibration. The cross-validation drop and backend-sensitive thresholds mean steering should be tested cautiously, with random-direction controls and dose-response checks.

No final thresholds or steering policy are selected here.
