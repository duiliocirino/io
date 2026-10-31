"""Separate continuous-intensity calibration from the binary gate.

The gate threshold τ decides whether a channel is active. For active rows,
fit a separate linear calibration raw -> target so intensity is not compressed
by the deadzone formula. Inactive rows are set to 0 by the gate.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm

from io_brain.brain.model import load_model
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


def extract_all(model, tokenizer, rows: list[dict], layers: list[int], device: str) -> dict[int, list[np.ndarray]]:
    hidden: dict[int, list[np.ndarray]] = {layer: [None] * len(rows) for layer in layers}
    for index, row in enumerate(tqdm(rows, desc="Extracting rows")):
        states = extract_hidden_layers(model, tokenizer, row["text"], layers, device)
        for layer in layers:
            hidden[layer][index] = states[layer]
    return hidden


def fit_linear(raw: np.ndarray, target: np.ndarray) -> tuple[float, float]:
    if len(raw) < 2 or np.ptp(raw) == 0:
        return 1.0, 0.0
    slope, intercept = np.polyfit(raw, target, 1)
    return float(slope), float(intercept)


def apply_gate_and_calibration(raw: float, tau: float, slope: float, intercept: float) -> float:
    if raw < tau:
        return 0.0
    return float(np.clip(slope * raw + intercept, 0.0, 1.0))


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate continuous intensity separately from the gate")
    parser.add_argument("--model", default="Qwen/Qwen3.5-9B-Base")
    parser.add_argument("--contrastive", type=Path, default=Path("data/calibration/contrastive.jsonl"))
    parser.add_argument("--negative-controls", type=Path, default=Path("data/calibration/negative_controls.jsonl"))
    parser.add_argument("--mixed-labeled", type=Path, default=Path("data/calibration/mixed_labeled.jsonl"))
    parser.add_argument("--gates", type=Path, default=Path("runs/gates-base.json"))
    parser.add_argument("--layers", default="10:28")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--gguf-file", default=None)
    parser.add_argument("--quantization", default=None)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--out-json", type=Path, default=Path("runs/intensity.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("runs/intensity.csv"))
    args = parser.parse_args()

    gates = json.loads(args.gates.read_text(encoding="utf-8"))
    contrastive = load_jsonl(args.contrastive)
    negative = load_jsonl(args.negative_controls)
    mixed = load_jsonl(args.mixed_labeled)
    layers = parse_layers(args.layers)

    model, tokenizer = load_model(
        args.model,
        dtype=args.dtype,
        device=args.device,
        gguf_file=args.gguf_file,
        quantization=args.quantization,
    )
    contrastive_hidden = extract_all(model, tokenizer, contrastive, layers, args.device)
    negative_hidden = extract_all(model, tokenizer, negative, layers, args.device)
    mixed_hidden = extract_all(model, tokenizer, mixed, layers, args.device)

    report: dict[str, object] = {
        "model": args.model,
        "dtype": args.dtype,
        "device": args.device,
        "gguf_file": args.gguf_file,
        "quantization": args.quantization,
        "layers": layers,
        "gates": str(args.gates),
        "intensity_metrics": {},
    }
    csv_rows: list[dict[str, object]] = []

    for layer in tqdm(layers, desc="Calibrating intensity"):
        layer_metrics: dict[str, object] = {}

        for channel in sorted({row["channel"] for row in contrastive}):
            train_indices = [
                i for i, row in enumerate(contrastive)
                if row["channel"] == channel and row["split"] == "train"
            ]
            if not train_indices:
                continue

            x_train = np.array([contrastive_hidden[layer][i] for i in train_indices])
            y_train = np.array([contrastive[i]["target"] for i in train_indices], dtype=float)
            probe = fit_channel_probe(x_train, y_train, alpha=args.alpha)

            gate = gates["gate_metrics"][str(layer)][channel]
            tau = float(gate["tau"])

            train_active_raw = np.array([
                float(probe.predict([mixed_hidden[layer][i]])[0])
                for i, row in enumerate(mixed)
                if row["split"] == "train" and row["channels"][channel] > 0.0
            ])
            train_active_target = np.array([
                row["channels"][channel]
                for row in mixed
                if row["split"] == "train" and row["channels"][channel] > 0.0
            ], dtype=float)

            slope, intercept = fit_linear(train_active_raw, train_active_target)

            test_active_raw = []
            test_active_target = []
            test_absent_raw = []

            for i, row in enumerate(mixed):
                if row["split"] != "test":
                    continue
                raw = float(probe.predict([mixed_hidden[layer][i]])[0])
                if row["channels"][channel] > 0.0:
                    test_active_raw.append(raw)
                    test_active_target.append(row["channels"][channel])
                else:
                    test_absent_raw.append(raw)

            for i, row in enumerate(negative):
                if row["split"] == "test":
                    test_absent_raw.append(float(probe.predict([negative_hidden[layer][i]])[0]))

            active_pred = [
                apply_gate_and_calibration(raw, tau, slope, intercept)
                for raw in test_active_raw
            ]
            absent_pred = [
                apply_gate_and_calibration(raw, tau, slope, intercept)
                for raw in test_absent_raw
            ]

            active_mae = float(np.mean(np.abs(np.array(active_pred) - np.array(test_active_target)))) if active_pred else None
            absent_mae = float(np.mean(np.abs(absent_pred))) if absent_pred else None
            gate_recall = float(np.mean(np.array(test_active_raw) >= tau)) if test_active_raw else None
            gate_fpr = float(np.mean(np.array(test_absent_raw) >= tau)) if test_absent_raw else None

            channel_metrics = {
                "tau": tau,
                "slope": slope,
                "intercept": intercept,
                "active_mae": active_mae,
                "absent_mae": absent_mae,
                "gate_recall": gate_recall,
                "gate_fpr": gate_fpr,
                "deadzone_active_mae": gate.get("active_mae"),
            }
            layer_metrics[channel] = channel_metrics

            csv_rows.append({
                "model": args.model,
                "layer": layer,
                "channel": channel,
                "tau": tau,
                "slope": slope,
                "intercept": intercept,
                "active_mae": active_mae,
                "absent_mae": absent_mae,
                "gate_recall": gate_recall,
                "gate_fpr": gate_fpr,
                "deadzone_active_mae": gate.get("active_mae"),
            })

        report["intensity_metrics"][str(layer)] = layer_metrics

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "model", "layer", "channel", "tau", "slope", "intercept",
            "active_mae", "absent_mae", "gate_recall", "gate_fpr", "deadzone_active_mae",
        ])
        writer.writeheader()
        writer.writerows(csv_rows)

    print(json.dumps({
        "model": args.model,
        "gguf_file": args.gguf_file,
        "quantization": args.quantization,
        "layers": layers,
        "gates": str(args.gates),
        "out_json": str(args.out_json),
        "out_csv": str(args.out_csv),
    }, indent=2))


if __name__ == "__main__":
    main()
