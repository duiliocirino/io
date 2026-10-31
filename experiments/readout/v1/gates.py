"""Calibrate per-channel activation gates from probe outputs.

For each layer and channel:

- train a ridge probe on contrastive rows;
- select a binary threshold with an FPR cap on negative controls and
  explicit 0.0 channels;
- also report a Youden-J threshold as a diagnostic;
- apply a shifted deadzone for continuous readout;
- evaluate train/test FPR, recall, precision, F1, active MAE, absent MAE.

Outputs JSON and CSV; model weights are not modified.
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


def binary_metrics(negatives: np.ndarray, positives: np.ndarray, tau: float) -> dict[str, float | int]:
    predicted_neg = negatives >= tau
    predicted_pos = positives >= tau
    tp = int(np.sum(predicted_pos))
    fn = int(len(positives) - tp)
    fp = int(np.sum(predicted_neg))
    tn = int(len(negatives) - fp)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "fpr": fp / (fp + tn) if fp + tn else 0.0,
        "recall": recall,
        "precision": precision,
        "f1": f1,
    }


def choose_fpr_threshold(negatives: np.ndarray, positives: np.ndarray, fpr_cap: float) -> float:
    candidates = sorted(set(np.concatenate([negatives, positives])))
    for tau in candidates:
        fpr = float(np.mean(negatives >= tau))
        if fpr <= fpr_cap:
            return float(tau)
    return float(np.max(negatives) + 1e-6) if len(negatives) else 0.0


def choose_youden_threshold(negatives: np.ndarray, positives: np.ndarray) -> tuple[float, float]:
    candidates = sorted(set(np.concatenate([negatives, positives])))
    best_tau = 0.0
    best_j = -1.0
    for tau in candidates:
        sensitivity = float(np.mean(positives >= tau))
        specificity = float(np.mean(negatives < tau))
        j = sensitivity + specificity - 1.0
        if j > best_j:
            best_j = j
            best_tau = float(tau)
    return best_tau, best_j


def calibrated(value: float, tau: float) -> float:
    if tau >= 1.0:
        return 0.0
    return float(np.clip(max(0.0, value - tau) / (1.0 - tau), 0.0, 1.0))


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate per-channel activation gates")
    parser.add_argument("--model", default="Qwen/Qwen3.5-9B-Base")
    parser.add_argument("--contrastive", type=Path, default=Path("data/calibration/contrastive.jsonl"))
    parser.add_argument("--negative-controls", type=Path, default=Path("data/calibration/negative_controls.jsonl"))
    parser.add_argument("--mixed-labeled", type=Path, default=Path("data/calibration/mixed_labeled.jsonl"))
    parser.add_argument("--layers", default="10:28")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--gguf-file", default=None)
    parser.add_argument("--quantization", default=None)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--fpr-cap", type=float, default=0.05)
    parser.add_argument("--out-json", type=Path, default=Path("runs/gates.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("runs/gates.csv"))
    args = parser.parse_args()

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
        "fpr_cap": args.fpr_cap,
        "gate_metrics": {},
    }
    csv_rows: list[dict[str, object]] = []

    for layer in tqdm(layers, desc="Calibrating gates"):
        layer_metrics: dict[str, object] = {}

        for channel in sorted({row["channel"] for row in contrastive}):
            train_indices = [i for i, row in enumerate(contrastive) if row["channel"] == channel and row["split"] == "train"]
            if not train_indices:
                continue

            x_train = np.array([contrastive_hidden[layer][i] for i in train_indices])
            y_train = np.array([contrastive[i]["target"] for i in train_indices], dtype=float)
            probe = fit_channel_probe(x_train, y_train, alpha=args.alpha)

            # Negative controls: every row is all-zero.
            neg_train = np.array([
                float(probe.predict([negative_hidden[layer][i]])[0])
                for i, row in enumerate(negative)
                if row["split"] == "train"
            ])
            neg_test = np.array([
                float(probe.predict([negative_hidden[layer][i]])[0])
                for i, row in enumerate(negative)
                if row["split"] == "test"
            ])

            # Mixed labeled: active channels are positives; explicit zeros are negatives.
            mixed_train_pos = np.array([
                float(probe.predict([mixed_hidden[layer][i]])[0])
                for i, row in enumerate(mixed)
                if row["split"] == "train" and row["channels"][channel] > 0.0
            ])
            mixed_train_neg = np.array([
                float(probe.predict([mixed_hidden[layer][i]])[0])
                for i, row in enumerate(mixed)
                if row["split"] == "train" and row["channels"][channel] == 0.0
            ])
            mixed_test_pos = np.array([
                float(probe.predict([mixed_hidden[layer][i]])[0])
                for i, row in enumerate(mixed)
                if row["split"] == "test" and row["channels"][channel] > 0.0
            ])
            mixed_test_neg = np.array([
                float(probe.predict([mixed_hidden[layer][i]])[0])
                for i, row in enumerate(mixed)
                if row["split"] == "test" and row["channels"][channel] == 0.0
            ])

            train_negatives = np.concatenate([neg_train, mixed_train_neg])
            train_positives = mixed_train_pos
            test_negatives = np.concatenate([neg_test, mixed_test_neg])
            test_positives = mixed_test_pos

            if not len(train_positives) or not len(train_negatives):
                continue

            tau = max(0.0, choose_fpr_threshold(train_negatives, train_positives, args.fpr_cap))
            youden_tau, youden_j = choose_youden_threshold(train_negatives, train_positives)

            train_metrics = binary_metrics(train_negatives, train_positives, tau)
            test_metrics = binary_metrics(test_negatives, test_positives, tau)

            # Continuous calibrated values on test rows.
            active_errors = []
            absent_errors = []
            for i, row in enumerate(mixed):
                if row["split"] != "test":
                    continue
                raw = float(probe.predict([mixed_hidden[layer][i]])[0])
                value = calibrated(raw, tau)
                if row["channels"][channel] > 0.0:
                    active_errors.append(abs(value - row["channels"][channel]))
                else:
                    absent_errors.append(abs(value))
            for i, row in enumerate(negative):
                if row["split"] != "test":
                    continue
                raw = float(probe.predict([negative_hidden[layer][i]])[0])
                absent_errors.append(abs(calibrated(raw, tau)))

            channel_metrics = {
                "tau": tau,
                "youden_tau": youden_tau,
                "youden_j": youden_j,
                "train": train_metrics,
                "test": test_metrics,
                "active_mae": float(np.mean(active_errors)) if active_errors else None,
                "absent_mae": float(np.mean(absent_errors)) if absent_errors else None,
            }
            layer_metrics[channel] = channel_metrics

            csv_rows.append({
                "model": args.model,
                "layer": layer,
                "channel": channel,
                "tau": tau,
                "youden_tau": youden_tau,
                "youden_j": youden_j,
                "train_fpr": train_metrics["fpr"],
                "train_recall": train_metrics["recall"],
                "train_precision": train_metrics["precision"],
                "train_f1": train_metrics["f1"],
                "test_fpr": test_metrics["fpr"],
                "test_recall": test_metrics["recall"],
                "test_precision": test_metrics["precision"],
                "test_f1": test_metrics["f1"],
                "active_mae": channel_metrics["active_mae"],
                "absent_mae": channel_metrics["absent_mae"],
            })

        report["gate_metrics"][str(layer)] = layer_metrics

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "model", "layer", "channel", "tau", "youden_tau", "youden_j",
            "train_fpr", "train_recall", "train_precision", "train_f1",
            "test_fpr", "test_recall", "test_precision", "test_f1",
            "active_mae", "absent_mae",
        ])
        writer.writeheader()
        writer.writerows(csv_rows)

    print(json.dumps({
        "model": args.model,
        "gguf_file": args.gguf_file,
        "quantization": args.quantization,
        "layers": layers,
        "fpr_cap": args.fpr_cap,
        "out_json": str(args.out_json),
        "out_csv": str(args.out_csv),
    }, indent=2))


if __name__ == "__main__":
    main()
