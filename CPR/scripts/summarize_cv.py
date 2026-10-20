#!/usr/bin/env python3
"""Summarize aggregate cross-validation metrics without loading patient data."""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from pathlib import Path


SPLIT_PATTERN = re.compile(r"(?:^|/)repetition_(\d+)/fold_(\d+)(?:/|$)")


def summarize(root: Path, repetitions: int | None = None, folds: int | None = None) -> dict:
    if (repetitions is None) != (folds is None):
        raise ValueError("--repetitions and --folds must be provided together")
    if repetitions is not None and (repetitions < 1 or folds < 1):
        raise ValueError("repetitions and folds must be positive")

    splits: dict[tuple[int, int], dict[str, float]] = {}
    for path in sorted(root.rglob("test_metrics.json")):
        match = SPLIT_PATTERN.search(path.relative_to(root).as_posix())
        if match is None:
            raise ValueError(f"metric file lacks repetition/fold directories: {path.name}")
        key = tuple(map(int, match.groups()))
        if key in splits:
            raise ValueError(f"duplicate metrics for repetition {key[0]}, fold {key[1]}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        metrics = {}
        for source, target in (("AUC", "auroc"), ("PR", "auprc")):
            value = raw.get(source)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{source} must be numeric for repetition {key[0]}, fold {key[1]}")
            value = float(value)
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{source} must be finite and in [0,1]")
            metrics[target] = value
        splits[key] = metrics

    if not splits:
        raise ValueError("no test_metrics.json files found")
    missing = []
    if repetitions is not None:
        expected = {(rep, fold) for rep in range(repetitions) for fold in range(folds)}
        extra = sorted(set(splits) - expected)
        if extra:
            raise ValueError(f"split indices outside expected grid: {extra}")
        missing = sorted(expected - set(splits))
        if missing:
            raise ValueError(f"missing splits: {missing}")

    result = {"split_count": len(splits), "repetitions": len({key[0] for key in splits}),
              "folds": len({key[1] for key in splits}), "metrics": {}}
    for name in ("auroc", "auprc"):
        values = [entry[name] for _, entry in sorted(splits.items())]
        result["metrics"][name] = {"mean": statistics.mean(values),
                                   "std": statistics.stdev(values) if len(values) > 1 else None,
                                   "min": min(values), "max": max(values)}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--folds", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(summarize(args.root, args.repetitions, args.folds), indent=2) + "\n"
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
