# Data

This folder documents the data used in the **Hospital Readmission Reduction Initiative**. Raw and processed files are stored under `readmission_project/data/` to keep paths consistent with the pipeline.

## Source data

| File | Description |
|------|-------------|
| `readmission_project/data/diabetic_data.csv` | Encounter-level data (demographics, admission, diagnoses, procedures, medications, outcomes). |
| `readmission_project/data/IDS_mapping.csv` | Mappings for admission source, discharge disposition, admission type. |

## Pipeline-generated data

| File | Description |
|------|-------------|
| `readmission_project/data/readmissions.db` | SQLite database created by `scripts/01_load_data.py`; used by cohort SQL. |
| `readmission_project/data/model_ready_data.csv` | Cleaned, feature-engineered dataset (after `scripts/02_prepare_model_data.py`). |
| `readmission_project/data/X_train.csv`, `X_test.csv` | Feature matrices (train/test split). |
| `readmission_project/data/y_train.csv`, `y_test.csv` | Target (30-day readmission flag) for train/test. |

## Cohort and scope

- **Encounters:** 99,492 (after exclusions).
- **Target:** 30-day readmission indicator.
- **Readmission rate:** 9.5% (9,433 readmissions).

For column definitions and feature engineering logic, see `scripts/02_prepare_model_data.py` and `scripts/02_readmission_cohorts.sql`.
