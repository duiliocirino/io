# Experiments

Reusable code lives in `src/io_brain/brain/`. Experiment scripts live in versioned folders under `experiments/`; raw outputs and logs go to `runs/` and are not committed.

## Versioning

- `experiments/readout/v1/` — first readout-only calibration.
- `experiments/steering/v1/` — later steering experiment.
- `runs/` — generated outputs, gitignored.
- `data/calibration/` — hand-validated calibration data and rubric.

## Calibration files

- `data/calibration/contrastive.jsonl` — 864 per-channel contrastive rows used for the first readout experiment.
- `data/calibration/mixed.jsonl` — 162 multi-channel scenarios for later validation.

`experiments/readout/v1/validate_data.py` checks schema, IDs, targets, perspectives, splits, and mixed-state constraints without ML dependencies.

Text-only readout uses `AutoTokenizer`, not `AutoProcessor`; this avoids the Pillow/Torchvision image-processor dependency. If later experiments use images, install the `multimodal` extra (`pillow`, `torchvision`). For optimized Qwen kernels, install the `acceleration` extra (`causal-conv1d`, `flash-linear-attention`). The sweep shows a `tqdm` progress bar for layer extraction and mixed validation.

`experiments/readout/v1/sweep.py` runs the layer sweep and writes JSON/CSV metrics. `experiments/readout/v1/gates.py` calibrates per-channel activation thresholds on `negative_controls.jsonl` and `mixed_labeled.jsonl`, writing `runs/gates.json` and `runs/gates.csv`. `experiments/readout/v1/intensity.py` calibrates continuous intensity separately from the binary gate: the gate decides activation, then a linear active-row mapping preserves intensity.

Transformers GGUF loading may dequantize the whole model on this Linux GPU because no GGUF matmul kernel is published for the device. For a true 8-bit weight path, use `--quantization 8bit` with `bitsandbytes`:

```bash
poetry run python experiments/readout/v1/sweep.py \
  --model Qwen/Qwen3.5-9B-Base \
  --quantization 8bit \
  --layers 10:28 \
  --out-json runs/readout-base-8bit.json \
  --out-csv runs/readout-base-8bit.csv
```

For Q8/Q6 GGUF, add `--gguf-file` to the readout, gate, and intensity commands:

```bash
poetry run python experiments/readout/v1/sweep.py \
  --model models/qwen3.5-base-q8 \
  --gguf-file Qwen3.5-9B-Base.Q8_0.gguf \
  --layers 10:28 \
  --out-json runs/readout-base-q8.json \
  --out-csv runs/readout-base-q8.csv
```

```bash
poetry run python experiments/readout/v1/sweep.py \
  --model models/qwen3.5-base-q6 \
  --gguf-file Qwen3.5-9B-Base.Q6_K.gguf \
  --layers 10:28 \
  --out-json runs/readout-base-q6-dequantized.json \
  --out-csv runs/readout-base-q6-dequantized.csv
```

Native Transformers GGUF is weight-only/dequantized on this GPU. Label Q6 outputs as `q6-dequantized`, not true Q6 matmul. For true Q6 inference, use llama.cpp with custom layer hooks.

`experiments/readout/v1/intensity_report.py` builds an intensity dashboard with active-MAE trends, heatmaps, selected-layer metrics, negative-slope warnings, and an optional Base-vs-Default comparison. The same scripts can compare BF16 and bitsandbytes 8-bit runs.

`experiments/readout/v1/gate_report.py` builds a gate dashboard with F1/threshold heatmaps, layer summaries, selected-layer metrics, FPR-cap warnings, and an optional Base-vs-Default comparison.

`experiments/readout/v1/narrative_report.py` builds the narrative experiment page from readout, gate, and intensity JSON, with BF16/8-bit charts and an explicit Q6 placeholder:

```bash
poetry run python experiments/readout/v1/narrative_report.py
```

`experiments/readout/v1/report.py` turns the sweep JSON into a compact HTML dashboard with a layer trend, key diagnostics, perspective sensitivity, confusion matrix, confusable-channel diagnostics, and an optional Base-vs-Default comparison:

```bash
poetry run python experiments/readout/v1/report.py \
  --json runs/readout-base.json \
  --compare runs/readout-default.json \
  --out runs/readout-report.html
```

Contrastive schema:

```json
{"id":"a001","text":"...","kind":"contrastive","channel":"anxiety","target":1.0,"perspective":"third_person","split":"train","generated_by":"frontier","reviewed_by":"manual"}
```

Targets are coarse: `0.0`, `0.5`, or `1.0`. They are calibration anchors, not measured ground truth.

## First experiment

`experiments/readout/v1/run.py` extracts mean-pooled hidden states at one decoder layer, trains per-channel ridge probes, and reports held-out R²/MSE.
