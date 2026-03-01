# Visualizations

This folder is the **portfolio home for key charts** produced by the Hospital Readmission Reduction Initiative. The pipeline writes images to `readmission_project/outputs/`; copies or references for recruiters are documented here.

## Generated charts

| Chart | Description | Source path |
|-------|-------------|-------------|
| **Readmission dashboard** | KPIs, readmission trend, risk heat map, diagnosis cost | `readmission_project/outputs/readmission_dashboard.png` |
| **Financial dashboard** | Cost by diagnosis/age, ROI scenarios, CMS | `readmission_project/outputs/financial_analysis_dashboard.png` |
| **Model performance** | ROC curve, precision-recall, feature coefficients, odds ratios | `readmission_project/outputs/model_performance.png` |
| **Model odds ratios** | Horizontal bar chart: risk (red) vs protective (green) factors | `readmission_project/outputs/model_viz.png` |
| **Model + scaler** | Odds ratios plus scaler mean/scale per feature | `readmission_project/outputs/model_and_scaler.png` |

## How to regenerate

1. **Full pipeline:** From repo root run `python run_all.py` — produces all dashboards and model outputs.
2. **Model charts only:** Run `scripts/03_logistic_regression.py`, then `readmission_project/outputs/model_coefficients_viz.py` and `model_and_scaler_to_png.py`.

All paths are relative to the repository root; data and scripts are in `readmission_project/` and `scripts/`.
