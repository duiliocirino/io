"""Constrained/isotonic intensity calibration.

The binary gate decides activation. For active rows, an isotonic regression
enforces a non-decreasing mapping from probe score to target intensity. This
avoids negative linear slopes while preserving the gate decision.

This is model-dependent and should be run when the GPU is free.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from sklearn.isotonic import IsotonicRegression
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


def extract_all(model, tokenizer, rows: list[dict], layer: int, device: str) -> list[np.ndarray]:
    hidden: list[np.ndarray] = [None] * len(rows)
    for index, row in enumerate(tqdm(rows, desc="Extracting rows", leave=False)):
        hidden[index] = extract_hidden_layers(model, tokenizer, row["text"], [layer], device)[layer]
    return hidden


def apply_gate_and_isotonic(raw: float, tau: float, iso: IsotonicRegression) -> float:
    if raw < tau:
        return 0.0
    return float(np.clip(iso.predict([raw])[0], 0.0, 1.0))


def main() -> None:
    parser = argparse.ArgumentParser(description="Isotonic intensity calibration")
    parser.add_argument("--model", default="Qwen/Qwen3.5-9B-Base")
    parser.add_argument("--contrastive", type=Path, default=Path("data/calibration/contrastive.jsonl"))
    parser.add_argument("--negative-controls", type=Path, default=Path("data/calibration/negative_controls.jsonl"))
    parser.add_argument("--mixed-labeled", type=Path, default=Path("data/calibration/mixed_labeled.jsonl"))
    parser.add_argument("--gates", type=Path, default=Path("runs/gates-base-8bit.json"))
    parser.add_argument("--layer", type=int, default=19)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--gguf-file", default=None)
    parser.add_argument("--quantization", default=None)
    parser.add_argument("--out-json", type=Path, default=Path("runs/constrained-intensity.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("runs/constrained-intensity.csv"))
    args = parser.parse_args()

    gates = json.loads(args.gates.read_text(encoding="utf-8"))
    contrastive = load_jsonl(args.contrastive)
    negative = load_jsonl(args.negative_controls)
    mixed = load_jsonl(args.mixed_labeled)

    model, tokenizer = load_model(
        args.model,
        dtype=args.dtype,
        device=args.device,
        gguf_file=args.gguf_file,
        quantization=args.quantization,
    )
    contrastive_hidden = extract_all(model, tokenizer, contrastive, args.layer, args.device)
    negative_hidden = extract_all(model, tokenizer, negative, args.layer, args.device)
    mixed_hidden = extract_all(model, tokenizer, mixed, args.layer, args.device)

    channels = sorted({row["channel"] for row in contrastive})
    rows = []

    for channel in channels:
        train_indices = [
            i for i, row in enumerate(contrastive)
            if row["channel"] == channel and row["split"] == "train"
        ]
        if not train_indices:
            continue

        x_train = np.array([contrastive_hidden[i] for i in train_indices])
        y_train = np.array([contrastive[i]["target"] for i in train_indices], dtype=float)
        probe = fit_channel_probe(x_train, y_train, alpha=args.alpha)

        tau = float(gates["gate_metrics"][str(args.layer)][channel]["tau"])

        train_active_raw = np.array([
            float(probe.predict([mixed_hidden[i]])[0])
            for i, row in enumerate(mixed)
            if row["split"] == "train" and row["channels"][channel] > 0.0
        ])
        train_active_target = np.array([
            row["channels"][channel]
            for row in mixed
            if row["split"] == "train" and row["channels"][channel] > 0.0
        ], dtype=float)

        iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
        if len(train_active_raw) >= 1:
            iso.fit(train_active_raw, train_active_target)

        test_active_raw = []
        test_active_target = []
        test_absent_raw = []

        for i, row in enumerate(mixed):
            if row["split"] != "test":
                continue
            raw = float(probe.predict([mixed_hidden[i]])[0])
            if row["channels"][channel] > 0.0:
                test_active_raw.append(raw)
                test_active_target.append(row["channels"][channel])
            else:
                test_absent_raw.append(raw)

        for i, row in enumerate(negative):
            if row["split"] == "test":
                test_absent_raw.append(float(probe.predict([negative_hidden[i]])[0]))

        active_pred = [
            apply_gate_and_isotonic(raw, tau, iso)
            for raw in test_active_raw
        ]
        absent_pred = [
            apply_gate_and_isotonic(raw, tau, iso)
            for raw in test_absent_raw
        ]

        active_mae = float(np.mean(np.abs(np.array(active_pred) - np.array(test_active_target)))) if active_pred else None
        absent_mae = float(np.mean(np.abs(absent_pred))) if absent_pred else None
        gate_recall = float(np.mean(np.array(test_active_raw) >= tau)) if test_active_raw else None
        gate_fpr = float(np.mean(np.array(test_absent_raw) >= tau)) if test_absent_raw else None

        rows.append({
            "channel": channel,
            "tau": tau,
            "active_mae": active_mae,
            "absent_mae": absent_mae,
            "gate_recall": gate_recall,
            "gate_fpr": gate_fpr,
            "deadzone_active_mae": gates["gate_metrics"][str(args.layer)][channel].get("active_mae"),
        })

    report = {
        "model": args.model,
        "device": args.device,
        "dtype": args.dtype,
        "gguf_file": args.gguf_file,
        "quantization": args.quantization,
        "layer": args.layer,
        "gates": str(args.gates),
        "channels": len(channels),
        "rows": rows,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    active_values = [row["active_mae"] for row in rows if row["active_mae"] is not None]
    absent_values = [row["absent_mae"] for row in rows if row["absent_mae"] is not None]
    print(json.dumps({
        "model": args.model,
        "layer": args.layer,
        "channels": len(channels),
        "active_mae": round(float(np.mean(active_values)), 4) if active_values else None,
        "absent_mae": round(float(np.mean(absent_values)), 4) if absent_values else None,
        "out_json": str(args.out_json),
        "out_csv": str(args.out_csv),
    }, indent=2))


if __name__ == "__main__":
    main()
