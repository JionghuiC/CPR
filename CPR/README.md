# CPR Auxiliary Evaluation Tools

This repository contains small, standalone utilities for checking and summarizing aggregate evaluation results. It does **not** contain the CPR model, training code, checkpoints, patient records, predictions, cohort files, or unpublished experiment results.

The scripts require Python 3.10 or newer and use only the standard library. The included demo generates synthetic aggregate metrics; its numbers are not research results.

## Quick start

```bash
python3 scripts/make_demo_data.py --output demo_output
python3 scripts/summarize_cv.py --root demo_output/cv --repetitions 2 --folds 2
python3 scripts/summarize_stress.py --input demo_output/stress_metrics.csv
python3 -m unittest discover -s tests -v
```

## Input formats

`summarize_cv.py` reads files named `test_metrics.json` under paths containing `repetition_<n>/fold_<n>`. Each JSON object must contain numeric `AUC` and `PR` fields in `[0, 1]`. The script checks duplicate and missing splits before reporting split-level mean and sample standard deviation. It writes only aggregate counts and metrics, never input paths.

`summarize_stress.py` reads a CSV with columns `model,repetition,fold,condition,auroc,auprc`. Each model and split must have one `clean` row and one row for each other condition. All models must use the same split set. The output reports paired stressed-minus-clean differences within each split; it does not compare unmatched cohorts.

Both tools print JSON to stdout and accept `--output` to write it to a file. They do not load patient-level data. Only use public, synthetic, or otherwise authorized aggregate inputs.

## Release boundary

Publish **only the contents of this directory** as a separate GitHub repository. Do not push a parent research workspace: it may contain restricted clinical data, local paths, credentials, model implementations, checkpoints, or unfinished analyses. No claims about CPR performance or reproducibility are implied by this auxiliary release. Review the license and repository metadata before publishing.
