import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from make_demo_data import generate  # noqa: E402
from summarize_cv import summarize as summarize_cv  # noqa: E402
from summarize_stress import summarize as summarize_stress  # noqa: E402


class AuxiliaryToolsTest(unittest.TestCase):
    def test_demo_and_summaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate(root)
            cv = summarize_cv(root / "cv", repetitions=2, folds=2)
            self.assertEqual(cv["split_count"], 4)
            self.assertAlmostEqual(cv["metrics"]["auroc"]["mean"], 0.7075)
            stress = summarize_stress(root / "stress_metrics.csv")
            self.assertEqual(stress["split_count"], 4)
            self.assertEqual(len(stress["results"]), 4)
            self.assertAlmostEqual(stress["results"][0]["auroc_change_mean"], -0.02)

    def test_cv_rejects_missing_split(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate(root)
            (root / "cv/repetition_1/fold_1/test_metrics.json").unlink()
            with self.assertRaisesRegex(ValueError, "missing splits"):
                summarize_cv(root / "cv", repetitions=2, folds=2)

    def test_stress_rejects_unmatched_split(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate(root)
            path = root / "stress_metrics.csv"
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            rows = [row for row in rows if not (row["model"] == "model_b" and
                    row["condition"] == "removal_40" and row["fold"] == "1")]
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "incomplete or unmatched"):
                summarize_stress(path)


if __name__ == "__main__":
    unittest.main()
