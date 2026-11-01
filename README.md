# io
Getting a grasp on human like programs

## Research and presentations

- [Research library](docs/index.html): browse all research documents, companion decks, and working notes.
- [Emotion research document](docs/research/emotions-research-document.html): theory, evidence, references, and an interpretable state model.
- [Emotion presentation deck](docs/research/emotions-presentation-deck.html): a ten-slide guided summary.
- [Cognitive routing and attention research](docs/research/cognitive-routing-research-document.html): network coordination, cooperation, subdivisions, evidence limits, and open architectural questions.
- [Cognitive routing presentation deck](docs/research/cognitive-routing-presentation-deck.html): a twelve-slide introduction linked to the full research.
- [Memory systems research](docs/research/memory-systems-research-document.html): complementary learning, working memory, encoding, retrieval, consolidation, schema assimilation, reconsolidation, and open engineering candidates.
- [Memory systems presentation deck](docs/research/memory-systems-presentation-deck.html): a twelve-slide introduction linked to the full research.
- [Valuation, gating, and modulation research](docs/research/valuation-gating-modulation-research-document.html): Layers 5–7, affect, social homeostasis, curiosity, basal-ganglia gating, and neuromodulatory control.
- [Valuation, gating, and modulation presentation deck](docs/research/valuation-gating-modulation-presentation-deck.html): a twelve-slide introduction linked to the full research.

Open the HTML files directly in a modern browser. Keep `docs/assets/` alongside the documents; no installation, build step, or network connection is needed to read them. External references require internet access.

## Installation

Use Python 3.13 in this environment; Python 3.14.3 here lacks `_lzma`, which breaks `torchvision` imports.

```bash
poetry env use /home/duilio999/.local/share/uv/python/cpython-3.13-linux-x86_64-gnu/bin/python3.13
poetry install --extras "multimodal acceleration gguf quantization"
```

The `multimodal` extra adds `pillow` and `torchvision` for later image experiments. The `acceleration` extra adds `causal-conv1d` and `flash-linear-attention` for optimized Qwen kernels. The `gguf` extra adds `gguf` and `kernels` for GGUF loading. The `quantization` extra adds `bitsandbytes` for true 8-bit weight loading. Text-only readout uses `AutoTokenizer` and does not need the multimodal extras.

## Latent experiment scaffold

- [`pyproject.toml`](pyproject.toml): Poetry project with `python >= 3.13`, minimal runtime dependencies, and a dev `pytest` group.
- [`src/io_brain/brain/`](src/io_brain/brain): reusable model loading, residual-stream hooks, and probe fitting.
- [`experiments/readout/v1/`](experiments/readout/v1): first readout-only calibration.
- [`data/calibration/rubric.md`](data/calibration/rubric.md): coarse 27-channel calibration anchors.
- [`data/calibration/contrastive.jsonl`](data/calibration/contrastive.jsonl): 864 per-channel contrastive rows.
- [`data/calibration/mixed.jsonl`](data/calibration/mixed.jsonl): 162 active-channel scenarios for later validation.
- [`data/calibration/negative_controls.jsonl`](data/calibration/negative_controls.jsonl): 110 all-zero rows for false-positive calibration.
- [`data/calibration/mixed_labeled.jsonl`](data/calibration/mixed_labeled.jsonl): 110 fully labeled multi-channel rows.
- `runs/`, `models/`, and `data/raw/` are gitignored.

## Research and source exploration

- [Research map](docs/notes/research-map.md): a compact topic overview, discussion status, and next questions.
- [Learning notebook](docs/notes/cognitive-architecture-learning.md): discussion checkpoints, source notes, and open questions—not a finished specification.
- [Source gap register](docs/notes/source-gap-register.md): consolidated coverage audit and open integration questions.

## Practical experiments

- [Practical experiments hub](docs/experiments/index.html): separate exploratory track for model-specific readout and steering work.
- [Qwen 3.5 9B readout analysis](docs/experiments/qwen-latent-readout-analysis.html): narrative report with BF16, 8-bit, and Q6-dequantized results.
- [Qwen 3.5 9B latent experiment plan](docs/notes/qwen-latent-experiment-plan.md): model variants, layer sweep, probe calibration, and steering tests.
- [Quantization transfer plan](docs/notes/quantization-transfer-plan.md): BF16, bitsandbytes 8-bit, and GGUF Q8/Q6 caveats.

## HTML design system

See [the design system guide](docs/design-system.md) for the editorial style, accessibility and authoring conventions, and reusable [document](docs/templates/document.html), [slide](docs/templates/slides.html), and [social carousel](docs/templates/social.html) templates.

The system has two [design versions](docs/design-system.md#design-versions): v1 (warm paper and orange) and v2 (cleaner off-white, green structure, citron highlights, and points as the signature element). The research pages and templates use v2. Remove `data-io-theme="v2"` from a page's `<html>` to return it to v1; the original v1 state is also tagged as `design-v1`.
