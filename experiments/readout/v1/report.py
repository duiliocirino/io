"""Build a compact HTML dashboard from readout sweep JSON.

The report is intentionally dependency-free: it uses inline CSS and SVG.
It shows layer trends, channel diagnostics, mixed-state errors, and an
optional Base-vs-Default comparison.
"""
from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from pathlib import Path


def heat_color(value: float | None) -> str:
    if value is None:
        return "#22262b"
    if value < 0.0:
        return "#4a2430"
    if value < 0.2:
        return "#2b2f33"
    if value < 0.4:
        return "#31483e"
    if value < 0.6:
        return "#356b5a"
    if value < 0.8:
        return "#3f8f6f"
    return "#6fbf8a"


def fmt(value: float | None, digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def svg_trend(layers: list[int], values: list[float], width: int = 900, height: int = 260) -> str:
    if not values:
        return ""
    low = min(values)
    high = max(values)
    span = high - low or 0.01
    pad = 0.04 * span
    low -= pad
    high += pad
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
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="Mean R2 by layer">
      <rect x="0" y="0" width="{width}" height="{height}" fill="#1b222a" rx="8"/>
      <line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#2b3540"/>
      <line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#2b3540"/>
      <polyline points="{path}" fill="none" stroke="#6fbf8a" stroke-width="3"/>
      {circles}
      {labels}
    </svg>
    """


def main() -> None:
    parser = argparse.ArgumentParser(description="Build readout HTML report")
    parser.add_argument("--json", type=Path, default=Path("runs/readout-base.json"))
    parser.add_argument("--compare", type=Path, default=None)
    parser.add_argument("--layer", type=int, default=None)
    parser.add_argument("--out", type=Path, default=Path("runs/readout-report.html"))
    args = parser.parse_args()

    data = json.loads(args.json.read_text(encoding="utf-8"))
    compare = json.loads(args.compare.read_text(encoding="utf-8")) if args.compare else None
    layers = data["layers"]
    layer_metrics = data["layer_metrics"]
    channels = sorted(layer_metrics[str(layers[0])]["channels"])

    best_layer = args.layer or max(layers, key=lambda l: layer_metrics[str(l)]["mean_r2"] or 0)
    best = layer_metrics[str(best_layer)]
    best_channels = best["channels"]

    strongest = sorted(best_channels.items(), key=lambda kv: kv[1]["r2"], reverse=True)[:5]
    weakest = sorted(best_channels.items(), key=lambda kv: kv[1]["r2"])[:5]

    perspective_spread = []
    for channel, metrics in best_channels.items():
        perspective_maes = [p["mae"] for p in metrics["perspective"].values()]
        if perspective_maes:
            perspective_spread.append((max(perspective_maes) - min(perspective_maes), channel))
    perspective_spread.sort(reverse=True)

    confusion = Counter()
    channel_errors = {}
    for channel, metrics in best_channels.items():
        errors = 0
        for row in metrics["confusion"]:
            confusion[(row["actual"], row["predicted"])] += row["count"]
            if row["actual"] != row["predicted"]:
                errors += row["count"]
        channel_errors[channel] = errors

    coarse_errors = sum(count for (actual, predicted), count in confusion.items() if actual != predicted)
    coarse_total = sum(confusion.values())
    coarse_rate = coarse_errors / coarse_total if coarse_total else None

    probe_pairs = []
    cosine = best["probe_cosine"]
    for a in sorted(cosine):
        for b in sorted(cosine[a]):
            if a < b:
                probe_pairs.append((cosine[a][b], a, b))
    probe_pairs.sort(reverse=True)

    centroid_channels = sorted(best["centroid_distance"].items(), key=lambda kv: kv[1])[:5]

    summary_rows = []
    for layer in layers:
        metrics = layer_metrics[str(layer)]
        summary_rows.append(
            "<tr>"
            f"<td>{layer}</td>"
            f"<td>{fmt(metrics['mean_r2'])}</td>"
            f"<td>{fmt(metrics['median_r2'])}</td>"
            f"<td>{fmt(metrics['mean_mae'])}</td>"
            f"<td>{fmt(metrics['mixed']['active_mae'])}</td>"
            f"<td>{fmt(metrics['mixed']['absent_mae'])}</td>"
            "</tr>"
        )

    heat_rows = []
    for channel in channels:
        cells = []
        for layer in layers:
            value = layer_metrics[str(layer)]["channels"].get(channel, {}).get("r2")
            cells.append(f"<td style=\"background:{heat_color(value)}\">{fmt(value)}</td>")
        heat_rows.append(f"<tr><th>{html.escape(channel)}</th>{''.join(cells)}</tr>")

    channel_rows = []
    for channel in channels:
        metrics = best_channels.get(channel, {})
        worst_perspective = max(
            metrics.get("perspective", {}).values(),
            key=lambda p: p["mae"],
            default=None,
        )
        channel_rows.append(
            "<tr>"
            f"<td>{html.escape(channel)}</td>"
            f"<td>{fmt(metrics.get('r2'))}</td>"
            f"<td>{fmt(metrics.get('mae'))}</td>"
            f"<td>{fmt(worst_perspective['mae'] if worst_perspective else None)}</td>"
            f"<td>{channel_errors.get(channel, 0)}</td>"
            "</tr>"
        )

    confusion_rows = []
    for actual in [0.0, 0.5, 1.0]:
        cells = []
        for predicted in [0.0, 0.5, 1.0]:
            cells.append(f"<td>{confusion.get((actual, predicted), 0)}</td>")
        confusion_rows.append(f"<tr><th>{actual}</th>{''.join(cells)}</tr>")

    mixed_rows = []
    for layer in layers:
        metrics = layer_metrics[str(layer)]["mixed"]
        mixed_rows.append(
            f"<tr><td>{layer}</td><td>{fmt(metrics['active_mae'])}</td><td>{fmt(metrics['absent_mae'])}</td></tr>"
        )

    comparison_rows = []
    channel_delta_rows = []
    if compare:
        for layer in layers:
            b = layer_metrics[str(layer)]
            d = compare["layer_metrics"][str(layer)]
            comparison_rows.append(
                "<tr>"
                f"<td>{layer}</td>"
                f"<td>{fmt(b['mean_r2'])}</td>"
                f"<td>{fmt(d['mean_r2'])}</td>"
                f"<td>{fmt(d['mean_r2'] - b['mean_r2'])}</td>"
                f"<td>{fmt(b['mixed']['absent_mae'])}</td>"
                f"<td>{fmt(d['mixed']['absent_mae'])}</td>"
                "</tr>"
            )
        b = layer_metrics[str(best_layer)]["channels"]
        d = compare["layer_metrics"][str(best_layer)]["channels"]
        deltas = sorted(
            ((d[c]["r2"] - b[c]["r2"], c, b[c]["r2"], d[c]["r2"]) for c in b),
            reverse=True,
        )
        for delta, channel, br2, dr2 in deltas:
            channel_delta_rows.append(
                f"<tr><td>{html.escape(channel)}</td><td>{fmt(br2)}</td><td>{fmt(dr2)}</td><td>{fmt(delta)}</td></tr>"
            )

    strongest_rows = "".join(
        f"<tr><td>{html.escape(c)}</td><td>{fmt(v['r2'])}</td></tr>" for c, v in strongest
    )
    weakest_rows = "".join(
        f"<tr><td>{html.escape(c)}</td><td>{fmt(v['r2'])}</td></tr>" for c, v in weakest
    )
    perspective_rows = "".join(
        f"<tr><td>{html.escape(c)}</td><td>{fmt(spread)}</td></tr>" for spread, c in perspective_spread[:5]
    )
    probe_rows = "".join(
        f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{fmt(value)}</td></tr>"
        for value, a, b in probe_pairs[:5]
    )
    centroid_rows = "".join(
        f"<tr><td>{html.escape(channel)}</td><td>{fmt(value)}</td></tr>"
        for channel, value in centroid_channels
    )

    trend = svg_trend(layers, [layer_metrics[str(l)]["mean_r2"] or 0 for l in layers])

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Qwen 3.5 readout sweep</title>
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
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
  </style>
</head>
<body>
<main>
  <h1>Qwen 3.5 readout sweep</h1>
  <p>Model: <strong>{html.escape(str(data['model']))}</strong> · dtype: {html.escape(str(data['dtype']))} · rows: {data['rows']} · mixed rows: {data['mixed_rows']}</p>

  <div class="cards">
    <div class="card"><span>Layers</span><strong>{layers[0]}–{layers[-1]}</strong></div>
    <div class="card"><span>Best mean R² layer</span><strong>{best_layer}</strong></div>
    <div class="card"><span>Mean R² at best layer</span><strong>{fmt(best['mean_r2'])}</strong></div>
    <div class="card"><span>Mixed active MAE</span><strong>{fmt(best['mixed']['active_mae'])}</strong></div>
    <div class="card"><span>Mixed absent MAE</span><strong>{fmt(best['mixed']['absent_mae'])}</strong></div>
    <div class="card"><span>Coarse error rate</span><strong>{fmt(coarse_rate)}</strong></div>
  </div>

  <h2>Layer trend</h2>
  <p class="note">Mean held-out R² by text-decoder layer. Early layers are strong; later layers weaken.</p>
  {trend}

  <h2>Key diagnostics at layer {best_layer}</h2>
  <div class="grid">
    <div>
      <h2>Strongest channels</h2>
      <table><thead><tr><th>Channel</th><th>R²</th></tr></thead><tbody>{strongest_rows}</tbody></table>
    </div>
    <div>
      <h2>Weakest channels</h2>
      <table><thead><tr><th>Channel</th><th>R²</th></tr></thead><tbody>{weakest_rows}</tbody></table>
    </div>
  </div>

  <h2>Perspective sensitivity</h2>
  <p class="note">Largest spread between perspective-specific MAE values at layer {best_layer}.</p>
  <table><thead><tr><th>Channel</th><th>MAE spread</th></tr></thead><tbody>{perspective_rows}</tbody></table>

  <h2>Channel table at layer {best_layer}</h2>
  <table>
    <thead><tr><th>Channel</th><th>R²</th><th>MAE</th><th>Worst perspective MAE</th><th>Coarse errors</th></tr></thead>
    <tbody>{''.join(channel_rows)}</tbody>
  </table>

  <h2>Aggregate coarse confusion at layer {best_layer}</h2>
  <table>
    <thead><tr><th>Actual</th><th>Predicted 0.0</th><th>Predicted 0.5</th><th>Predicted 1.0</th></tr></thead>
    <tbody>{''.join(confusion_rows)}</tbody>
  </table>

  <h2>Channel × layer R² heatmap</h2>
  <table class="heat">
    <thead><tr><th>Channel</th>{''.join(f'<th>{layer}</th>' for layer in layers)}</tr></thead>
    <tbody>{''.join(heat_rows)}</tbody>
  </table>

  <h2>Confusable channel pairs</h2>
  <div class="grid">
    <div>
      <h2>Highest probe cosine</h2>
      <table><thead><tr><th>A</th><th>B</th><th>Cosine</th></tr></thead><tbody>{probe_rows}</tbody></table>
    </div>
    <div>
      <h2>Smallest high-vs-low centroid distance</h2>
      <table><thead><tr><th>Channel</th><th>Distance</th></tr></thead><tbody>{centroid_rows}</tbody></table>
    </div>
  </div>

  <h2>Mixed-state validation</h2>
  <table>
    <thead><tr><th>Layer</th><th>Active MAE</th><th>Absent MAE</th></tr></thead>
    <tbody>{''.join(mixed_rows)}</tbody>
  </table>

  <h2>Layer summary</h2>
  <table>
    <thead><tr><th>Layer</th><th>Mean R²</th><th>Median R²</th><th>Mean MAE</th><th>Mixed active MAE</th><th>Mixed absent MAE</th></tr></thead>
    <tbody>{''.join(summary_rows)}</tbody>
  </table>

  {f'''
  <h2>Base vs Default comparison</h2>
  <table>
    <thead><tr><th>Layer</th><th>Base mean R²</th><th>Default mean R²</th><th>Delta</th><th>Base mixed absent MAE</th><th>Default mixed absent MAE</th></tr></thead>
    <tbody>{''.join(comparison_rows)}</tbody>
  </table>
  <h2>Channel deltas at layer {best_layer}</h2>
  <table>
    <thead><tr><th>Channel</th><th>Base R²</th><th>Default R²</th><th>Delta</th></tr></thead>
    <tbody>{''.join(channel_delta_rows)}</tbody>
  </table>
  ''' if compare else ''}
</main>
</body>
</html>
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(document, encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
