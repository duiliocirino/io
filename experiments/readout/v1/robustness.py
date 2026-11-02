"""Robustness checks for the 27-channel readout.

Checks:
- held-out train/test quality for mean pooling and last-token pooling;
- per-channel k-fold cross-validation;
- perspective-stratified error spread;
- lexical/negative-control false positives against gate thresholds.

The script does not modify model weights. It is model-dependent and should be
run when the GPU is free.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
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


def extract_all(
    model,
    tokenizer,
    rows: list[dict],
    layer: int,
    device: str,
    pooling: str,
) -> list[np.ndarray]:
    hidden: list[np.ndarray] = [None] * len(rows)
    for index, row in enumerate(tqdm(rows, desc=f"Extracting {pooling} states", leave=False)):
        hidden[index] = extract_hidden_layers(
            model,
            tokenizer,
            row["text"],
            [layer],
            device,
            pooling=pooling,
        )[layer]
    return hidden


def r2_score(probe: Ridge, x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) < 2 or np.ptp(y) == 0:
        return None
    return float(probe.score(x, y))


def main() -> None:
    parser = argparse.ArgumentParser(description="Readout robustness checks")
    parser.add_argument("--model", default="Qwen/Qwen3.5-9B-Base")
    parser.add_argument("--contrastive", type=Path, default=Path("data/calibration/contrastive.jsonl"))
    parser.add_argument("--negative-controls", type=Path, default=Path("data/calibration/negative_controls.jsonl"))
    parser.add_argument("--gates", type=Path, default=Path("runs/gates-base.json"))
    parser.add_argument("--layer", type=int, default=14)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--gguf-file", default=None)
    parser.add_argument("--quantization", default=None)
    parser.add_argument("--out-json", type=Path, default=Path("runs/robustness.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("runs/robustness.csv"))
    args = parser.parse_args()

    contrastive = load_jsonl(args.contrastive)
    negative = load_jsonl(args.negative_controls)
    gates = json.loads(args.gates.read_text(encoding="utf-8"))

    model, tokenizer = load_model(
        args.model,
        dtype=args.dtype,
        device=args.device,
        gguf_file=args.gguf_file,
        quantization=args.quantization,
    )

    mean_hidden = extract_all(model, tokenizer, contrastive, args.layer, args.device, "mean")
    last_hidden = extract_all(model, tokenizer, contrastive, args.layer, args.device, "last")
    negative_mean = extract_all(model, tokenizer, negative, args.layer, args.device, "mean")

    channels = sorted({row["channel"] for row in contrastive})
    rows = []

    for channel in channels:
        indices = [i for i, row in enumerate(contrastive) if row["channel"] == channel]
        train_indices = [i for i in indices if contrastive[i]["split"] == "train"]
        test_indices = [i for i in indices if contrastive[i]["split"] == "test"]

        y_train = np.array([contrastive[i]["target"] for i in train_indices], dtype=float)
        y_test = np.array([contrastive[i]["target"] for i in test_indices], dtype=float)

        mean_train = np.array([mean_hidden[i] for i in train_indices])
        mean_test = np.array([mean_hidden[i] for i in test_indices])
        last_train = np.array([last_hidden[i] for i in train_indices])
        last_test = np.array([last_hidden[i] for i in test_indices])

        mean_probe = fit_channel_probe(mean_train, y_train, alpha=args.alpha)
        last_probe = fit_channel_probe(last_train, y_train, alpha=args.alpha)

        mean_pred = mean_probe.predict(mean_test)
        last_pred = last_probe.predict(last_test)
        mean_mae = float(np.mean(np.abs(mean_pred - y_test)))
        last_mae = float(np.mean(np.abs(last_pred - y_test)))
        mean_r2 = r2_score(mean_probe, mean_test, y_test)
        last_r2 = r2_score(last_probe, last_test, y_test)

        # Per-channel k-fold cross-validation on all rows.
        cv_r2 = []
        cv_mae = []
        all_mean = np.array([mean_hidden[i] for i in indices])
        all_y = np.array([contrastive[i]["target"] for i in indices], dtype=float)
        kfold = KFold(n_splits=args.folds, shuffle=True, random_state=args.seed)
        for fold_train, fold_test in kfold.split(all_mean):
            probe = fit_channel_probe(all_mean[fold_train], all_y[fold_train], alpha=args.alpha)
            pred = probe.predict(all_mean[fold_test])
            cv_mae.append(float(np.mean(np.abs(pred - all_y[fold_test]))))
            score = r2_score(probe, all_mean[fold_test], all_y[fold_test])
            if score is not None:
                cv_r2.append(score)

        # Perspective spread on the held-out mean-pooled rows.
        perspective = {}
        for perspective_name in sorted({contrastive[i]["perspective"] for i in test_indices}):
            subset = [i for i in test_indices if contrastive[i]["perspective"] == perspective_name]
            pred = mean_probe.predict(np.array([mean_hidden[i] for i in subset]))
            truth = np.array([contrastive[i]["target"] for i in subset], dtype=float)
            perspective[perspective_name] = {
                "n": len(subset),
                "mae": float(np.mean(np.abs(pred - truth))),
            }

        perspective_maes = [item["mae"] for item in perspective.values()]
        worst_perspective = max(perspective, key=lambda key: perspective[key]["mae"]) if perspective else "—"
        perspective_spread = max(perspective_maes) - min(perspective_maes) if perspective_maes else 0.0

        # Lexical/negative-control false positives.
        tau = float(gates["gate_metrics"][str(args.layer)][channel]["tau"])
        negative_pred = np.array([
            float(mean_probe.predict([negative_mean[i]])[0])
            for i in range(len(negative))
        ])
        lexical_mae = float(np.mean(np.abs(negative_pred)))
        lexical_fpr = float(np.mean(negative_pred >= tau))

        rows.append({
            "channel": channel,
            "mean_r2": mean_r2,
            "mean_mae": mean_mae,
            "last_r2": last_r2,
            "last_mae": last_mae,
            "cv_r2_mean": float(np.mean(cv_r2)) if cv_r2 else None,
            "cv_r2_std": float(np.std(cv_r2)) if cv_r2 else None,
            "cv_mae_mean": float(np.mean(cv_mae)) if cv_mae else None,
            "cv_mae_std": float(np.std(cv_mae)) if cv_mae else None,
            "worst_perspective": worst_perspective,
            "perspective_spread": perspective_spread,
            "lexical_mae": lexical_mae,
            "lexical_fpr": lexical_fpr,
        })

    report = {
        "model": args.model,
        "device": args.device,
        "dtype": args.dtype,
        "gguf_file": args.gguf_file,
        "quantization": args.quantization,
        "layer": args.layer,
        "folds": args.folds,
        "alpha": args.alpha,
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

    mean_r2_values = [row["mean_r2"] for row in rows if row["mean_r2"] is not None]
    mean_mae_values = [row["mean_mae"] for row in rows]
    cv_r2_values = [row["cv_r2_mean"] for row in rows if row["cv_r2_mean"] is not None]
    lexical_fpr_values = [row["lexical_fpr"] for row in rows]

    print(json.dumps({
        "model": args.model,
        "layer": args.layer,
        "channels": len(channels),
        "mean_r2": round(float(np.mean(mean_r2_values)), 4) if mean_r2_values else None,
        "mean_mae": round(float(np.mean(mean_mae_values)), 4) if mean_mae_values else None,
        "cv_r2_mean": round(float(np.mean(cv_r2_values)), 4) if cv_r2_values else None,
        "lexical_fpr_mean": round(float(np.mean(lexical_fpr_values)), 4) if lexical_fpr_values else None,
        "out_json": str(args.out_json),
        "out_csv": str(args.out_csv),
    }, indent=2))


if __name__ == "__main__":
    main()
