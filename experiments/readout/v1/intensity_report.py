"""Build a compact HTML dashboard from intensity-calibration JSON."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def fmt(value: float | None, digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def mae_color(value: float | None) -> str:
    if value is None:
        return "#22262b"
    if value < 0.2:
        return "#6fbf8a"
    if value < 0.3:
        return "#3f8f6f"
    if value < 0.45:
        return "#356b5a"
    if value < 0.6:
        return "#4a2430"
    return "#6a3038"


def svg_trend(layers: list[int], values: list[float], width: int = 900, height: int = 260) -> str:
    if not values:
        return ""
    low = min(values)
    high = max(values)
    span = high - low or 0.01
    low -= 0.04 * span
    high += 0.04 * span
    left, right, top, bottom = 50, width - 20, 20, height - 35
    points = []
    for layer, value in zip(layers, values):
        x = left + (layer - layers[0]) / (layers[-1] - layers[0]) * (right - left)
        y = bottom - (value - low) / (high - low) * (bottom - top)
        points.append((x, y))
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    circles = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#6fbf8a"/>' for x, y in points)
    labels = "".join(
        f'<text x="{left + (layer - layers[0]) / (layers[-1] - layers[0]) * (right - left):.1f}" y="{height - 10}" text-anchor="middle" fill="#9ec5d8" font-size="12">{layer}</text>'
        for layer in layers
    )
    return f"""
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="Mean active MAE by layer">
      <rect x="0" y="0" width="{width}" height="{height}" fill="#1b222a" rx="8"/>
      <line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#2b3540"/>
      <line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#2b3540"/>
      <polyline points="{path}" fill="none" stroke="#6fbf8a" stroke-width="3"/>
      {circles}
      {labels}
    </svg>
    """


def main() -> None:
    parser = argparse.ArgumentParser(description="Build intensity HTML report")
    parser.add_argument("--json", type=Path, default=Path("runs/intensity-base.json"))
    parser.add_argument("--compare", type=Path, default=None)
    parser.add_argument("--layer", type=int, default=None)
    parser.add_argument("--out", type=Path, default=Path("runs/intensity-report.html"))
    args = parser.parse_args()

    data = json.loads(args.json.read_text(encoding="utf-8"))
    compare = json.loads(args.compare.read_text(encoding="utf-8")) if args.compare else None
    layers = data["layers"]
    metrics = data["intensity_metrics"]
    channels = sorted(metrics[str(layers[0])])

    best_layer = args.layer or min(
        layers,
        key=lambda layer: sum(v["active_mae"] for v in metrics[str(layer)].values() if v["active_mae"] is not None)
        / len(metrics[str(layer)]),
    )
    best = metrics[str(best_layer)]

    mean_active = sum(v["active_mae"] for v in best.values() if v["active_mae"] is not None) / len(best)
    mean_absent = sum(v["absent_mae"] for v in best.values() if v["absent_mae"] is not None) / len(best)
    mean_recall = sum(v["gate_recall"] for v in best.values() if v["gate_recall"] is not None) / len(best)
    mean_fpr = sum(v["gate_fpr"] for v in best.values() if v["gate_fpr"] is not None) / len(best)
    mean_deadzone = sum(v["deadzone_active_mae"] for v in best.values() if v["deadzone_active_mae"] is not None) / len(best)
    mean_improvement = mean_deadzone - mean_active

    layer_rows = []
    for layer in layers:
        vals = metrics[str(layer)].values()
        layer_rows.append(
            "<tr>"
            f"<td>{layer}</td>"
            f"<td>{fmt(sum(v['active_mae'] for v in vals if v['active_mae'] is not None) / len(vals))}</td>"
            f"<td>{fmt(sum(v['absent_mae'] for v in vals if v['absent_mae'] is not None) / len(vals))}</td>"
            f"<td>{fmt(sum(v['gate_recall'] for v in vals if v['gate_recall'] is not None) / len(vals))}</td>"
            f"<td>{fmt(sum(v['gate_fpr'] for v in vals if v['gate_fpr'] is not None) / len(vals))}</td>"
            f"<td>{fmt(sum(v['deadzone_active_mae'] for v in vals if v['deadzone_active_mae'] is not None) / len(vals))}</td>"
            "</tr>"
        )

    heat_rows = []
    for channel in channels:
        cells = []
        for layer in layers:
            value = metrics[str(layer)].get(channel, {}).get("active_mae")
            cells.append(f"<td style=\"background:{mae_color(value)}\">{fmt(value)}</td>")
        heat_rows.append(f"<tr><th>{html.escape(channel)}</th>{''.join(cells)}</tr>")

    selected_rows = []
    negative_slopes = []
    for channel in channels:
        v = best[channel]
        improvement = v["deadzone_active_mae"] - v["active_mae"] if v["deadzone_active_mae"] is not None and v["active_mae"] is not None else None
        selected_rows.append(
            "<tr>"
            f"<td>{html.escape(channel)}</td>"
            f"<td>{fmt(v['tau'])}</td>"
            f"<td>{fmt(v['slope'])}</td>"
            f"<td>{fmt(v['intercept'])}</td>"
            f"<td>{fmt(v['active_mae'])}</td>"
            f"<td>{fmt(v['absent_mae'])}</td>"
            f"<td>{fmt(v['gate_recall'])}</td>"
            f"<td>{fmt(v['gate_fpr'])}</td>"
            f"<td>{fmt(v['deadzone_active_mae'])}</td>"
            f"<td>{fmt(improvement)}</td>"
            "</tr>"
        )
        if v["slope"] < 0:
            negative_slopes.append(
                f"<tr><td>{html.escape(channel)}</td><td>{fmt(v['slope'])}</td><td>{fmt(v['active_mae'])}</td></tr>"
            )

    top_channels = sorted(
        ((v["active_mae"], c) for c, v in best.items() if v["active_mae"] is not None)
    )[:8]
    bottom_channels = sorted(
        ((v["active_mae"], c) for c, v in best.items() if v["active_mae"] is not None),
        reverse=True,
    )[:8]

    top_rows = "".join(f"<tr><td>{html.escape(c)}</td><td>{fmt(v)}</td></tr>" for v, c in top_channels)
    bottom_rows = "".join(f"<tr><td>{html.escape(c)}</td><td>{fmt(v)}</td></tr>" for v, c in bottom_channels)

    comparison_html = ""
    if compare:
        comparison_rows = []
        for layer in layers:
            b = metrics[str(layer)]
            d = compare["intensity_metrics"][str(layer)]
            bmae = sum(v["active_mae"] for v in b.values() if v["active_mae"] is not None) / len(b)
            dmae = sum(v["active_mae"] for v in d.values() if v["active_mae"] is not None) / len(d)
            babs = sum(v["absent_mae"] for v in b.values() if v["absent_mae"] is not None) / len(b)
            dabs = sum(v["absent_mae"] for v in d.values() if v["absent_mae"] is not None) / len(d)
            comparison_rows.append(
                "<tr>"
                f"<td>{layer}</td>"
                f"<td>{fmt(bmae)}</td>"
                f"<td>{fmt(dmae)}</td>"
                f"<td>{fmt(dmae - bmae)}</td>"
                f"<td>{fmt(babs)}</td>"
                f"<td>{fmt(dabs)}</td>"
                "</tr>"
            )

        channel_delta_rows = []
        b = metrics[str(best_layer)]
        d = compare["intensity_metrics"][str(best_layer)]
        deltas = sorted(
            ((d[c]["active_mae"] - b[c]["active_mae"], c, b[c]["active_mae"], d[c]["active_mae"]) for c in b),
            reverse=True,
        )
        for delta, channel, bmae, dmae in deltas:
            channel_delta_rows.append(
                f"<tr><td>{html.escape(channel)}</td><td>{fmt(bmae)}</td><td>{fmt(dmae)}</td><td>{fmt(delta)}</td></tr>"
            )

        comparison_html = f"""
  <h2>Base vs Default intensity comparison</h2>
  <table>
    <thead><tr><th>Layer</th><th>Base active MAE</th><th>Default active MAE</th><th>Delta</th><th>Base absent MAE</th><th>Default absent MAE</th></tr></thead>
    <tbody>{''.join(comparison_rows)}</tbody>
  </table>
  <h2>Channel active-MAE deltas at layer {best_layer}</h2>
  <table>
    <thead><tr><th>Channel</th><th>Base active MAE</th><th>Default active MAE</th><th>Delta</th></tr></thead>
    <tbody>{''.join(channel_delta_rows)}</tbody>
  </table>
  """

    trend = svg_trend(layers, [
        sum(v["active_mae"] for v in metrics[str(layer)].values() if v["active_mae"] is not None)
        / len(metrics[str(layer)])
        for layer in layers
    ])

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Qwen 3.5 intensity calibration</title>
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
  <h1>Qwen 3.5 intensity calibration</h1>
  <p>Model: <strong>{html.escape(str(data['model']))}</strong> · dtype: {html.escape(str(data['dtype']))} · gates: {html.escape(str(data['gates']))}</p>

  <div class="cards">
    <div class="card"><span>Layers</span><strong>{layers[0]}–{layers[-1]}</strong></div>
    <div class="card"><span>Best active MAE layer</span><strong>{best_layer}</strong></div>
    <div class="card"><span>Mean active MAE</span><strong>{fmt(mean_active)}</strong></div>
    <div class="card"><span>Mean absent MAE</span><strong>{fmt(mean_absent)}</strong></div>
    <div class="card"><span>Mean gate recall</span><strong>{fmt(mean_recall)}</strong></div>
    <div class="card"><span>Mean gate FPR</span><strong>{fmt(mean_fpr)}</strong></div>
    <div class="card"><span>Improvement over deadzone</span><strong>{fmt(mean_improvement)}</strong></div>
  </div>

  <h2>Active MAE trend</h2>
  <p class="note">Lower is better. The separate linear calibration preserves intensity better than the gate deadzone.</p>
  {trend}

  <h2>Layer summary</h2>
  <table>
    <thead><tr><th>Layer</th><th>Mean active MAE</th><th>Mean absent MAE</th><th>Mean gate recall</th><th>Mean gate FPR</th><th>Mean deadzone active MAE</th></tr></thead>
    <tbody>{''.join(layer_rows)}</tbody>
  </table>

  <h2>Channel × layer active-MAE heatmap</h2>
  <table class="heat">
    <thead><tr><th>Channel</th>{''.join(f'<th>{layer}</th>' for layer in layers)}</tr></thead>
    <tbody>{''.join(heat_rows)}</tbody>
  </table>

  <h2>Intensity metrics at layer {best_layer}</h2>
  <table>
    <thead><tr><th>Channel</th><th>τ</th><th>Slope</th><th>Intercept</th><th>Active MAE</th><th>Absent MAE</th><th>Gate recall</th><th>Gate FPR</th><th>Deadzone active MAE</th><th>Improvement</th></tr></thead>
    <tbody>{''.join(selected_rows)}</tbody>
  </table>

  <div>
    <h2>Best active MAE channels</h2>
    <table><thead><tr><th>Channel</th><th>Active MAE</th></tr></thead><tbody>{top_rows}</tbody></table>
  </div>
  <div>
    <h2>Worst active MAE channels</h2>
    <table><thead><tr><th>Channel</th><th>Active MAE</th></tr></thead><tbody>{bottom_rows}</tbody></table>
  </div>

  <h2>Negative-slope warnings</h2>
  <p class="note">A negative slope means the linear fit is unstable; use constrained or isotonic calibration for those channels.</p>
  <table>
    <thead><tr><th>Channel</th><th>Slope</th><th>Active MAE</th></tr></thead>
    <tbody>{''.join(negative_slopes)}</tbody>
  </table>

  {comparison_html}

  <h2>Interpretation</h2>
  <p class="note">The separate intensity mapping improves active MAE substantially, but some channels still have high error and unstable slopes. The gate remains useful for binary activation; intensity calibration needs a constrained monotone fit for production.</p>
</main>
</body>
</html>
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(document, encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
