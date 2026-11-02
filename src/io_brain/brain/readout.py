"""Readout extraction and coarse probe fitting."""
from __future__ import annotations

from typing import Any

import numpy as np
import torch
from sklearn.linear_model import Ridge

from .hooks import capture_layer, capture_layers, pool_hidden
from .model import get_decoder_layers


def extract_hidden(
    model: Any,
    tokenizer: Any,
    text: str,
    layer_index: int,
    device: str = "cuda",
    pooling: str = "mean",
) -> np.ndarray:
    """Return a pooled residual stream at one text-decoder layer."""
    inputs = tokenizer(text=text, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}

    layers = get_decoder_layers(model)
    with torch.no_grad():
        with capture_layer(layers[layer_index]) as captured:
            model(**inputs)

    pooled = pool_hidden(captured["output"], pooling).squeeze(0).float()
    return pooled.detach().cpu().numpy()


def extract_hidden_layers(
    model: Any,
    tokenizer: Any,
    text: str,
    layer_indices: list[int],
    device: str = "cuda",
    pooling: str = "mean",
) -> dict[int, np.ndarray]:
    """Return pooled residual states for several decoder layers in one pass."""
    inputs = tokenizer(text=text, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}

    layers = get_decoder_layers(model)
    selected = [(index, layers[index]) for index in layer_indices]
    with torch.no_grad():
        with capture_layers([layer for _, layer in selected]) as captured:
            model(**inputs)

    return {
        index: pool_hidden(captured[position], pooling).squeeze(0).float().detach().cpu().numpy()
        for position, (index, _) in enumerate(selected)
    }


def fit_channel_probe(
    hidden: np.ndarray,
    target: np.ndarray,
    alpha: float = 1.0,
) -> Ridge:
    """Fit a ridge probe for one coarse channel target."""
    probe = Ridge(alpha=alpha)
    probe.fit(hidden, target)
    return probe


def evaluate_probe(probe: Ridge, hidden: np.ndarray, target: np.ndarray) -> dict[str, float]:
    """Report held-out regression quality for one channel."""
    prediction = probe.predict(hidden)
    return {
        "r2": float(probe.score(hidden, target)),
        "mse": float(np.mean((prediction - target) ** 2)),
    }
