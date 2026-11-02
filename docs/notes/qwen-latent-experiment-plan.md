# Qwen 3.5 9B latent experiment plan

**Last updated:** 2026-10-30

## Purpose

Test whether the 27-channel affective/control state can be read from Qwen 3.5 9B’s latent space and whether steering from that state is causally effective. This is a model-specific experiment, not a final architecture.

## Model variants

Use both variants:

- `Qwen/Qwen3.5-9B` — the standard/default release; assumed to be the instruction-tuned or chat-facing variant. Verify the exact model card before use.
- `Qwen/Qwen3.5-9B-Base` — the pretrained base model, used as a cleaner reference for latent geometry.

The text decoder has **32 layers** and hidden size **4096**. The model also has a **27-layer vision encoder**; text-only experiments should not mix vision-layer readouts unless multimodal behavior is explicitly tested.

## Layer strategy

These are starting ranges, not fixed conclusions:

- **Readout sweep:** text-decoder layers 10–28.
- **Likely readout band:** layers 16–22.
- **Steering sweep:** layers 18–27.
- **Do not select steering layers solely by probe accuracy.** The “Read-Best Is Not Steer-Best” result indicates that probe-best and steer-best layers can diverge.

## Experiment stages

1. **Load both models** in Python with PyTorch and a residual-stream hook tool such as TransformerLens or nnsight.
2. **Extract activations** at each candidate layer for contrastive affect scenarios.
3. **Train 27 probes** using the existing channel taxonomy and GoEmotions-style calibration data. Use cross-validation and held-out scenarios.
4. **Calibrate the readout** with sigmoid/ridge projections; measure expected calibration error and layer stability.
5. **Compare Base vs Default** geometry, probe separability, and valence/arousal alignment.
6. **Test steering** at mid-to-late layers using activation addition. Include random-direction controls.
7. **Measure coherence and safety**: output fluency, off-manifold behavior, refusal/safety shifts, and reversibility.
8. **Connect to a persistent state**: feed readouts into a leaky integrator with decay and set-points; test whether continuity changes behavior.
9. **Instrument telemetry**: log latent vectors, probe values, gating decisions, action traces, and uncertainty.

## Decision gates

- **Gate 1:** Is the 27D readout stable across layers and across Base/Default?
- **Gate 2:** Does steering causally shift affect or control behavior, not just correlate with it?
- **Gate 3:** Is the steering coherent and safe enough to be bounded?
- **Gate 4:** Does the external persistent state improve continuity without destabilizing the model?

If Gate 1 fails, the 27D state is only a diagnostic projection, not a reliable control state. If Gate 2 fails, readout alone is not enough.

## Stack and data

- **Python** with Poetry and `python >= 3.13` for model loading, probes, calibration, and steering.
- Text-only readout uses `AutoTokenizer`; `AutoProcessor` would also load the image processor and require Pillow plus Torchvision.
- Optional extras: `multimodal` for images, `acceleration` for `causal-conv1d` and `flash-linear-attention`, and `gguf` for `gguf`/`kernels`. The sweep reports progress with `tqdm`.
- Q8 GGUF loading uses `AutoModelForCausalLM` and `AutoTokenizer` with `gguf_file`; verify that GPU kernels avoid whole-model dequantization. On this Linux GPU, the published GGUF kernel repo has no x86_64 CUDA build, so Transformers dequantizes. Use `--quantization 8bit` with bitsandbytes for a true 8-bit weight path.
- Reusable code lives in `src/io_brain/brain/`; experiments are versioned under `experiments/`.
- Raw outputs go to `runs/` and are gitignored; model weights stay in the Hugging Face cache.
- Calibration targets are coarse: `0.0`, `0.5`, `1.0`. They are hand-crafted calibration anchors, not measured ground truth.
- The validated data now lives in `data/calibration/contrastive.jsonl` (864 rows, 32 per channel), `data/calibration/mixed.jsonl` (162 active-channel scenarios), `data/calibration/negative_controls.jsonl` (110 all-zero rows), and `data/calibration/mixed_labeled.jsonl` (110 fully labeled rows).
- `experiments/readout/v1/gates.py` calibrates per-channel thresholds with an FPR cap and a shifted deadzone.
- `experiments/readout/v1/intensity.py` separates binary activation from continuous intensity calibration; `intensity_report.py` visualizes the active/absent MAE tradeoff.
- Start with the contrastive file for the first readout experiment; use mixed scenarios later for co-activation validation.
- The rubric is `data/calibration/rubric.md`.
- Q8 is a practical compromise for VRAM; FP16/BF16 is the cleaner reference for latent geometry. Bitsandbytes 8-bit is the practical Python path; native Transformers GGUF dequantizes on this GPU. Q6-dequantized readout, gates, and intensity are now complete; true Q6 still needs llama.cpp or a custom backend.
- **Backend decision:** BF16 is the reference geometry; bitsandbytes 8-bit is the deployment candidate; Q6-dequantized is a weight-transfer check only, not true Q6 production behavior.
- **C++/CUDA** only if the hot projection/steering path becomes a measured bottleneck.
- **C** later for the persistent BrainState and gating kernel, if it proves simpler and faster.

## Output measures

- Per-layer and per-channel held-out R²/MSE/MAE.
- Coarse target confusion.
- Perspective-stratified MAE.
- Probe-direction cosine similarity.
- High-vs-low channel centroid distance.
- Mixed-state active/absent prediction error.
- Base-vs-Default comparison.
- Later, BF16-to-Q8/Q6 transfer metrics. See [quantization transfer plan](quantization-transfer-plan.md) for backend caveats and the [readout analysis](https://duiliocirino.github.io/io/experiments/qwen-latent-readout-analysis.html) for current results.
- Robustness: cross-validation, last-token vs mean pooling, lexical/negative controls, threshold stability, perspective spread, and isotonic intensity. See [readout robustness plan](readout-robustness-plan.md).

`experiments/readout/v1/sweep.py` writes JSON and CSV; `report.py` builds a compact HTML dashboard with a layer summary, channel heatmap, best layer per channel, and mixed-state validation.

## Open questions

- Which exact Qwen 3.5 9B variant is the “Default” model?
- Which layers are read-best versus steer-best?
- How stable are the 27 channels across Base and instruction-tuned versions?
- How much does steering degrade coherence or safety?
- What set-points, decay rates, and gate thresholds are justified by behavior?

No implementation, thresholds, or final architecture are selected here.
