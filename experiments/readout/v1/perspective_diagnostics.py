"""Compare perspective-stratified readout errors across quantization backends.

This is a model-independent diagnostic: it reads existing readout JSON files and
reports the worst perspective and MAE spread for each channel at the backend's
best readout layer.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def fmt(value: float | None, digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def best_read_layer(layer_metrics: dict[str, dict[str, object]]) -> int:
    return max(
        (int(layer) for layer in layer_metrics),
        key=lambda layer: layer_metrics[str(layer)]["mean_r2"] or 0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare perspective sensitivity across backends")
    parser.add_argument("--base", type=Path, default=Path("runs/readout-base.json"))
    parser.add_argument("--eight-bit", type=Path, default=Path("runs/readout-base-8bit.json"))
    parser.add_argument("--q6", type=Path, default=Path("runs/readout-base-q6-dequantized.json"))
    parser.add_argument("--out-json", type=Path, default=Path("runs/perspective-diagnostics.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("runs/perspective-diagnostics.csv"))
    args = parser.parse_args()

    base = json.loads(args.base.read_text(encoding="utf-8"))
    eight = json.loads(args.eight_bit.read_text(encoding="utf-8"))
    q6 = json.loads(args.q6.read_text(encoding="utf-8"))

    base_lm = base["layer_metrics"]
    eight_lm = eight["layer_metrics"]
    q6_lm = q6["layer_metrics"]

    base_layer = best_read_layer(base_lm)
    eight_layer = best_read_layer(eight_lm)
    q6_layer = best_read_layer(q6_lm)

    channels = sorted(base_lm[str(base_layer)]["channels"])
    rows = []

    for channel in channels:
        base_channel = base_lm[str(base_layer)]["channels"][channel]
        eight_channel = eight_lm[str(eight_layer)]["channels"][channel]
        q6_channel = q6_lm[str(q6_layer)]["channels"][channel]

        def worst(metrics: dict[str, dict[str, object]]) -> tuple[str, float]:
            perspective = metrics.get("perspective", {})
            if not perspective:
                return "—", 0.0
            name = max(perspective, key=lambda key: perspective[key]["mae"])
            return name, perspective[name]["mae"]

        def spread(metrics: dict[str, dict[str, object]]) -> float:
            values = [item["mae"] for item in metrics.get("perspective", {}).values()]
            return max(values) - min(values) if values else 0.0

        base_worst_name, base_worst_mae = worst(base_channel)
        eight_worst_name, eight_worst_mae = worst(eight_channel)
        q6_worst_name, q6_worst_mae = worst(q6_channel)

        rows.append({
            "channel": channel,
            "base_layer": base_layer,
            "base_worst_perspective": base_worst_name,
            "base_worst_mae": base_worst_mae,
            "base_spread": spread(base_channel),
            "eight_layer": eight_layer,
            "eight_worst_perspective": eight_worst_name,
            "eight_worst_mae": eight_worst_mae,
            "eight_spread": spread(eight_channel),
            "q6_layer": q6_layer,
            "q6_worst_perspective": q6_worst_name,
            "q6_worst_mae": q6_worst_mae,
            "q6_spread": spread(q6_channel),
        })

    mean_spread_base = sum(row["base_spread"] for row in rows) / len(rows)
    mean_spread_eight = sum(row["eight_spread"] for row in rows) / len(rows)
    mean_spread_q6 = sum(row["q6_spread"] for row in rows) / len(rows)

    report = {
        "base": str(args.base),
        "eight_bit": str(args.eight_bit),
        "q6": str(args.q6),
        "base_layer": base_layer,
        "eight_layer": eight_layer,
        "q6_layer": q6_layer,
        "channels": len(channels),
        "mean_spread_base": mean_spread_base,
        "mean_spread_8bit": mean_spread_eight,
        "mean_spread_q6": mean_spread_q6,
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
        "base_layer": base_layer,
        "eight_layer": eight_layer,
        "q6_layer": q6_layer,
        "channels": len(channels),
        "mean_spread_base": round(mean_spread_base, 4),
        "mean_spread_8bit": round(mean_spread_eight, 4),
        "mean_spread_q6": round(mean_spread_q6, 4),
        "out_json": str(args.out_json),
        "out_csv": str(args.out_csv),
    }, indent=2))


if __name__ == "__main__":
    main()
