# Scripts — Pipeline Overview

This folder contains the **core data and analytics pipeline** for the Hospital Readmission Reduction Initiative. Run in order (or use root `run_all.py`).

| Script | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| **01_load_data.py** | Load raw CSVs into SQLite | `readmission_project/data/diabetic_data.csv`, `IDS_mapping.csv` | `readmission_project/data/readmissions.db` |
| **02_readmission_cohorts.sql** | Define cohorts and 30-day readmission flag | `readmissions.db` | Temp tables + `readmission_analytics` view |
| **02_prepare_model_data.py** | Feature engineering, train/test split | `readmission_analytics` (via DB), model_ready_data | `model_ready_data.csv`, `X_train/test`, `y_train/test` |
| **03_logistic_regression.py** | Train model, evaluate, save | `X_train`, `y_train`, `X_test`, `y_test` | `readmission_model.pkl`, `scaler.pkl`, `model_performance.png` |
| **04_financial_impact_analysis.py** | ROI, cost by diagnosis/age, dashboards | `model_ready_data.csv`, risk outputs | `financial_analysis_dashboard.png`, CSVs, impact statement |

**Paths:** All paths are relative to the **repository root**; data and outputs live under `readmission_project/data/` and `readmission_project/outputs/`.

**Run full pipeline:** From repo root, `python run_all.py`.
