"""Build a compact HTML dashboard from gate-calibration JSON."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def fmt(value: float | None, digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def f1_color(value: float | None) -> str:
    if value is None:
        return "#22262b"
    if value < 0.3:
        return "#4a2430"
    if value < 0.5:
        return "#3a2f2f"
    if value < 0.7:
        return "#356b5a"
    if value < 0.85:
        return "#3f8f6f"
    return "#6fbf8a"


def tau_color(value: float | None) -> str:
    if value is None:
        return "#22262b"
    if value < 0.4:
        return "#2b4b5a"
    if value < 0.55:
        return "#356b7a"
    if value < 0.7:
        return "#4f8f9f"
    return "#8fbfcf"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build gate HTML report")
    parser.add_argument("--json", type=Path, default=Path("runs/gates-base.json"))
    parser.add_argument("--compare", type=Path, default=None)
    parser.add_argument("--layer", type=int, default=None)
    parser.add_argument("--out", type=Path, default=Path("runs/gates-report.html"))
    args = parser.parse_args()

    data = json.loads(args.json.read_text(encoding="utf-8"))
    compare = json.loads(args.compare.read_text(encoding="utf-8")) if args.compare else None
    layers = data["layers"]
    metrics = data["gate_metrics"]
    channels = sorted(metrics[str(layers[0])])

    best_layer = args.layer or max(
        layers,
        key=lambda layer: sum(v["test"]["f1"] for v in metrics[str(layer)].values()) / len(metrics[str(layer)]),
    )
    best = metrics[str(best_layer)]

    mean_f1 = sum(v["test"]["f1"] for v in best.values()) / len(best)
    mean_fpr = sum(v["test"]["fpr"] for v in best.values()) / len(best)
    mean_recall = sum(v["test"]["recall"] for v in best.values()) / len(best)
    mean_active_mae = sum(v["active_mae"] for v in best.values() if v["active_mae"] is not None) / len(best)
    mean_absent_mae = sum(v["absent_mae"] for v in best.values() if v["absent_mae"] is not None) / len(best)

    layer_rows = []
    for layer in layers:
        vals = metrics[str(layer)].values()
        layer_rows.append(
            "<tr>"
            f"<td>{layer}</td>"
            f"<td>{fmt(sum(v['test']['f1'] for v in vals) / len(vals))}</td>"
            f"<td>{fmt(sum(v['test']['fpr'] for v in vals) / len(vals))}</td>"
            f"<td>{fmt(sum(v['test']['recall'] for v in vals) / len(vals))}</td>"
            f"<td>{fmt(sum(v['active_mae'] for v in vals if v['active_mae'] is not None) / len(vals))}</td>"
            f"<td>{fmt(sum(v['absent_mae'] for v in vals if v['absent_mae'] is not None) / len(vals))}</td>"
            "</tr>"
        )

    f1_rows = []
    tau_rows = []
    for channel in channels:
        f1_cells = []
        tau_cells = []
        for layer in layers:
            value = metrics[str(layer)].get(channel, {})
            f1_cells.append(f"<td style=\"background:{f1_color(value.get('test', {}).get('f1'))}\">{fmt(value.get('test', {}).get('f1'))}</td>")
            tau_cells.append(f"<td style=\"background:{tau_color(value.get('tau'))}\">{fmt(value.get('tau'))}</td>")
        f1_rows.append(f"<tr><th>{html.escape(channel)}</th>{''.join(f1_cells)}</tr>")
        tau_rows.append(f"<tr><th>{html.escape(channel)}</th>{''.join(tau_cells)}</tr>")

    selected_rows = []
    exceed_rows = []
    for channel in channels:
        v = best[channel]
        selected_rows.append(
            "<tr>"
            f"<td>{html.escape(channel)}</td>"
            f"<td>{fmt(v['tau'])}</td>"
            f"<td>{fmt(v['youden_j'])}</td>"
            f"<td>{fmt(v['test']['fpr'])}</td>"
            f"<td>{fmt(v['test']['recall'])}</td>"
            f"<td>{fmt(v['test']['precision'])}</td>"
            f"<td>{fmt(v['test']['f1'])}</td>"
            f"<td>{fmt(v['active_mae'])}</td>"
            f"<td>{fmt(v['absent_mae'])}</td>"
            "</tr>"
        )
        if v["test"]["fpr"] > data["fpr_cap"]:
            exceed_rows.append(
                f"<tr><td>{html.escape(channel)}</td><td>{fmt(v['test']['fpr'])}</td></tr>"
            )

    comparison_html = ""
    if compare:
        comparison_rows = []
        for layer in layers:
            b = metrics[str(layer)]
            d = compare["gate_metrics"][str(layer)]
            bf = sum(v["test"]["f1"] for v in b.values()) / len(b)
            df = sum(v["test"]["f1"] for v in d.values()) / len(d)
            bfp = sum(v["test"]["fpr"] for v in b.values()) / len(b)
            dfp = sum(v["test"]["fpr"] for v in d.values()) / len(d)
            bmae = sum(v["active_mae"] for v in b.values() if v["active_mae"] is not None) / len(b)
            dmae = sum(v["active_mae"] for v in d.values() if v["active_mae"] is not None) / len(d)
            comparison_rows.append(
                "<tr>"
                f"<td>{layer}</td>"
                f"<td>{fmt(bf)}</td>"
                f"<td>{fmt(df)}</td>"
                f"<td>{fmt(df - bf)}</td>"
                f"<td>{fmt(bfp)}</td>"
                f"<td>{fmt(dfp)}</td>"
                f"<td>{fmt(bmae)}</td>"
                f"<td>{fmt(dmae)}</td>"
                "</tr>"
            )

        channel_delta_rows = []
        b = metrics[str(best_layer)]
        d = compare["gate_metrics"][str(best_layer)]
        deltas = sorted(
            ((d[c]["test"]["f1"] - b[c]["test"]["f1"], c, b[c]["test"]["f1"], d[c]["test"]["f1"]) for c in b),
            reverse=True,
        )
        for delta, channel, bf1, df1 in deltas:
            channel_delta_rows.append(
                f"<tr><td>{html.escape(channel)}</td><td>{fmt(bf1)}</td><td>{fmt(df1)}</td><td>{fmt(delta)}</td></tr>"
            )

        comparison_html = f"""
  <h2>Base vs Default gate comparison</h2>
  <table>
    <thead><tr><th>Layer</th><th>Base F1</th><th>Default F1</th><th>Delta</th><th>Base FPR</th><th>Default FPR</th><th>Base active MAE</th><th>Default active MAE</th></tr></thead>
    <tbody>{''.join(comparison_rows)}</tbody>
  </table>
  <h2>Channel F1 deltas at layer {best_layer}</h2>
  <table>
    <thead><tr><th>Channel</th><th>Base F1</th><th>Default F1</th><th>Delta</th></tr></thead>
    <tbody>{''.join(channel_delta_rows)}</tbody>
  </table>
  """

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Qwen 3.5 gate calibration</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      background: #14181d;
      color: #e6edf3;
      line-height: 1.5;
    }}
    main {{ max-width: 1150px; margin: 0 auto; padding: 28px 20px 48px; }}
    h1 {{ font-size: 1.7rem; margin: 0 0 6px; }}
    h2 {{ font-size: 1.15rem; margin: 28px 0 10px; color: #9ec5d8; }}
    p {{ color: #aab6c2; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 18px 0; }}
    .card {{ background: #1b222a; border: 1px solid #2b3540; border-radius: 10px; padding: 12px 14px; }}
    .card strong {{ display: block; font-size: 1.2rem; }}
    table {{ width: 100%; border-collapse: collapse; background: #1b222a; border-radius: 8px; overflow: hidden; margin-bottom: 16px; }}
    th, td {{ padding: 8px 10px; border-bottom: 1px solid #2b3540; text-align: left; }}
    th {{ color: #9ec5d8; font-weight: 600; }}
    td {{ color: #e6edf3; }}
    .heat td {{ text-align: center; font-variant-numeric: tabular-nums; }}
    .heat th {{ position: sticky; left: 0; background: #1b222a; }}
    .note {{ color: #aab6c2; font-size: 0.92rem; }}
  </style>
</head>
<body>
<main>
  <h1>Qwen 3.5 gate calibration</h1>
  <p>Model: <strong>{html.escape(str(data['model']))}</strong> · dtype: {html.escape(str(data['dtype']))} · FPR cap: {data['fpr_cap']}</p>

  <div class="cards">
    <div class="card"><span>Layers</span><strong>{layers[0]}–{layers[-1]}</strong></div>
    <div class="card"><span>Best F1 layer</span><strong>{best_layer}</strong></div>
    <div class="card"><span>Mean F1</span><strong>{fmt(mean_f1)}</strong></div>
    <div class="card"><span>Mean FPR</span><strong>{fmt(mean_fpr)}</strong></div>
    <div class="card"><span>Mean recall</span><strong>{fmt(mean_recall)}</strong></div>
    <div class="card"><span>Active MAE</span><strong>{fmt(mean_active_mae)}</strong></div>
    <div class="card"><span>Absent MAE</span><strong>{fmt(mean_absent_mae)}</strong></div>
  </div>

  <h2>Layer summary</h2>
  <table>
    <thead><tr><th>Layer</th><th>Mean F1</th><th>Mean FPR</th><th>Mean recall</th><th>Active MAE</th><th>Absent MAE</th></tr></thead>
    <tbody>{''.join(layer_rows)}</tbody>
  </table>

  <h2>Channel × layer F1 heatmap</h2>
  <p class="note">Green is stronger binary detection. F1 is computed on held-out mixed/negative rows.</p>
  <table class="heat">
    <thead><tr><th>Channel</th>{''.join(f'<th>{layer}</th>' for layer in layers)}</tr></thead>
    <tbody>{''.join(f1_rows)}</tbody>
  </table>

  <h2>Channel × layer threshold heatmap</h2>
  <p class="note">Higher τ means a stricter gate; it reduces false positives but can compress continuous intensity.</p>
  <table class="heat">
    <thead><tr><th>Channel</th>{''.join(f'<th>{layer}</th>' for layer in layers)}</tr></thead>
    <tbody>{''.join(tau_rows)}</tbody>
  </table>

  <h2>Gate metrics at layer {best_layer}</h2>
  <table>
    <thead><tr><th>Channel</th><th>τ</th><th>Youden J</th><th>Test FPR</th><th>Recall</th><th>Precision</th><th>F1</th><th>Active MAE</th><th>Absent MAE</th></tr></thead>
    <tbody>{''.join(selected_rows)}</tbody>
  </table>

  <h2>Test FPR above cap</h2>
  <p class="note">These channels exceed the 5% FPR cap on the held-out set; do not tune on test, but treat them as transfer warnings.</p>
  <table>
    <thead><tr><th>Channel</th><th>Test FPR</th></tr></thead>
    <tbody>{''.join(exceed_rows)}</tbody>
  </table>

  {comparison_html}

  <h2>Interpretation</h2>
  <p class="note">The gate removes absent-channel false positives, but the shifted deadzone compresses active intensity. Binary detection is promising; continuous readout needs a separate intensity calibration.</p>
</main>
</body>
</html>
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(document, encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
