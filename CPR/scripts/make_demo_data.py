#!/usr/bin/env python3
"""Generate deterministic synthetic aggregate metrics for the CLI examples."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def generate(output: Path) -> None:
    cv_root = output / "cv"
    stress_rows = []
    for rep in range(2):
        for fold in range(2):
            offset = 0.01 * rep + 0.005 * fold
            metrics = {"AUC": round(0.70 + offset, 4), "PR": round(0.40 + offset, 4)}
            split = cv_root / f"repetition_{rep}" / f"fold_{fold}"
            split.mkdir(parents=True, exist_ok=True)
            (split / "test_metrics.json").write_text(json.dumps(metrics) + "\n", encoding="utf-8")
            for model, shift in (("model_a", 0.0), ("model_b", 0.025)):
                for condition, reduction in (("clean", 0.0), ("removal_20", 0.02),
                                             ("removal_40", 0.05)):
                    stress_rows.append({"model": model, "repetition": rep, "fold": fold,
                                        "condition": condition,
                                        "auroc": round(metrics["AUC"] + shift - reduction, 4),
                                        "auprc": round(metrics["PR"] + shift - reduction, 4)})
    with (output / "stress_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(stress_rows[0]))
        writer.writeheader()
        writer.writerows(stress_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("demo_output"))
    args = parser.parse_args()
    generate(args.output)
    print("Synthetic aggregate demo created; values are not research results.")


if __name__ == "__main__":
    main()
