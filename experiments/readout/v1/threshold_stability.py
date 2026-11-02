"""Compare gate thresholds and F1 across quantization backends.

This is a model-independent diagnostic: it reads existing gate JSON files and
reports per-channel threshold shifts, F1 changes, and the best layer for each
backend. It does not recalibrate anything.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def fmt(value: float | None, digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def best_layer_for_channel(gate_metrics: dict[str, dict[str, object]], channel: str) -> int:
    """Return the layer with the highest held-out F1 for a channel."""
    return max(
        (int(layer) for layer in gate_metrics),
        key=lambda layer: gate_metrics[str(layer)][channel]["test"]["f1"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare gate threshold stability across backends")
    parser.add_argument("--base", type=Path, default=Path("runs/gates-base.json"))
    parser.add_argument("--eight-bit", type=Path, default=Path("runs/gates-base-8bit.json"))
    parser.add_argument("--q6", type=Path, default=Path("runs/gates-base-q6-dequantized.json"))
    parser.add_argument("--out-json", type=Path, default=Path("runs/threshold-stability.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("runs/threshold-stability.csv"))
    args = parser.parse_args()

    base = json.loads(args.base.read_text(encoding="utf-8"))
    eight = json.loads(args.eight_bit.read_text(encoding="utf-8"))
    q6 = json.loads(args.q6.read_text(encoding="utf-8"))

    base_metrics = base["gate_metrics"]
    eight_metrics = eight["gate_metrics"]
    q6_metrics = q6["gate_metrics"]
    channels = sorted(base_metrics[str(base["layers"][0])])

    rows = []
    for channel in channels:
        base_layer = best_layer_for_channel(base_metrics, channel)
        eight_layer = best_layer_for_channel(eight_metrics, channel)
        q6_layer = best_layer_for_channel(q6_metrics, channel)

        base_gate = base_metrics[str(base_layer)][channel]
        eight_gate = eight_metrics[str(eight_layer)][channel]
        q6_gate = q6_metrics[str(q6_layer)][channel]

        rows.append({
            "channel": channel,
            "base_layer": base_layer,
            "base_tau": base_gate["tau"],
            "base_f1": base_gate["test"]["f1"],
            "eight_layer": eight_layer,
            "eight_tau": eight_gate["tau"],
            "eight_f1": eight_gate["test"]["f1"],
            "q6_layer": q6_layer,
            "q6_tau": q6_gate["tau"],
            "q6_f1": q6_gate["test"]["f1"],
            "tau_delta_8bit": eight_gate["tau"] - base_gate["tau"],
            "tau_delta_q6": q6_gate["tau"] - base_gate["tau"],
            "f1_delta_8bit": eight_gate["test"]["f1"] - base_gate["test"]["f1"],
            "f1_delta_q6": q6_gate["test"]["f1"] - base_gate["test"]["f1"],
        })

    mean_abs_tau_8bit = sum(abs(row["tau_delta_8bit"]) for row in rows) / len(rows)
    mean_abs_tau_q6 = sum(abs(row["tau_delta_q6"]) for row in rows) / len(rows)
    mean_f1_8bit = sum(row["f1_delta_8bit"] for row in rows) / len(rows)
    mean_f1_q6 = sum(row["f1_delta_q6"] for row in rows) / len(rows)

    report = {
        "base": str(args.base),
        "eight_bit": str(args.eight_bit),
        "q6": str(args.q6),
        "channels": len(channels),
        "mean_abs_tau_delta_8bit": mean_abs_tau_8bit,
        "mean_abs_tau_delta_q6": mean_abs_tau_q6,
        "mean_f1_delta_8bit": mean_f1_8bit,
        "mean_f1_delta_q6": mean_f1_q6,
        "rows": rows,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({
        "channels": len(channels),
        "mean_abs_tau_delta_8bit": round(mean_abs_tau_8bit, 4),
        "mean_abs_tau_delta_q6": round(mean_abs_tau_q6, 4),
        "mean_f1_delta_8bit": round(mean_f1_8bit, 4),
        "mean_f1_delta_q6": round(mean_f1_q6, 4),
        "out_json": str(args.out_json),
        "out_csv": str(args.out_csv),
    }, indent=2))


if __name__ == "__main__":
    main()
