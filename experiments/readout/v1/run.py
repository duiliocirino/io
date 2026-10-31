"""Readout-only calibration for Qwen 3.5 9B.

Extract mean-pooled residual states at one decoder layer, train per-channel
ridge probes, and report held-out R2/MSE. This does not modify the model.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import tomllib

import numpy as np
from sklearn.model_selection import train_test_split

from io_brain.brain.model import load_model
from io_brain.brain.readout import evaluate_probe, extract_hidden, fit_channel_probe


def load_config(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_rows(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Qwen 3.5 9B readout calibration")
    parser.add_argument("--config", type=Path, default=Path("experiments/readout/v1/config.toml"))
    parser.add_argument("--model", default=None)
    parser.add_argument("--layer", type=int, default=None)
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--device", default=None)
    parser.add_argument("--dtype", default=None)
    parser.add_argument("--gguf-file", default=None)
    parser.add_argument("--quantization", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    model_id = args.model or config["model"]["id"]
    layer = args.layer or config["model"]["layer"]
    data_path = args.data or Path(config["data"]["path"])
    out_path = args.out or Path(config["output"]["path"])
    device = args.device or config["model"]["device"]
    dtype = args.dtype or config["model"]["dtype"]

    rows = load_rows(data_path)
    by_channel: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_channel[row["channel"]].append(row)

    model, tokenizer = load_model(
        model_id,
        dtype=dtype,
        device=device,
        gguf_file=args.gguf_file,
        quantization=args.quantization,
    )

    results: dict[str, dict[str, float | int]] = {}
    for channel, items in sorted(by_channel.items()):
        if len(items) < 2:
            continue

        train = [item for item in items if item.get("split") == "train"]
        test = [item for item in items if item.get("split") == "test"]
        if not train or not test:
            train, test = train_test_split(items, test_size=0.25, random_state=0)

        x_train = np.array([
            extract_hidden(model, tokenizer, item["text"], layer, device)
            for item in train
        ])
        y_train = np.array([item["target"] for item in train], dtype=float)
        x_test = np.array([
            extract_hidden(model, tokenizer, item["text"], layer, device)
            for item in test
        ])
        y_test = np.array([item["target"] for item in test], dtype=float)

        probe = fit_channel_probe(x_train, y_train)
        results[channel] = {
            "train_n": len(train),
            "test_n": len(test),
            **evaluate_probe(probe, x_test, y_test),
        }

    payload = {
        "model": model_id,
        "layer": layer,
        "device": device,
        "dtype": dtype,
        "gguf_file": args.gguf_file,
        "quantization": args.quantization,
        "rows": len(rows),
        "channels": results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
