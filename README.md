# CPR: Clinical Progression Residual Network

**Observation-Supported Progression Residual Learning for Clinical Risk Prediction from Longitudinal EHRs**

This repository accompanies our research on clinical risk prediction from longitudinal electronic health records (EHRs).

## Overview

Clinical risk prediction depends not only on a patient's current measurements but also on how clinical variables evolve over time. However, changes estimated from sparse or irregular observations may be unreliable. CPR addresses this challenge by learning patient-specific progression together with the observational evidence supporting each estimated change.

The framework comprises four complementary components.

- **Patient-state encoding** captures the current clinical state from longitudinal EHR information.
- **Observation-supported progression modeling** characterizes variable-level changes relative to preceding observations across multiple temporal contexts. Historical coverage, measurement freshness, and observation status are used to estimate support for these changes.
- **Cumulative observation-aware summary** provides complementary information about the patient's recorded clinical history.
- **Controlled residual refinement** selectively integrates progression and cumulative context into the patient-state prediction through gated residual corrections.

## Evaluation

CPR is evaluated on three clinical prediction tasks:

- In-hospital mortality prediction
- Acute kidney injury (AKI) prediction
- Sepsis prediction

Experiments use the **MIMIC-III**, **MIMIC-IV**, and **eICU** datasets under standardized evaluation protocols.

## Code Availability

**The complete source code and instructions for reproducing the experiments will be released upon publication of the associated paper.**

Before the full release, this repository may contain selected supporting scripts and project documentation. These preliminary materials do not constitute a complete reproduction package.

## Data Availability

The clinical datasets are subject to the access requirements of their respective providers and are not redistributed through this repository. Researchers should obtain access through the official dataset channels.

## Citation

The citation and paper link will be added after publication.
