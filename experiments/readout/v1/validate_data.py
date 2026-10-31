"""Validate calibration JSONL files without ML dependencies.

Checks schema, allowed channels, targets, perspectives, split coverage,
duplicate IDs, and basic mixed-state constraints.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

CHANNELS = {
    "admiration",
    "adoration",
    "aesthetic_appreciation",
    "amusement",
    "anger",
    "anxiety",
    "awe",
    "awkwardness",
    "boredom",
    "calmness",
    "confusion",
    "craving",
    "disgust",
    "empathetic_pain",
    "entrancement",
    "excitement",
    "fear",
    "horror",
    "interest",
    "joy",
    "nostalgia",
    "relief",
    "romance",
    "sadness",
    "satisfaction",
    "sexual_desire",
    "surprise",
}
PERSPECTIVES = {"first_person", "third_person", "observer", "quoted", "neutral"}
SPLITS = {"train", "test"}
TARGETS = {0.0, 0.5, 1.0}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def validate_contrastive(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    ids: set[str] = set()
    channel_counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    target_counts: Counter[str] = Counter()

    for row in rows:
        required = {"id", "text", "kind", "channel", "target", "perspective", "split"}
        missing = required - row.keys()
        if missing:
            errors.append(f"{row.get('id', '?')}: missing fields {sorted(missing)}")
            continue
        if row["kind"] != "contrastive":
            errors.append(f"{row['id']}: kind must be 'contrastive'")
        if row["channel"] not in CHANNELS:
            errors.append(f"{row['id']}: unknown channel {row['channel']!r}")
        if row["target"] not in TARGETS:
            errors.append(f"{row['id']}: target must be one of {sorted(TARGETS)}")
        if row["perspective"] not in PERSPECTIVES:
            errors.append(f"{row['id']}: unknown perspective {row['perspective']!r}")
        if row["split"] not in SPLITS:
            errors.append(f"{row['id']}: split must be 'train' or 'test'")
        if not isinstance(row["text"], str) or not row["text"].strip():
            errors.append(f"{row['id']}: text must be non-empty")
        if row["id"] in ids:
            errors.append(f"{row['id']}: duplicate ID")
        ids.add(row["id"])
        channel_counts[row["channel"]] += 1
        split_counts[row["split"]] += 1
        target_counts[row["target"]] += 1

    for channel in sorted(CHANNELS):
        parts = Counter(row["split"] for row in rows if row.get("channel") == channel)
        if parts["train"] == 0 or parts["test"] == 0:
            errors.append(f"{channel}: needs both train and test rows")

    summary = {
        "rows": len(rows),
        "unique_ids": len(ids),
        "channels": dict(sorted(channel_counts.items())),
        "splits": dict(sorted(split_counts.items())),
        "targets": dict(sorted(target_counts.items())),
    }
    return summary, errors


def validate_mixed(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    ids: set[str] = set()
    split_counts: Counter[str] = Counter()
    active_counts: Counter[int] = Counter()
    channel_counts: Counter[str] = Counter()

    for row in rows:
        required = {"id", "text", "kind", "channels", "perspective", "split"}
        missing = required - row.keys()
        if missing:
            errors.append(f"{row.get('id', '?')}: missing fields {sorted(missing)}")
            continue
        if row["kind"] != "mixed":
            errors.append(f"{row['id']}: kind must be 'mixed'")
        if row["perspective"] not in PERSPECTIVES:
            errors.append(f"{row['id']}: unknown perspective {row['perspective']!r}")
        if row["split"] not in SPLITS:
            errors.append(f"{row['id']}: split must be 'train' or 'test'")
        if not isinstance(row["text"], str) or not row["text"].strip():
            errors.append(f"{row['id']}: text must be non-empty")
        if row["id"] in ids:
            errors.append(f"{row['id']}: duplicate ID")
        ids.add(row["id"])

        channels = row["channels"]
        if not isinstance(channels, dict):
            errors.append(f"{row['id']}: channels must be an object")
            continue
        if len(channels) < 2:
            errors.append(f"{row['id']}: mixed row needs at least two active channels")
        for channel, value in channels.items():
            if channel not in CHANNELS:
                errors.append(f"{row['id']}: unknown channel {channel!r}")
            if value not in TARGETS:
                errors.append(f"{row['id']}: channel target must be one of {sorted(TARGETS)}")
            channel_counts[channel] += 1

        active_counts[len(channels)] += 1
        split_counts[row["split"]] += 1

    summary = {
        "rows": len(rows),
        "unique_ids": len(ids),
        "active_channels": dict(sorted(active_counts.items())),
        "splits": dict(sorted(split_counts.items())),
        "channel_mentions": dict(sorted(channel_counts.items())),
    }
    return summary, errors


def validate_full_channels(
    rows: list[dict[str, Any]],
    kind: str,
    require_active: bool,
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    ids: set[str] = set()
    split_counts: Counter[str] = Counter()
    active_counts: Counter[int] = Counter()
    channel_counts: Counter[str] = Counter()

    for row in rows:
        required = {"id", "text", "kind", "channels", "perspective", "split"}
        missing = required - row.keys()
        if missing:
            errors.append(f"{row.get('id', '?')}: missing fields {sorted(missing)}")
            continue
        if row["kind"] != kind:
            errors.append(f"{row['id']}: kind must be {kind!r}")
        if row["perspective"] not in PERSPECTIVES:
            errors.append(f"{row['id']}: unknown perspective {row['perspective']!r}")
        if row["split"] not in SPLITS:
            errors.append(f"{row['id']}: split must be 'train' or 'test'")
        if not isinstance(row["text"], str) or not row["text"].strip():
            errors.append(f"{row['id']}: text must be non-empty")
        if row["id"] in ids:
            errors.append(f"{row['id']}: duplicate ID")
        ids.add(row["id"])

        channels = row["channels"]
        if not isinstance(channels, dict):
            errors.append(f"{row['id']}: channels must be an object")
            continue
        if set(channels) != CHANNELS:
            errors.append(f"{row['id']}: channels must contain all 27 keys")
        for channel, value in channels.items():
            if channel not in CHANNELS:
                errors.append(f"{row['id']}: unknown channel {channel!r}")
            if value not in TARGETS:
                errors.append(f"{row['id']}: channel target must be one of {sorted(TARGETS)}")
            if value > 0.0:
                channel_counts[channel] += 1

        active = sum(value > 0.0 for value in channels.values())
        active_counts[active] += 1
        split_counts[row["split"]] += 1

        if require_active and active < 2:
            errors.append(f"{row['id']}: needs at least two active channels")
        if kind == "negative_control" and active != 0:
            errors.append(f"{row['id']}: negative control must have all channels 0.0")

    summary = {
        "rows": len(rows),
        "unique_ids": len(ids),
        "active_channels": dict(sorted(active_counts.items())),
        "splits": dict(sorted(split_counts.items())),
        "channel_mentions": dict(sorted(channel_counts.items())),
    }
    return summary, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate calibration JSONL files")
    parser.add_argument("--contrastive", type=Path, default=Path("data/calibration/contrastive.jsonl"))
    parser.add_argument("--mixed", type=Path, default=Path("data/calibration/mixed.jsonl"))
    parser.add_argument("--negative-controls", type=Path, default=Path("data/calibration/negative_controls.jsonl"))
    parser.add_argument("--mixed-labeled", type=Path, default=Path("data/calibration/mixed_labeled.jsonl"))
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    all_errors: list[str] = []
    report: dict[str, Any] = {}

    validators = (
        ("contrastive", args.contrastive, validate_contrastive),
        ("mixed", args.mixed, validate_mixed),
        ("negative_controls", args.negative_controls, lambda rows: validate_full_channels(rows, "negative_control", False)),
        ("mixed_labeled", args.mixed_labeled, lambda rows: validate_full_channels(rows, "mixed_labeled", True)),
    )

    for label, path, validator in validators:
        rows = load_jsonl(path)
        summary, errors = validator(rows)
        report[label] = summary
        all_errors.extend(errors)

    report["errors"] = all_errors
    report["ok"] = not all_errors

    text = json.dumps(report, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    sys.exit(0 if not all_errors else 1)


if __name__ == "__main__":
    main()
