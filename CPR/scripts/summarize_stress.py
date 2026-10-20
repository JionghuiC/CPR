#!/usr/bin/env python3
"""Summarize paired stress-condition changes from aggregate split metrics."""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path


REQUIRED = {"model", "repetition", "fold", "condition", "auroc", "auprc"}


def summarize(path: Path, reference: str = "clean") -> dict:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError(f"CSV requires columns: {', '.join(sorted(REQUIRED))}")
        rows = list(reader)
    if not rows:
        raise ValueError("input CSV is empty")

    data: dict[tuple[str, int, int, str], dict[str, float]] = {}
    for row in rows:
        model, condition = row["model"].strip(), row["condition"].strip()
        if not model or not condition:
            raise ValueError("model and condition must be nonempty")
        rep, fold = int(row["repetition"]), int(row["fold"])
        if rep < 0 or fold < 0:
            raise ValueError("split indices must be nonnegative")
        key = (model, rep, fold, condition)
        if key in data:
            raise ValueError(f"duplicate model/split/condition: {key}")
        metrics = {name: float(row[name]) for name in ("auroc", "auprc")}
        if any(not math.isfinite(value) or not 0 <= value <= 1 for value in metrics.values()):
            raise ValueError(f"invalid AUROC/AUPRC for {key}")
        data[key] = metrics

    models = sorted({key[0] for key in data})
    conditions = sorted({key[3] for key in data})
    if reference not in conditions or len(conditions) < 2:
        raise ValueError("reference and at least one stress condition are required")
    split_sets = {model: {(rep, fold) for name, rep, fold, cond in data
                          if name == model and cond == reference} for model in models}
    common = split_sets[models[0]]
    if not common or any(splits != common for splits in split_sets.values()):
        raise ValueError("models must share the same nonempty reference split set")
    for model in models:
        for condition in conditions:
            observed = {(rep, fold) for name, rep, fold, cond in data
                        if name == model and cond == condition}
            if observed != common:
                raise ValueError(f"incomplete or unmatched splits for {model}/{condition}")

    results = []
    for model in models:
        for condition in conditions:
            if condition == reference:
                continue
            row = {"model": model, "condition": condition, "paired_splits": len(common)}
            for metric in ("auroc", "auprc"):
                deltas = [data[model, rep, fold, condition][metric] -
                          data[model, rep, fold, reference][metric]
                          for rep, fold in sorted(common)]
                row[f"{metric}_change_mean"] = statistics.mean(deltas)
                row[f"{metric}_change_std"] = (statistics.stdev(deltas)
                                                 if len(deltas) > 1 else None)
            results.append(row)
    return {"reference": reference, "split_count": len(common), "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--reference", default="clean")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(summarize(args.input, args.reference), indent=2) + "\n"
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
