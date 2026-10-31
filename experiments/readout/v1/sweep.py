"""Layer sweep for Qwen 3.5 latent affect readout.

For each decoder layer, train one ridge probe per channel on the contrastive
training rows, evaluate on held-out rows, and report compact metrics:

- held-out R2, MSE, MAE;
- coarse target confusion;
- perspective-stratified MAE;
- probe-direction cosine similarity;
- high-vs-low channel centroid distance;
- mixed-state active/absent prediction error.

Outputs JSON and CSV; no model weights are modified.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from tqdm import tqdm

from io_brain.brain.model import get_decoder_layers, load_model
from io_brain.brain.readout import extract_hidden_layers, fit_channel_probe


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def parse_layers(value: str) -> list[int]:
    start, end = value.split(":")
    return list(range(int(start), int(end) + 1))


def coarse(value: float) -> float:
    if value < 0.25:
        return 0.0
    if value < 0.75:
        return 0.5
    return 1.0


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def main() -> None:
    parser = argparse.ArgumentParser(description="Qwen 3.5 layer sweep")
    parser.add_argument("--model", default="Qwen/Qwen3.5-9B-Base")
    parser.add_argument("--data", type=Path, default=Path("data/calibration/contrastive.jsonl"))
    parser.add_argument("--mixed", type=Path, default=Path("data/calibration/mixed.jsonl"))
    parser.add_argument("--layers", default="10:28")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--gguf-file", default=None)
    parser.add_argument("--quantization", default=None)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--out-json", type=Path, default=Path("runs/readout-sweep.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("runs/readout-sweep.csv"))
    args = parser.parse_args()

    rows = load_jsonl(args.data)
    mixed_rows = load_jsonl(args.mixed) if args.mixed.exists() else []
    layer_indices = parse_layers(args.layers)

    by_channel: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        by_channel[row["channel"]].append(index)

    model, tokenizer = load_model(
        args.model,
        dtype=args.dtype,
        device=args.device,
        gguf_file=args.gguf_file,
        quantization=args.quantization,
    )
    layers = get_decoder_layers(model)

    # Extract all selected layers once per row.
    hidden: dict[int, list[np.ndarray | None]] = {
        layer: [None] * len(rows) for layer in layer_indices
    }
    for index, row in tqdm(enumerate(rows), total=len(rows), desc="Extracting layers"):
        states = extract_hidden_layers(model, tokenizer, row["text"], layer_indices, args.device)
        for layer in layer_indices:
            hidden[layer][index] = states[layer]

    report: dict[str, object] = {
        "model": args.model,
        "device": args.device,
        "dtype": args.dtype,
        "gguf_file": args.gguf_file,
        "quantization": args.quantization,
        "layers": layer_indices,
        "rows": len(rows),
        "mixed_rows": len(mixed_rows),
        "layer_metrics": {},
    }

    csv_rows: list[dict[str, object]] = []

    for layer in tqdm(layer_indices, desc="Training probes"):
        channel_metrics: dict[str, dict[str, object]] = {}
        probes = {}
        coefficients = {}

        for channel, indices in sorted(by_channel.items()):
            train_indices = [i for i in indices if rows[i]["split"] == "train"]
            test_indices = [i for i in indices if rows[i]["split"] == "test"]
            if not train_indices or not test_indices:
                continue

            x_train = np.array([hidden[layer][i] for i in train_indices])
            y_train = np.array([rows[i]["target"] for i in train_indices], dtype=float)
            x_test = np.array([hidden[layer][i] for i in test_indices])
            y_test = np.array([rows[i]["target"] for i in test_indices], dtype=float)

            probe = fit_channel_probe(x_train, y_train, alpha=args.alpha)
            prediction = probe.predict(x_test)
            probes[channel] = probe
            coefficients[channel] = probe.coef_

            r2 = float(probe.score(x_test, y_test))
            mse = float(np.mean((prediction - y_test) ** 2))
            mae = float(np.mean(np.abs(prediction - y_test)))

            perspective_metrics: dict[str, dict[str, float]] = {}
            for perspective in sorted({rows[i]["perspective"] for i in test_indices}):
                subset = [i for i in test_indices if rows[i]["perspective"] == perspective]
                pred = probe.predict(np.array([hidden[layer][i] for i in subset]))
                truth = np.array([rows[i]["target"] for i in subset], dtype=float)
                perspective_metrics[perspective] = {
                    "n": len(subset),
                    "mae": float(np.mean(np.abs(pred - truth))),
                    "r2": float(probe.score(np.array([hidden[layer][i] for i in subset]), truth))
                    if len(subset) >= 2
                    else None,
                }

            confusion = Counter()
            for actual, pred in zip(y_test, prediction):
                confusion[(float(actual), coarse(float(pred)))] += 1

            channel_metrics[channel] = {
                "train_n": len(train_indices),
                "test_n": len(test_indices),
                "r2": r2,
                "mse": mse,
                "mae": mae,
                "coef_norm": float(np.linalg.norm(probe.coef_)),
                "perspective": perspective_metrics,
                "confusion": [
                    {
                        "actual": actual,
                        "predicted": predicted,
                        "count": count,
                    }
                    for (actual, predicted), count in sorted(confusion.items())
                ],
            }

            csv_rows.append({
                "model": args.model,
                "layer": layer,
                "channel": channel,
                "train_n": len(train_indices),
                "test_n": len(test_indices),
                "r2": r2,
                "mse": mse,
                "mae": mae,
                "coef_norm": float(np.linalg.norm(probe.coef_)),
            })

        # Probe-direction similarity.
        probe_cosine = {}
        for channel_a in sorted(coefficients):
            probe_cosine[channel_a] = {
                channel_b: cosine(coefficients[channel_a], coefficients[channel_b])
                for channel_b in sorted(coefficients)
            }

        # High-vs-low channel centroids.
        centroid_distance = {}
        for channel, indices in sorted(by_channel.items()):
            high = [i for i in indices if rows[i]["target"] == 1.0]
            low = [i for i in indices if rows[i]["target"] == 0.0]
            if high and low:
                high_centroid = np.mean(np.array([hidden[layer][i] for i in high]), axis=0)
                low_centroid = np.mean(np.array([hidden[layer][i] for i in low]), axis=0)
                centroid_distance[channel] = float(np.linalg.norm(high_centroid - low_centroid))

        # Mixed-state validation.
        mixed_metrics = {"active_mae": None, "absent_mae": None, "rows": len(mixed_rows)}
        if mixed_rows and probes:
            active_errors = []
            absent_errors = []
            for row in tqdm(mixed_rows, desc=f"Mixed validation layer {layer}", leave=False):
                state = extract_hidden_layers(model, tokenizer, row["text"], [layer], args.device)[layer]
                active = row["channels"]
                for channel, target in active.items():
                    if channel in probes:
                        active_errors.append(abs(float(probes[channel].predict([state])[0]) - target))
                for channel, probe in probes.items():
                    if channel not in active:
                        absent_errors.append(abs(float(probe.predict([state])[0])))
            mixed_metrics["active_mae"] = float(np.mean(active_errors)) if active_errors else None
            mixed_metrics["absent_mae"] = float(np.mean(absent_errors)) if absent_errors else None

        r2_values = [metric["r2"] for metric in channel_metrics.values()]
        mae_values = [metric["mae"] for metric in channel_metrics.values()]
        report["layer_metrics"][str(layer)] = {
            "channels": channel_metrics,
            "mean_r2": float(np.mean(r2_values)) if r2_values else None,
            "median_r2": float(np.median(r2_values)) if r2_values else None,
            "mean_mae": float(np.mean(mae_values)) if mae_values else None,
            "probe_cosine": probe_cosine,
            "centroid_distance": centroid_distance,
            "mixed": mixed_metrics,
        }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "model", "layer", "channel", "train_n", "test_n", "r2", "mse", "mae", "coef_norm"
        ])
        writer.writeheader()
        writer.writerows(csv_rows)

    print(json.dumps({
        "model": args.model,
        "gguf_file": args.gguf_file,
        "quantization": args.quantization,
        "layers": layer_indices,
        "rows": len(rows),
        "mixed_rows": len(mixed_rows),
        "out_json": str(args.out_json),
        "out_csv": str(args.out_csv),
    }, indent=2))


if __name__ == "__main__":
    main()
