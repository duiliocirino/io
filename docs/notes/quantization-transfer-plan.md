# Quantization transfer plan

**Last updated:** 2026-10-31

## Purpose

Test whether the latent readout, binary gates, and continuous intensity calibration survive lower-precision model loading. This is a transfer check, not a claim that quantization preserves the same internal geometry.

## Quantization paths

### 1. BF16 reference

The cleanest latent-geometry reference. Keep the BF16 Base and Default runs as the baseline.

### 2. Bitsandbytes 8-bit

This is the practical Python path:

```bash
poetry run python experiments/readout/v1/sweep.py \
  --model Qwen/Qwen3.5-9B-Base \
  --quantization 8bit \
  --layers 10:28 \
  --out-json runs/readout-base-8bit.json \
  --out-csv runs/readout-base-8bit.csv
```

Caveat: bitsandbytes `MatMul8bitLt` casts incoming BF16 activations to FP16. The run is therefore **8-bit weights + FP16 compute**, not BF16 compute. Record this in metadata.

### 3. GGUF Q8/Q6 through Transformers

Transformers can load a GGUF checkpoint with `--gguf-file`, but on this Linux GPU the published GGUF matmul kernel has no x86_64 CUDA build. Transformers therefore dequantizes the whole model.

That gives a **weight-only quantized checkpoint dequantized to FP16/FP32**, not true Q8/Q6 matmul. It is still useful as a weight-quantization transfer check, but it must be labeled as dequantized.

```bash
poetry run python experiments/readout/v1/sweep.py \
  --model models/qwen3.5-base-q6 \
  --gguf-file Qwen3.5-9B-Base.Q6_K.gguf \
  --layers 10:28 \
  --out-json runs/readout-base-q6-dequantized.json \
  --out-csv runs/readout-base-q6-dequantized.csv
```

### 4. GGUF through llama.cpp

This is the true GGUF compute path. It is not plug-and-play for layer readout: llama.cpp does not expose per-layer residual streams in the same way Transformers hooks do. A custom C++ hook or a modified llama.cpp build is needed.

Use this only if exact Q6/Q8 matmul behavior is required.

## What to compare

For each backend, run:

1. readout sweep;
2. gate calibration;
3. intensity calibration.

Compare:

- held-out R²/MSE/MAE;
- confusion and per-channel errors;
- gate F1, FPR, recall;
- active and absent MAE;
- best layer for readout vs gate vs intensity;
- per-channel threshold shifts.

Do not reuse BF16 thresholds or layer choices on a quantized model. Recalibrate on the exact backend.

## Current 8-bit result

The bitsandbytes 8-bit run is close to BF16:

- readout layer 14: mean R² ≈ 0.864 vs 0.865;
- gate best layer shifts from 23 to 19;
- intensity best layer shifts from 23 to 19;
- 8-bit gate/intensity metrics are slightly better.

This suggests coarse readout survives 8-bit loading, but gate/intensity calibration is backend-sensitive.

## Q6-dequantized result

`models/qwen3.5-base-q6/Qwen3.5-9B-Base.Q6_K.gguf` was run through native Transformers GGUF. It dequantizes on this GPU, so the result is **Q6 weights + dequantized BF16 compute**, not true Q6 matmul.

- readout layer 14: mean R² ≈ 0.865 vs BF16 0.865;
- Q6 coarse error ≈ 12.7%;
- gate best layer shifts to 28, mean F1 ≈ 0.622 vs BF16 0.626;
- intensity best layer shifts to 23, active MAE ≈ 0.308 vs BF16 0.304.

Q6-dequantized readout is close; gates and intensity are close but slightly weaker than the 8-bit run. This is a weight-only transfer check, not proof of true Q6_K behavior.

## Decision gate

Q6-dequantized readout and gates do not degrade substantially. Treat Q6 as a deployment candidate only after true Q6 inference is tested with llama.cpp or a custom backend. Recalibrate thresholds on the exact backend.

No thresholds or final architecture are selected here.
