"""Model loading and decoder-layer access for Qwen 3.5."""
from __future__ import annotations

from typing import Any

import torch

DEFAULT_MODEL = "Qwen/Qwen3.5-9B"
BASE_MODEL = "Qwen/Qwen3.5-9B-Base"


def load_model(
    model_id: str,
    dtype: str = "bfloat16",
    device: str = "cuda",
    gguf_file: str | None = None,
    quantization: str | None = None,
) -> tuple[Any, Any]:
    """Load a Qwen 3.5 model and its text tokenizer.

    - `gguf_file`: load a GGUF causal-LM checkpoint.
    - `quantization="8bit"`: load an 8-bit bitsandbytes model.
    - otherwise: load the multimodal model class.

    The tokenizer is used instead of AutoProcessor because the readout
    experiments are text-only.
    """
    from transformers import AutoModelForCausalLM, AutoModelForImageTextToText, AutoTokenizer

    torch_dtype = getattr(torch, dtype)
    if gguf_file is not None and quantization is not None:
        raise ValueError("Choose either gguf_file or quantization, not both")

    if quantization == "8bit":
        from transformers import BitsAndBytesConfig

        model = AutoModelForImageTextToText.from_pretrained(
            model_id,
            quantization_config=BitsAndBytesConfig(load_in_8bit=True),
            device_map=device,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_id)
    elif gguf_file is not None:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            gguf_file=gguf_file,
            dtype=torch_dtype,
            device_map=device,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_id, gguf_file=gguf_file)
    else:
        model = AutoModelForImageTextToText.from_pretrained(
            model_id,
            dtype=torch_dtype,
            device_map=device,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_id)

    model.eval()
    return model, tokenizer


def get_decoder_layers(model: Any) -> torch.nn.ModuleList:
    """Find the text-decoder layer list without assuming one Qwen layout."""
    candidates = (
        "model.language_model.layers",
        "language_model.layers",
        "model.layers",
        "layers",
    )
    for path in candidates:
        node = model
        for part in path.split("."):
            node = getattr(node, part, None)
            if node is None:
                break
        if isinstance(node, torch.nn.ModuleList):
            return node
    raise AttributeError("Could not locate decoder layers; inspect the model structure.")
