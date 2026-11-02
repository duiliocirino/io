"""Build a narrative HTML report from readout, gate, and intensity JSON.

The page uses the IO document template and the opt-in research/readout assets.
It is intentionally dependency-free and keeps the Q6 section as an explicit
placeholder until Q6 results exist.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def fmt(value: float | None, digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def mean(values: list[float | None]) -> float | None:
    clean = [value for value in values if value is not None]
    return sum(clean) / len(clean) if clean else None


def svg_line_chart(
    layers: list[int],
    series: list[tuple[str, list[float], str]],
    title: str,
    y_label: str,
    width: int = 900,
    height: int = 260,
) -> str:
    values = [value for _, points, _ in series for value in points]
    if not values:
        return ""
    low = min(values)
    high = max(values)
    span = high - low or 0.01
    pad = 0.06 * span
    low -= pad
    high += pad

    left, right, top, bottom = 62, width - 24, 24, height - 42

    def x(layer: int) -> float:
        return left + (layer - layers[0]) / (layers[-1] - layers[0]) * (right - left)

    def y(value: float) -> float:
        return bottom - (value - low) / (high - low) * (bottom - top)

    grid = []
    for i in range(5):
        value = low + (high - low) * i / 4
        yy = y(value)
        grid.append(
            f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="var(--io-rule)"/>'
            f'<text x="{left - 8}" y="{yy + 4:.1f}" text-anchor="end" fill="var(--io-ink-muted)" font-size="11">{value:.2f}</text>'
        )

    x_labels = "".join(
        f'<text x="{x(layer):.1f}" y="{height - 14}" text-anchor="middle" fill="var(--io-ink-muted)" font-size="11">{layer}</text>'
        for layer in layers
    )

    lines = []
    for label, points, color in series:
        path = " ".join(f"{x(layer):.1f},{y(value):.1f}" for layer, value in zip(layers, points))
        dots = "".join(
            f'<circle cx="{x(layer):.1f}" cy="{y(value):.1f}" r="3.2" fill="{color}"/>'
            for layer, value in zip(layers, points)
        )
        lines.append(
            f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2.6" stroke-linejoin="round"/>'
            f"{dots}"
        )

    return f"""
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">
      <rect x="0" y="0" width="{width}" height="{height}" fill="var(--io-paper-raised)" rx="8"/>
      {''.join(grid)}
      {''.join(lines)}
      {x_labels}
      <text x="{left}" y="{top - 6}" fill="var(--io-accent-deep)" font-size="12" font-weight="700">{html.escape(y_label)}</text>
    </svg>
    """


def heat_color(value: float | None) -> str:
    if value is None:
        return "#f1efe6"
    if value < 0.2:
        return "#f4dedd"
    if value < 0.4:
        return "#f8efe6"
    if value < 0.6:
        return "#e6f0df"
    if value < 0.8:
        return "#cfe6c6"
    return "#9ccf91"


def build_report(
    readout: Path,
    readout_8bit: Path,
    readout_q6: Path,
    gates: Path,
    gates_8bit: Path,
    gates_q6: Path,
    intensity: Path,
    intensity_8bit: Path,
    intensity_q6: Path,
    robustness: Path,
    constrained_intensity: Path,
    out: Path,
) -> None:
    base = json.loads(readout.read_text(encoding="utf-8"))
    q8 = json.loads(readout_8bit.read_text(encoding="utf-8"))
    q6 = json.loads(readout_q6.read_text(encoding="utf-8"))
    gate_base = json.loads(gates.read_text(encoding="utf-8"))
    gate_q8 = json.loads(gates_8bit.read_text(encoding="utf-8"))
    gate_q6 = json.loads(gates_q6.read_text(encoding="utf-8"))
    int_base = json.loads(intensity.read_text(encoding="utf-8"))
    int_q8 = json.loads(intensity_8bit.read_text(encoding="utf-8"))
    int_q6 = json.loads(intensity_q6.read_text(encoding="utf-8"))
    robust = json.loads(robustness.read_text(encoding="utf-8"))
    constrained = json.loads(constrained_intensity.read_text(encoding="utf-8"))

    layers = base["layers"]
    base_lm = base["layer_metrics"]
    q8_lm = q8["layer_metrics"]
    q6_lm = q6["layer_metrics"]

    best_read_layer = max(layers, key=lambda layer: base_lm[str(layer)]["mean_r2"] or 0)
    base_best = base_lm[str(best_read_layer)]
    q8_best = q8_lm[str(best_read_layer)]
    q6_best = q6_lm[str(best_read_layer)]

    base_r2 = [base_lm[str(layer)]["mean_r2"] or 0 for layer in layers]
    q8_r2 = [q8_lm[str(layer)]["mean_r2"] or 0 for layer in layers]
    q6_r2 = [q6_lm[str(layer)]["mean_r2"] or 0 for layer in layers]

    gate_layers = gate_base["layers"]
    gate_base_lm = gate_base["gate_metrics"]
    gate_q8_lm = gate_q8["gate_metrics"]
    gate_q6_lm = gate_q6["gate_metrics"]

    def gate_mean_f1(metrics: dict[str, dict[str, object]]) -> float:
        return mean([channel["test"]["f1"] for channel in metrics.values()]) or 0.0

    gate_base_f1 = [gate_mean_f1(gate_base_lm[str(layer)]) for layer in gate_layers]
    gate_q8_f1 = [gate_mean_f1(gate_q8_lm[str(layer)]) for layer in gate_layers]
    gate_q6_f1 = [gate_mean_f1(gate_q6_lm[str(layer)]) for layer in gate_layers]

    best_gate_base = max(gate_layers, key=lambda layer: gate_mean_f1(gate_base_lm[str(layer)]))
    best_gate_q8 = max(gate_layers, key=lambda layer: gate_mean_f1(gate_q8_lm[str(layer)]))
    best_gate_q6 = max(gate_layers, key=lambda layer: gate_mean_f1(gate_q6_lm[str(layer)]))

    int_layers = int_base["layers"]
    int_base_lm = int_base["intensity_metrics"]
    int_q8_lm = int_q8["intensity_metrics"]
    int_q6_lm = int_q6["intensity_metrics"]

    def intensity_mean_active(metrics: dict[str, dict[str, object]]) -> float:
        return mean([channel["active_mae"] for channel in metrics.values()]) or 0.0

    int_base_mae = [intensity_mean_active(int_base_lm[str(layer)]) for layer in int_layers]
    int_q8_mae = [intensity_mean_active(int_q8_lm[str(layer)]) for layer in int_layers]
    int_q6_mae = [intensity_mean_active(int_q6_lm[str(layer)]) for layer in int_layers]

    best_int_base = min(int_layers, key=lambda layer: intensity_mean_active(int_base_lm[str(layer)]))
    best_int_q8 = min(int_layers, key=lambda layer: intensity_mean_active(int_q8_lm[str(layer)]))
    best_int_q6 = min(int_layers, key=lambda layer: intensity_mean_active(int_q6_lm[str(layer)]))

    channels = sorted(base_best["channels"])
    strongest = sorted(base_best["channels"].items(), key=lambda item: item[1]["r2"], reverse=True)[:6]
    weakest = sorted(base_best["channels"].items(), key=lambda item: item[1]["r2"])[:6]

    channel_deltas = sorted(
        ((q8_best["channels"][channel]["r2"] - base_best["channels"][channel]["r2"], channel)
         for channel in channels),
        reverse=True,
    )
    improved = channel_deltas[:5]
    declined = channel_deltas[-5:]

    q6_channel_deltas = sorted(
        ((q6_best["channels"][channel]["r2"] - base_best["channels"][channel]["r2"], channel)
         for channel in channels),
        reverse=True,
    )
    q6_improved = q6_channel_deltas[:5]
    q6_declined = q6_channel_deltas[-5:]

    def coarse_rate_for(metrics: dict[str, dict[str, object]]) -> float | None:
        errors = 0
        total = 0
        for channel in metrics.values():
            for row in channel["confusion"]:
                total += row["count"]
                if row["actual"] != row["predicted"]:
                    errors += row["count"]
        return errors / total if total else None

    coarse_rate = coarse_rate_for(base_best["channels"])
    q6_coarse_rate = coarse_rate_for(q6_best["channels"])

    heat_rows = []
    for channel in channels:
        cells = []
        for layer in layers:
            value = base_lm[str(layer)]["channels"].get(channel, {}).get("r2")
            cells.append(
                f'<td style="background:{heat_color(value)}">{fmt(value)}</td>'
            )
        heat_rows.append(f"<tr><th>{html.escape(channel)}</th>{''.join(cells)}</tr>")

    strongest_rows = "".join(
        f"<tr><td>{html.escape(channel)}</td><td>{fmt(metrics['r2'])}</td></tr>"
        for channel, metrics in strongest
    )
    weakest_rows = "".join(
        f"<tr><td>{html.escape(channel)}</td><td>{fmt(metrics['r2'])}</td></tr>"
        for channel, metrics in weakest
    )

    delta_rows = []
    for delta, channel in improved + declined:
        cls = "delta-positive" if delta >= 0 else "delta-negative"
        delta_rows.append(
            f"<tr><td>{html.escape(channel)}</td><td>{fmt(base_best['channels'][channel]['r2'])}</td>"
            f"<td>{fmt(q8_best['channels'][channel]['r2'])}</td>"
            f"<td class=\"{cls}\">{fmt(delta)}</td></tr>"
        )

    q6_delta_rows = []
    for delta, channel in q6_improved + q6_declined:
        cls = "delta-positive" if delta >= 0 else "delta-negative"
        q6_delta_rows.append(
            f"<tr><td>{html.escape(channel)}</td><td>{fmt(base_best['channels'][channel]['r2'])}</td>"
            f"<td>{fmt(q6_best['channels'][channel]['r2'])}</td>"
            f"<td class=\"{cls}\">{fmt(delta)}</td></tr>"
        )

    def gate_summary(metrics: dict[str, dict[str, object]]) -> tuple[float, float, float, float, float]:
        return (
            mean([channel["test"]["f1"] for channel in metrics.values()]) or 0.0,
            mean([channel["test"]["fpr"] for channel in metrics.values()]) or 0.0,
            mean([channel["test"]["recall"] for channel in metrics.values()]) or 0.0,
            mean([channel["active_mae"] for channel in metrics.values()]) or 0.0,
            mean([channel["absent_mae"] for channel in metrics.values()]) or 0.0,
        )

    gate_base_summary = gate_summary(gate_base_lm[str(best_gate_base)])
    gate_q8_summary = gate_summary(gate_q8_lm[str(best_gate_q8)])
    gate_q6_summary = gate_summary(gate_q6_lm[str(best_gate_q6)])

    int_base_summary = (
        intensity_mean_active(int_base_lm[str(best_int_base)]),
        mean([channel["absent_mae"] for channel in int_base_lm[str(best_int_base)].values()]) or 0.0,
        mean([channel["gate_recall"] for channel in int_base_lm[str(best_int_base)].values()]) or 0.0,
        mean([channel["gate_fpr"] for channel in int_base_lm[str(best_int_base)].values()]) or 0.0,
        mean([channel["deadzone_active_mae"] for channel in int_base_lm[str(best_int_base)].values()]) or 0.0,
    )
    int_q8_summary = (
        intensity_mean_active(int_q8_lm[str(best_int_q8)]),
        mean([channel["absent_mae"] for channel in int_q8_lm[str(best_int_q8)].values()]) or 0.0,
        mean([channel["gate_recall"] for channel in int_q8_lm[str(best_int_q8)].values()]) or 0.0,
        mean([channel["gate_fpr"] for channel in int_q8_lm[str(best_int_q8)].values()]) or 0.0,
        mean([channel["deadzone_active_mae"] for channel in int_q8_lm[str(best_int_q8)].values()]) or 0.0,
    )
    int_q6_summary = (
        intensity_mean_active(int_q6_lm[str(best_int_q6)]),
        mean([channel["absent_mae"] for channel in int_q6_lm[str(best_int_q6)].values()]) or 0.0,
        mean([channel["gate_recall"] for channel in int_q6_lm[str(best_int_q6)].values()]) or 0.0,
        mean([channel["gate_fpr"] for channel in int_q6_lm[str(best_int_q6)].values()]) or 0.0,
        mean([channel["deadzone_active_mae"] for channel in int_q6_lm[str(best_int_q6)].values()]) or 0.0,
    )

    robust_rows = robust["rows"]
    robust_mean_r2 = mean([row["mean_r2"] for row in robust_rows]) or 0.0
    robust_mean_mae = mean([row["mean_mae"] for row in robust_rows]) or 0.0
    robust_last_r2 = mean([row["last_r2"] for row in robust_rows]) or 0.0
    robust_last_mae = mean([row["last_mae"] for row in robust_rows]) or 0.0
    robust_cv_r2 = mean([row["cv_r2_mean"] for row in robust_rows]) or 0.0
    robust_cv_mae = mean([row["cv_mae_mean"] for row in robust_rows]) or 0.0
    robust_lexical_mae = mean([row["lexical_mae"] for row in robust_rows]) or 0.0
    robust_lexical_fpr = mean([row["lexical_fpr"] for row in robust_rows]) or 0.0
    robust_perspective_spread = mean([row["perspective_spread"] for row in robust_rows]) or 0.0

    constrained_rows = constrained["rows"]
    constrained_active_mae = mean([row["active_mae"] for row in constrained_rows]) or 0.0
    constrained_absent_mae = mean([row["absent_mae"] for row in constrained_rows]) or 0.0
    constrained_recall = mean([row["gate_recall"] for row in constrained_rows]) or 0.0
    constrained_fpr = mean([row["gate_fpr"] for row in constrained_rows]) or 0.0
    constrained_deadzone = mean([row["deadzone_active_mae"] for row in constrained_rows]) or 0.0

    readout_chart = svg_line_chart(
        layers,
        [
            ("BF16", base_r2, "var(--io-accent)"),
            ("8-bit", q8_r2, "var(--io-accent-line)"),
            ("Q6-dequantized", q6_r2, "var(--io-ink-muted)"),
        ],
        "Mean held-out R2 by decoder layer",
        "Mean held-out R2",
    )
    gate_chart = svg_line_chart(
        gate_layers,
        [
            ("BF16", gate_base_f1, "var(--io-accent)"),
            ("8-bit", gate_q8_f1, "var(--io-accent-line)"),
            ("Q6-dequantized", gate_q6_f1, "var(--io-ink-muted)"),
        ],
        "Mean gate F1 by decoder layer",
        "Mean gate F1",
    )
    intensity_chart = svg_line_chart(
        int_layers,
        [
            ("BF16", int_base_mae, "var(--io-accent)"),
            ("8-bit", int_q8_mae, "var(--io-accent-line)"),
            ("Q6-dequantized", int_q6_mae, "var(--io-ink-muted)"),
        ],
        "Mean active MAE by decoder layer",
        "Mean active MAE (lower is better)",
    )

    document = f"""<!doctype html>
<html lang="en" data-io-theme="v2">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Narrative analysis of the Qwen 3.5 9B 27-channel latent readout, BF16, bitsandbytes 8-bit, and Q6-dequantized transfer, gate and intensity calibration.">
  <title>Qwen 3.5 9B readout analysis · IO Experiment</title>
  <link rel="stylesheet" href="../assets/io-design-system.css">
  <link rel="stylesheet" href="../assets/io-research.css">
  <link rel="stylesheet" href="../assets/io-readout.css">
  <link rel="stylesheet" href="../assets/io-theme-v2.css">
  <script src="../assets/io-research.js" defer></script>
</head>
<body class="io-document io-research io-readout" id="top">
  <a class="skip-link" href="#main-content">Skip to main content</a>

  <div class="container">
    <header>
      <span class="badge">Experiment report · Readout v1</span>
      <h1>What the Qwen 3.5 9B readout shows</h1>
      <p class="subtitle">A readout-first experiment: 27 latent channels, a decoder-layer sweep, BF16, bitsandbytes 8-bit, and Q6-dequantized transfer, gate and intensity calibration.</p>
      <p class="document-meta">Qwen/Qwen3.5-9B-Base · 864 contrastive rows · 162 mixed scenarios · BF16 + 8-bit + Q6-dequantized · Updated 2026-10-31</p>
      <p><a href="../notes/qwen-latent-experiment-plan.md">Experiment plan →</a> · <a href="../notes/quantization-transfer-plan.md">Quantization transfer plan →</a> · <a href="../index.html">Research index →</a></p>
    </header>

    <div class="research-layout">
      <nav class="research-index" aria-label="Table of contents">
        <details open>
          <summary>In this report <span class="index-toggle" aria-hidden="true"></span></summary>
          <ol>
            <li><a href="#orientation"><span class="index-number" aria-hidden="true">01</span><span>The question</span></a></li>
            <li><a href="#method"><span class="index-number" aria-hidden="true">02</span><span>Method</span></a></li>
            <li><a href="#readout-result"><span class="index-number" aria-hidden="true">03</span><span>Readout result</span></a></li>
            <li><a href="#channel-geometry"><span class="index-number" aria-hidden="true">04</span><span>Channel geometry</span></a></li>
            <li><a href="#eight-bit"><span class="index-number" aria-hidden="true">05</span><span>8-bit transfer</span></a></li>
            <li><a href="#gates-intensity"><span class="index-number" aria-hidden="true">06</span><span>Gates and intensity</span></a></li>
            <li><a href="#q6-transfer"><span class="index-number" aria-hidden="true">07</span><span>Q6 transfer</span></a></li>
            <li><a href="#robustness"><span class="index-number" aria-hidden="true">08</span><span>Robustness</span></a></li>
            <li><a href="#limits"><span class="index-number" aria-hidden="true">09</span><span>Limits</span></a></li>
            <li><a href="#next"><span class="index-number" aria-hidden="true">10</span><span>Next steps</span></a></li>
            <li><a href="#reproduce"><span class="index-number" aria-hidden="true">11</span><span>Reproduce</span></a></li>
          </ol>
        </details>
      </nav>

      <main id="main-content">
        <section id="orientation">
          <span class="section-label">01 / Orientation</span>
          <h2>The question is readout, not inner feeling</h2>
          <p>This experiment asks whether a coarse 27-channel affective/control state can be read from Qwen 3.5 9B’s residual stream. It does <strong>not</strong> claim that the model has 27 semantic feelings, a human-like affect system, or a validated control state.</p>
          <p>The 27 channels are a <strong>model-derived latent projection</strong>. They are useful because they give a compact vocabulary for testing readout, gating, and later steering. They are not direct measurements of experience.</p>
          <aside class="callout">
            <strong>What the result supports</strong>
            <p><mark>A coarse 27-channel projection is readable at mid-depth, and it survives 8-bit and Q6-dequantized weight loading well enough to recalibrate.</mark> The result does not yet establish that the projection is a causal control state or that steering will work.</p>
          </aside>
        </section>

        <section id="method">
          <span class="section-label">02 / Method</span>
          <h2>Mean-pooled residual states and per-channel ridge probes</h2>
          <p>The first readout used <strong>864 contrastive rows</strong>, 32 per channel, split into 675 train and 189 held-out rows. Each row has a coarse target: <code>0.0</code> absent, <code>0.5</code> moderate/mixed, or <code>1.0</code> strong. These are hand-crafted calibration anchors, not measured ground truth.</p>
          <p>For each prompt, the experiment extracts the mean-pooled hidden state at decoder layers <strong>10–28</strong>. It trains one ridge probe per channel and reports held-out R², MAE, confusion, perspective sensitivity, probe cosine, and centroid distance.</p>
          <p>The 8-bit run uses bitsandbytes with <code>load_in_8bit=True</code>. Its matmul path casts BF16 activations to FP16, so the run is best described as <strong>8-bit weights + FP16 compute</strong>, not BF16 compute.</p>
        </section>

        <section id="readout-result">
          <span class="section-label">03 / Readout result</span>
          <h2>Readout peaks around layer 14, then weakens</h2>
          <p>BF16, 8-bit, and Q6-dequantized runs all peak at <strong>layer 14</strong>. BF16 reaches mean held-out R² ≈ <strong>0.865</strong>; 8-bit reaches ≈ <strong>0.864</strong>; Q6-dequantized reaches ≈ <strong>0.865</strong>. The coarse error rate is about <strong>12%</strong> for BF16, <strong>11.6%</strong> for 8-bit, and <strong>12.7%</strong> for Q6-dequantized. Most errors are the expected <code>1.0 → 0.5</code> under-reading, not random channel collapse.</p>

          <div class="metric-grid">
            <div class="metric"><span class="metric-label">Best read layer</span><span class="metric-value">{best_read_layer}</span><p class="metric-note">All three backends agree.</p></div>
            <div class="metric"><span class="metric-label">BF16 mean R²</span><span class="metric-value">{fmt(base_best['mean_r2'])}</span><p class="metric-note">At layer {best_read_layer}.</p></div>
            <div class="metric"><span class="metric-label">8-bit mean R²</span><span class="metric-value">{fmt(q8_best['mean_r2'])}</span><p class="metric-note">At layer {best_read_layer}.</p></div>
            <div class="metric"><span class="metric-label">Q6 mean R²</span><span class="metric-value">{fmt(q6_best['mean_r2'])}</span><p class="metric-note">At layer {best_read_layer}.</p></div>
            <div class="metric"><span class="metric-label">BF16 coarse error</span><span class="metric-value">{fmt(coarse_rate)}</span><p class="metric-note">Held-out rows at layer {best_read_layer}.</p></div>
            <div class="metric"><span class="metric-label">Q6 coarse error</span><span class="metric-value">{fmt(q6_coarse_rate)}</span><p class="metric-note">Held-out rows at layer {best_read_layer}.</p></div>
          </div>

          <figure class="chart-card">
            <figcaption>Figure 01 · Mean held-out R² by decoder layer, BF16, 8-bit, and Q6-dequantized</figcaption>
            {readout_chart}
            <p class="chart-legend"><span><i></i>BF16</span><span><i class="secondary"></i>8-bit</span><span><i class="tertiary"></i>Q6-dequantized</span></p>
            <p class="figure-note">The three curves are nearly indistinguishable at the readout peak. The peak is a readout layer, not automatically a steering layer.</p>
          </figure>
        </section>

        <section id="channel-geometry">
          <span class="section-label">04 / Channel geometry</span>
          <h2>Some channels are much easier to read than others</h2>
          <p>At layer {best_read_layer}, the strongest channels are <strong>{html.escape(strongest[0][0])}</strong>, <strong>{html.escape(strongest[1][0])}</strong>, and <strong>{html.escape(strongest[2][0])}</strong>. The weakest include <strong>{html.escape(weakest[0][0])}</strong>, <strong>{html.escape(weakest[1][0])}</strong>, and <strong>{html.escape(weakest[2][0])}</strong>. This is a useful warning: the 27-channel taxonomy is not uniformly readable.</p>

          <div class="grid">
            <div>
              <h3>Strongest channels at layer {best_read_layer}</h3>
              <div class="table-container" role="region" aria-label="Strongest channels, horizontally scrollable" tabindex="0">
                <table><thead><tr><th>Channel</th><th>R²</th></tr></thead><tbody>{strongest_rows}</tbody></table>
              </div>
            </div>
            <div>
              <h3>Weakest channels at layer {best_read_layer}</h3>
              <div class="table-container" role="region" aria-label="Weakest channels, horizontally scrollable" tabindex="0">
                <table><thead><tr><th>Channel</th><th>R²</th></tr></thead><tbody>{weakest_rows}</tbody></table>
              </div>
            </div>
          </div>

          <div class="table-container" role="region" aria-label="Channel by layer R2 heatmap, horizontally scrollable" tabindex="0">
            <table class="heat-table">
              <caption>Table 01 · Channel × layer R² heatmap, BF16</caption>
              <thead><tr><th>Channel</th>{''.join(f'<th>{layer}</th>' for layer in layers)}</tr></thead>
              <tbody>{''.join(heat_rows)}</tbody>
            </table>
          </div>
          <p class="figure-note">The heatmap is descriptive. A darker cell means lower held-out R²; a lighter cell means stronger readout. The values remain visible, so colour is not the only carrier of meaning.</p>
        </section>

        <section id="eight-bit">
          <span class="section-label">05 / 8-bit transfer</span>
          <h2>8-bit is close for readout, but shifts gate and intensity layers</h2>
          <p>The 8-bit readout is almost identical to BF16. The gate and intensity calibrations are more backend-sensitive: the best gate layer moves from <strong>23</strong> to <strong>19</strong>, and the best intensity layer also moves from <strong>23</strong> to <strong>19</strong>.</p>

          <div class="table-container" role="region" aria-label="Channel R2 deltas at layer 14, horizontally scrollable" tabindex="0">
            <table>
              <caption>Table 02 · Largest 8-bit minus BF16 R² changes at layer {best_read_layer}</caption>
              <thead><tr><th>Channel</th><th>BF16 R²</th><th>8-bit R²</th><th>Delta</th></tr></thead>
              <tbody>{''.join(delta_rows)}</tbody>
            </table>
          </div>

          <aside class="callout">
            <strong>Practical reading</strong>
            <p>The readout geometry is robust enough to keep the 27-channel projection. The gate and intensity thresholds are not robust enough to copy across backends. Recalibrate on the exact backend.</p>
          </aside>
        </section>

        <section id="gates-intensity">
          <span class="section-label">06 / Gates and intensity</span>
          <h2>Binary activation and continuous intensity are separate problems</h2>
          <p>The gate calibration uses an FPR cap as the primary criterion, with Youden’s J as a diagnostic. The intensity calibration keeps the gate decision and then fits a linear mapping on active rows. This avoids treating a deadzone threshold as an intensity estimate.</p>

          <figure class="chart-card">
            <figcaption>Figure 02 · Mean gate F1 by decoder layer, BF16, 8-bit, and Q6-dequantized</figcaption>
            {gate_chart}
            <p class="chart-legend"><span><i></i>BF16</span><span><i class="secondary"></i>8-bit</span><span><i class="tertiary"></i>Q6-dequantized</span></p>
            <p class="figure-note">The 8-bit curve peaks at layer {best_gate_q8}; BF16 peaks at layer {best_gate_base}; Q6-dequantized peaks at layer {best_gate_q6}. These are calibration shifts, not readout failures.</p>
          </figure>

          <div class="table-container" role="region" aria-label="Gate and intensity summary by backend, horizontally scrollable" tabindex="0">
            <table>
              <caption>Table 03 · Best gate and intensity layers by backend</caption>
              <thead><tr><th>Backend</th><th>Gate layer</th><th>Mean F1</th><th>FPR</th><th>Recall</th><th>Active MAE</th><th>Absent MAE</th></tr></thead>
              <tbody>
                <tr><td>BF16</td><td>{best_gate_base}</td><td>{fmt(gate_base_summary[0])}</td><td>{fmt(gate_base_summary[1])}</td><td>{fmt(gate_base_summary[2])}</td><td>{fmt(gate_base_summary[3])}</td><td>{fmt(gate_base_summary[4])}</td></tr>
                <tr><td>8-bit</td><td>{best_gate_q8}</td><td>{fmt(gate_q8_summary[0])}</td><td>{fmt(gate_q8_summary[1])}</td><td>{fmt(gate_q8_summary[2])}</td><td>{fmt(gate_q8_summary[3])}</td><td>{fmt(gate_q8_summary[4])}</td></tr>
                <tr><td>Q6-dequantized</td><td>{best_gate_q6}</td><td>{fmt(gate_q6_summary[0])}</td><td>{fmt(gate_q6_summary[1])}</td><td>{fmt(gate_q6_summary[2])}</td><td>{fmt(gate_q6_summary[3])}</td><td>{fmt(gate_q6_summary[4])}</td></tr>
              </tbody>
            </table>
          </div>

          <figure class="chart-card">
            <figcaption>Figure 03 · Mean active MAE by decoder layer, BF16, 8-bit, and Q6-dequantized</figcaption>
            {intensity_chart}
            <p class="chart-legend"><span><i></i>BF16</span><span><i class="secondary"></i>8-bit</span><span><i class="tertiary"></i>Q6-dequantized</span></p>
            <p class="figure-note">Lower is better. The 8-bit best layer is {best_int_q8}; BF16 best is {best_int_base}; Q6-dequantized best is {best_int_q6}.</p>
          </figure>

          <div class="table-container" role="region" aria-label="Intensity summary by backend, horizontally scrollable" tabindex="0">
            <table>
              <caption>Table 04 · Best intensity layer by backend</caption>
              <thead><tr><th>Backend</th><th>Intensity layer</th><th>Active MAE</th><th>Absent MAE</th><th>Gate recall</th><th>Gate FPR</th><th>Deadzone active MAE</th></tr></thead>
              <tbody>
                <tr><td>BF16</td><td>{best_int_base}</td><td>{fmt(int_base_summary[0])}</td><td>{fmt(int_base_summary[1])}</td><td>{fmt(int_base_summary[2])}</td><td>{fmt(int_base_summary[3])}</td><td>{fmt(int_base_summary[4])}</td></tr>
                <tr><td>8-bit</td><td>{best_int_q8}</td><td>{fmt(int_q8_summary[0])}</td><td>{fmt(int_q8_summary[1])}</td><td>{fmt(int_q8_summary[2])}</td><td>{fmt(int_q8_summary[3])}</td><td>{fmt(int_q8_summary[4])}</td></tr>
                <tr><td>Q6-dequantized</td><td>{best_int_q6}</td><td>{fmt(int_q6_summary[0])}</td><td>{fmt(int_q6_summary[1])}</td><td>{fmt(int_q6_summary[2])}</td><td>{fmt(int_q6_summary[3])}</td><td>{fmt(int_q6_summary[4])}</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="q6-transfer">
          <span class="section-label">07 / Q6 transfer</span>
          <h2>Q6-dequantized readout is close; gates and intensity shift</h2>
          <p>The Q6_K checkpoint was run through the native Transformers GGUF path. Because no x86_64 CUDA GGUF matmul kernel is published for this machine, Transformers dequantized the whole model. The result is <strong>Q6 weights + dequantized BF16 compute</strong>, not true Q6 matmul.</p>
          <p>Q6-dequantized readout is essentially the same as BF16 at layer {best_read_layer}: mean R² ≈ <strong>{fmt(q6_best['mean_r2'])}</strong>. The gate best layer moves to <strong>{best_gate_q6}</strong> and the intensity best layer to <strong>{best_int_q6}</strong>. The gate and intensity metrics are close to BF16 but slightly weaker than the 8-bit run.</p>

          <div class="table-container" role="region" aria-label="Q6 readout deltas at layer 14, horizontally scrollable" tabindex="0">
            <table>
              <caption>Table 05 · Largest Q6-dequantized minus BF16 R² changes at layer {best_read_layer}</caption>
              <thead><tr><th>Channel</th><th>BF16 R²</th><th>Q6 R²</th><th>Delta</th></tr></thead>
              <tbody>{''.join(q6_delta_rows)}</tbody>
            </table>
          </div>

          <aside class="callout">
            <strong>Backend caveat</strong>
            <p>Q6-dequantized is a weight-only transfer check. It is useful for asking whether Q6 weights preserve the readout geometry, but it does not establish true Q6_K matmul behavior. True Q6 inference requires llama.cpp or a custom low-bit backend with layer hooks.</p>
          </aside>
        </section>

        <section id="robustness">
          <span class="section-label">08 / Robustness</span>
          <h2>Mean pooling is better; cross-validation is more conservative</h2>
          <p>Robustness checks were run on BF16 Base at layer {best_read_layer} and on the 8-bit model at layer {best_int_q8}. Mean-pooled readout is stronger than last-token readout, lexical/negative controls produce very few gate false positives, and isotonic intensity calibration improves the active-row MAE.</p>

          <div class="table-container" role="region" aria-label="Robustness summary, horizontally scrollable" tabindex="0">
            <table>
              <caption>Table 06 · BF16 robustness summary at layer {best_read_layer}</caption>
              <thead><tr><th>Check</th><th>Result</th></tr></thead>
              <tbody>
                <tr><td>Mean-pooled held-out R²</td><td>{fmt(robust_mean_r2)}</td></tr>
                <tr><td>Mean-pooled held-out MAE</td><td>{fmt(robust_mean_mae)}</td></tr>
                <tr><td>Last-token R²</td><td>{fmt(robust_last_r2)}</td></tr>
                <tr><td>Last-token MAE</td><td>{fmt(robust_last_mae)}</td></tr>
                <tr><td>5-fold cross-validation R²</td><td>{fmt(robust_cv_r2)}</td></tr>
                <tr><td>5-fold cross-validation MAE</td><td>{fmt(robust_cv_mae)}</td></tr>
                <tr><td>Lexical/negative-control MAE</td><td>{fmt(robust_lexical_mae)}</td></tr>
                <tr><td>Lexical/negative-control FPR</td><td>{fmt(robust_lexical_fpr)}</td></tr>
                <tr><td>Perspective spread</td><td>{fmt(robust_perspective_spread)}</td></tr>
              </tbody>
            </table>
          </div>

          <div class="table-container" role="region" aria-label="Isotonic intensity summary, horizontally scrollable" tabindex="0">
            <table>
              <caption>Table 07 · Isotonic intensity at 8-bit layer {best_int_q8}</caption>
              <thead><tr><th>Metric</th><th>Isotonic</th><th>Unconstrained linear</th></tr></thead>
              <tbody>
                <tr><td>Active MAE</td><td>{fmt(constrained_active_mae)}</td><td>{fmt(int_q8_summary[0])}</td></tr>
                <tr><td>Absent MAE</td><td>{fmt(constrained_absent_mae)}</td><td>{fmt(int_q8_summary[1])}</td></tr>
                <tr><td>Gate recall</td><td>{fmt(constrained_recall)}</td><td>{fmt(int_q8_summary[2])}</td></tr>
                <tr><td>Gate FPR</td><td>{fmt(constrained_fpr)}</td><td>{fmt(int_q8_summary[3])}</td></tr>
                <tr><td>Deadzone active MAE</td><td>{fmt(constrained_deadzone)}</td><td>{fmt(int_q8_summary[4])}</td></tr>
              </tbody>
            </table>
          </div>

          <aside class="callout">
            <strong>Robustness reading</strong>
            <p>The cross-validation R² is lower than the single train/test split, so the split result is somewhat optimistic. The readout is usable for exploratory steering, but not yet control-grade.</p>
          </aside>
        </section>

        <section id="limits">
          <span class="section-label">09 / Limits</span>
          <h2>Readout is not steering, and labels are coarse</h2>
          <p>The calibration labels are hand-crafted anchors, not measured ground truth. The 27 channels are a projection vocabulary, not a claim that the model experiences those states. Robustness checks reduce, but do not eliminate, the risk that the projection is diagnostic rather than control-grade.</p>
          <p>The most important limit is causal: <strong>read-best is not steer-best</strong>. A layer that predicts a channel well may not be the layer where activation addition changes behavior coherently. Steering must be tested separately with random-direction controls, dose-response, reversibility, and safety checks.</p>
          <p>Backend sensitivity is also real: 8-bit and Q6-dequantized readout are close to BF16, but gate and intensity best layers shift. Thresholds should not be copied across backends.</p>
        </section>

        <section id="next">
          <span class="section-label">10 / Next steps</span>
          <h2>Robustness is complete; next is bounded steering</h2>
          <p>The backend decision is fixed: BF16 is the reference, 8-bit is the deployment candidate, and Q6-dequantized is a transfer check only. Robustness checks are complete.</p>
          <p>The next practical sequence is:</p>
          <ol>
            <li>Start <code>experiments/steering/v1/</code> with activation addition at layers roughly 18–27.</li>
            <li>Include random-direction controls, dose-response, reversibility, coherence, and safety checks.</li>
            <li>Compare BF16 reference steering with 8-bit steering; do not infer steering from readout accuracy.</li>
          </ol>
          <p>Steering is a separate phase. It should not be inferred from readout accuracy.</p>
        </section>

        <section id="reproduce">
          <span class="section-label">11 / Reproduce</span>
          <h2>Commands for readout, quantization transfer, and robustness</h2>
          <p>BF16 readout:</p>
          <pre><code>poetry run python experiments/readout/v1/sweep.py \
  --model Qwen/Qwen3.5-9B-Base \
  --layers 10:28 \
  --out-json runs/readout-base.json \
  --out-csv runs/readout-base.csv</code></pre>
          <p>8-bit readout:</p>
          <pre><code>poetry run python experiments/readout/v1/sweep.py \
  --model Qwen/Qwen3.5-9B-Base \
  --quantization 8bit \
  --layers 10:28 \
  --out-json runs/readout-base-8bit.json \
  --out-csv runs/readout-base-8bit.csv</code></pre>
          <p>Q6-dequantized readout:</p>
          <pre><code>poetry run python experiments/readout/v1/sweep.py \
  --model models/qwen3.5-base-q6 \
  --gguf-file Qwen3.5-9B-Base.Q6_K.gguf \
  --layers 10:28 \
  --out-json runs/readout-base-q6-dequantized.json \
  --out-csv runs/readout-base-q6-dequantized.csv</code></pre>
          <p>Robustness checks:</p>
          <pre><code>poetry run python experiments/readout/v1/robustness.py \
  --model Qwen/Qwen3.5-9B-Base \
  --layer 14 \
  --out-json runs/robustness-base.json \
  --out-csv runs/robustness-base.csv</code></pre>
          <p>Isotonic intensity:</p>
          <pre><code>poetry run python experiments/readout/v1/constrained_intensity.py \
  --model Qwen/Qwen3.5-9B-Base \
  --quantization 8bit \
  --layer 19 \
  --gates runs/gates-base-8bit.json \
  --out-json runs/constrained-intensity-base-8bit.json \
  --out-csv runs/constrained-intensity-base-8bit.csv</code></pre>
        </section>
      </main>
    </div>

    <footer>Qwen 3.5 9B latent experiment · Readout v1 · Updated 2026-10-31</footer>
  </div>
</body>
</html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document, encoding="utf-8")
    print(f"Wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build narrative readout HTML")
    parser.add_argument("--readout", type=Path, default=Path("runs/readout-base.json"))
    parser.add_argument("--readout-8bit", type=Path, default=Path("runs/readout-base-8bit.json"))
    parser.add_argument("--readout-q6", type=Path, default=Path("runs/readout-base-q6-dequantized.json"))
    parser.add_argument("--gates", type=Path, default=Path("runs/gates-base.json"))
    parser.add_argument("--gates-8bit", type=Path, default=Path("runs/gates-base-8bit.json"))
    parser.add_argument("--gates-q6", type=Path, default=Path("runs/gates-base-q6-dequantized.json"))
    parser.add_argument("--intensity", type=Path, default=Path("runs/intensity-base.json"))
    parser.add_argument("--intensity-8bit", type=Path, default=Path("runs/intensity-base-8bit.json"))
    parser.add_argument("--intensity-q6", type=Path, default=Path("runs/intensity-base-q6-dequantized.json"))
    parser.add_argument("--robustness", type=Path, default=Path("runs/robustness-base.json"))
    parser.add_argument("--constrained-intensity", type=Path, default=Path("runs/constrained-intensity-base-8bit.json"))
    parser.add_argument("--out", type=Path, default=Path("docs/experiments/qwen-latent-readout-analysis.html"))
    args = parser.parse_args()
    build_report(
        args.readout,
        args.readout_8bit,
        args.readout_q6,
        args.gates,
        args.gates_8bit,
        args.gates_q6,
        args.intensity,
        args.intensity_8bit,
        args.intensity_q6,
        args.robustness,
        args.constrained_intensity,
        args.out,
    )


if __name__ == "__main__":
    main()
