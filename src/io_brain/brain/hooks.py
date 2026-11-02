"""Residual-stream capture helpers."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import torch


@contextmanager
def capture_layer(layer: torch.nn.Module) -> Iterator[dict[str, torch.Tensor]]:
    """Capture the output tensor of one decoder layer for a single forward pass."""
    captured: dict[str, torch.Tensor] = {}

    def hook(module, inputs, output) -> None:
        captured["output"] = output

    handle = layer.register_forward_hook(hook)
    try:
        yield captured
    finally:
        handle.remove()


@contextmanager
def capture_layers(layers: list[torch.nn.Module]) -> Iterator[dict[int, torch.Tensor]]:
    """Capture several decoder-layer outputs during one forward pass."""
    captured: dict[int, torch.Tensor] = {}
    handles = []

    for index, layer in enumerate(layers):
        def hook(module, inputs, output, index=index) -> None:
            captured[index] = output

        handles.append(layer.register_forward_hook(hook))

    try:
        yield captured
    finally:
        for handle in handles:
            handle.remove()


def mean_pool(hidden: torch.Tensor) -> torch.Tensor:
    """Mean-pool across the sequence dimension, preserving the hidden dimension."""
    return hidden.mean(dim=1)


def last_token_pool(hidden: torch.Tensor) -> torch.Tensor:
    """Take the final token's residual state, preserving the hidden dimension."""
    return hidden[:, -1]


def pool_hidden(hidden: torch.Tensor, pooling: str = "mean") -> torch.Tensor:
    """Pool a residual stream with a named strategy."""
    if pooling == "mean":
        return mean_pool(hidden)
    if pooling == "last":
        return last_token_pool(hidden)
    raise ValueError(f"Unknown pooling strategy: {pooling}")
