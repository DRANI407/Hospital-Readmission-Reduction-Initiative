# Data Analysis Workflow — Hospital Readmission Reduction Initiative

This document describes the **end-to-end data analysis workflow** used in the project: from raw data to cleaned cohorts, feature engineering, modeling, and business reporting.

---

## 1. Data cleaning pipeline

| Step | Script / artifact | Description |
|------|-------------------|-------------|
| **Ingest** | `scripts/01_load_data.py` | Load `diabetic_data.csv` and `IDS_mapping.csv` into SQLite (`readmission_project/data/readmissions.db`). Build normalized tables: encounters, admission types, discharge dispositions, admission sources. |
| **Cohort definition** | `scripts/02_readmission_cohorts.sql` | Define 30-day readmission flag, exclusions, and analytics view (`readmission_analytics`). Run via `run_all.py` after DB creation. |
| **Model-ready dataset** | `scripts/02_prepare_model_data.py` | Filter (e.g., non-null age, known race/gender), engineer 15 features, drop missing rows. Output: `model_ready_data.csv`, train/test splits (`X_train`, `X_test`, `y_train`, `y_test`). |

**Cleaning rules (summary):** Missing age/race excluded; gender restricted to Male/Female; ICD-9 used to derive comorbidity flags; prior utilization and polypharmacy derived from encounter counts and medication count.

---

## 2. Exploratory data analysis (EDA)

- **Readmission rate:** Overall 9.5% (9,433 / 99,492).
- **Demographics:** Age bands, gender, race (where available).
- **Clinical:** Length of stay, number of procedures/labs/medications/diagnoses, insulin and A1C.
- **Utilization:** Prior inpatient, emergency, outpatient visits.
- **Outcome:** Distribution of 30-day readmission by segment; used to define risk quartiles and high-risk profile.

EDA is embedded in the pipeline scripts and in the financial/risk stratification steps. A Jupyter notebook for ad-hoc EDA is available in `notebooks/` (see README there).

---

## 3. Statistical analysis

- **Model:** Logistic regression (L2, balanced class weight) on **standardized** features.
- **Metrics:** ROC-AUC (~0.71), sensitivity, specificity, PPV, NPV; confusion matrix.
- **Inference:** Coefficients and odds ratios (exp(coef)) per feature; approximate interpretation per 1 SD change.
- **Risk stratification:** Quartiles of predicted probability (Low / Medium-Low / Medium-High / High); readmission rate and share of readmissions by quartile.

Statsmodels was attempted for detailed inference but skipped when singular matrix occurred; sklearn coefficients and odds ratios are used and documented in `reports/MODEL_CARD.md`.

---

## 4. Feature importance / risk factors

Feature importance is derived from **absolute coefficient** and **odds ratio**:

1. **high_prior_utilization** (OR 1.68) — Strongest risk factor.  
2. **number_diagnoses** (OR 1.36) — Comorbidity burden.  
3. **num_procedures** (OR 0.83) — Protective in this model (context-dependent).  
4. **polypharmacy** (OR 1.17), **time_in_hospital** (OR 1.12), **insulin_level** (OR 1.10), **diabetes_complications** (OR 1.08), plus cardiovascular, renal, respiratory, long_los.

Full table: `readmission_project/outputs/feature_importance.csv` or `model_coefficients.xlsx`. Visual: `readmission_project/outputs/model_viz.png`.

---

## 5. Financial and business analysis

- **Cost:** $15,000 per readmission (moderate scenario); total ~$141.5M annual.
- **By diagnosis:** Other, Diabetes, Heart Failure, CAD, COPD, Pneumonia (see Executive Summary).
- **By age:** Medicare-eligible (65+) and age bands for targeting.
- **ROI:** Transitional care at $750/patient; 50% high-risk coverage at 15% effectiveness → $9.4M net, 123.7% ROI.
- **CMS:** Readmission rate below benchmark → $0 penalty; narrative for maintaining and improving.

---

## 6. Execution order

Recommended run order (as in `run_all.py`):

1. `scripts/01_load_data.py`  
2. `scripts/02_readmission_cohorts.sql` (via sqlite3 or run_all)  
3. `scripts/02_prepare_model_data.py`  
4. `scripts/03_logistic_regression.py`  
5. `scripts/04_financial_impact_analysis.py`  
6. `readmission_project/dashboard/build_dashboard.py`  

Optional: `readmission_project/outputs/model_coefficients_viz.py`, `model_and_scaler_to_png.py`, `export_coefficients_table.py` for extra charts and exports.
