# 🏥 Hospital Readmission Reduction Initiative

### A data-driven case study in healthcare analytics for value-based care

---

<p align="center">
  <strong>Python</strong> · <strong>Pandas</strong> · <strong>SQL</strong> · <strong>Scikit-learn</strong> · <strong>Data Visualization</strong>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Business Problem](#-business-problem)
- [Why Readmissions Matter](#-why-hospital-readmissions-matter)
- [Dataset](#-dataset)
- [Tools & Technologies](#-tools--technologies)
- [Project Architecture](#-project-architecture)
- [Methodology](#-methodology)
- [Visualizations & Key Findings](#-visualizations--key-findings)
- [Business Impact](#-business-impact)
- [Actionable Recommendations](#-actionable-recommendations)
- [Future Improvements](#-future-improvements)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)

---

## 📌 Overview

This project is a **end-to-end healthcare analytics case study** that identifies drivers of 30-day hospital readmissions, builds a predictive risk model, and quantifies the financial impact of targeted interventions. The work is designed to support **value-based care** decisions: reducing avoidable readmissions, improving quality metrics, and minimizing CMS penalty exposure under the Hospital Readmission Reduction Program (HRRP).

| Deliverable | Description |
|-------------|-------------|
| **Predictive model** | Logistic regression for 30-day readmission risk (ROC-AUC ~0.71) |
| **Risk stratification** | High/medium/low risk segments with actionable profiles |
| **Financial analysis** | Cost by diagnosis, ROI scenarios, CMS penalty assessment |
| **Dashboards & reports** | Executive summary, model card, visualizations |

---

## 🎯 Business Problem

Hospitals face:

1. **Financial pressure** — Unplanned 30-day readmissions drive avoidable cost (~$15K per readmission in many studies).
2. **Regulatory risk** — CMS HRRP penalizes excess readmissions for conditions such as heart failure, pneumonia, and acute myocardial infarction.
3. **Quality goals** — Readmission rates are a core quality and patient-safety metric.

**Objective:** Use historical encounter data to **identify high-risk patients**, **explain key risk factors**, and **estimate the ROI of targeted transitional care** so leadership can prioritize resources and interventions.

---

## 💡 Why Hospital Readmissions Matter

| Dimension | Impact |
|-----------|--------|
| **Operational** | Readmissions strain bed capacity, nursing, and ED; disrupt planned care. |
| **Financial** | Avoidable readmissions cost U.S. hospitals billions annually; Medicare may not fully reimburse. |
| **Regulatory** | HRRP ties Medicare reimbursement to excess readmission ratios; penalties can be material. |
| **Clinical** | High readmission rates signal gaps in discharge planning, follow-up, and chronic disease management. |

This project links **data cleaning → EDA → feature engineering → modeling → financial analysis** to support decisions at the CMO/CFO level.

---

## 📂 Dataset

- **Source:** Diabetes 130-US hospitals dataset (UCI / real-world encounters, 1999–2008).
- **Scale:** **99,492** encounters after cohort definition; **9,433** 30-day readmissions (9.5% rate).
- **Content:** Demographics, admission/discharge, diagnoses (ICD-9), procedures, medications, length of stay, prior utilization, and readmission outcome.
- **Location:** Raw and processed data live in `data/` (see [Repository Structure](#-repository-structure)).

| Artifact | Description |
|----------|-------------|
| `diabetic_data.csv` | Core encounter-level data |
| `IDS_mapping.csv` | Mapping for admission source, discharge disposition, etc. |
| `readmissions.db` | SQLite database (loaded by pipeline) |
| `model_ready_data.csv` | Cleaned, feature-engineered dataset for modeling |

---

## 🛠 Tools & Technologies

| Category | Tools |
|----------|--------|
| **Language** | Python 3.11 |
| **Data manipulation** | Pandas, NumPy |
| **Database** | SQLite, SQL (cohort and analytics queries) |
| **Modeling** | Scikit-learn (Logistic Regression, StandardScaler) |
| **Statistics** | Statsmodels (optional diagnostics) |
| **Visualization** | Matplotlib, Seaborn |
| **Notebooks** | Jupyter (EDA, exploration) |
| **Export** | CSV, Excel (openpyxl), JSON, ONNX (optional) |

---

## 🏗 Project Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     HOSPITAL READMISSION REDUCTION PIPELINE                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   RAW DATA   │────▶│  LOAD & ETL   │────▶│  COHORT SQL   │────▶│  FEATURE      │
  │  (CSV, IDs)  │     │  (SQLite DB)  │     │  (Analytics   │     │  ENGINEERING  │
  └──────────────┘     └──────────────┘     │   View)       │     │  (Train/Test) │
                                             └──────────────┘     └───────┬───────┘
                                                                         │
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐             │
  │  DASHBOARDS  │◀────│  FINANCIAL   │◀────│  PREDICTIVE  │◀────────────┘
  │  & REPORTS   │     │  IMPACT      │     │  MODEL       │
  │  (PNG, MD)   │     │  (ROI, CMS)  │     │  (LR + Scaler)│
  └──────────────┘     └──────────────┘     └──────────────┘
```

**Pipeline:** `scripts/01_load_data.py` → `03_readmission_cohorts.sql` → `02_explore_data.sql` → `04_risk_factor_analysis.sql` → `05_prepare_model_data.py` → `06_logistic_regression.py` → `07_financial_analysis.py` → `08_dashboard_data.sql`. Run all via **`python run_all.py`** or **`python scripts/run_all.py`** from repo root.

---

## 📐 Methodology

### 1. Data cleaning pipeline

- Ingest `diabetic_data.csv` and `IDS_mapping.csv` into SQLite.
- Resolve admission source, discharge disposition, and encounter keys.
- Apply cohort logic (30-day readmission flag, exclusions) in SQL.

### 2. Exploratory data analysis (EDA)

- Readmission rate by demographics, length of stay, and diagnosis.
- Distribution of procedures, medications, and prior utilization.
- Identification of missing values and exclusion rules for modeling.

### 3. Feature engineering

- **Demographic:** Age band midpoint.
- **Clinical:** Time in hospital, number of lab procedures, procedures, medications, diagnoses.
- **Comorbidity flags:** Diabetes complications, cardiovascular, respiratory, renal (ICD-9 derived).
- **Utilization:** High prior utilization (ED/inpatient/outpatient thresholds), long length of stay (>7 days), polypharmacy (15+ medications), A1C abnormal, insulin level.

### 4. Statistical analysis & modeling

- **Model:** Logistic regression (L2, balanced class weight) on standardized features.
- **Outputs:** Coefficients, odds ratios, ROC-AUC (~0.71), risk quartiles.
- **Interpretation:** Top risk factors (e.g., high prior utilization, number of diagnoses, polypharmacy) and protective patterns.

### 5. Feature importance / risk factors

| Rank | Feature | Odds ratio | Interpretation |
|------|---------|------------|-----------------|
| 1 | high_prior_utilization | 1.68 | Prior high use → higher readmission odds |
| 2 | number_diagnoses | 1.36 | More diagnoses → higher risk |
| 3 | num_procedures | 0.83 | More procedures → slightly lower risk (context-dependent) |
| 4 | polypharmacy | 1.17 | 15+ medications → higher risk |
| 5 | time_in_hospital | 1.12 | Longer stay → higher risk |

Full coefficient table: `readmission_project/outputs/feature_importance.csv` or `model_coefficients.xlsx`.

---

## 📊 Visualizations & Key Findings

| Visualization | Description | Location |
|----------------|-------------|----------|
| **Model coefficients** | Risk vs protective factors (bar chart) | `outputs/visuals/model_coefficients_visual.png` |
| **Feature importance** | ROC, precision-recall, coefficients | `outputs/visuals/feature_importance_styled.png` |
| **Financial dashboard** | Cost by diagnosis, age, ROI scenarios | `outputs/visuals/financial_impact_dashboard.png` |
| **Readmission trend** | KPIs, trends | `outputs/visuals/readmission_trend.png` |
| **Risk heat map** | Risk by segment | `outputs/visuals/risk_heatmap.png` |

**Key findings:**

- **9.5%** 30-day readmission rate (below national benchmark **15.5%** → **$0** CMS penalty in this analysis).
- Top **20%** highest-risk patients account for **~39%** of readmissions.
- **High-risk profile:** 65+, diabetes with complications/CVD/renal, LOS >7 days, polypharmacy, high prior utilization.
- **Largest cost drivers:** Other (61%), Diabetes (12%), Heart Failure (11%), CAD (7%), COPD (5%), Pneumonia (4%) at $15K/readmission.

---

## 💼 Business Impact

Hospitals can use this analysis to:

1. **Target interventions** — Focus transitional care (e.g., discharge planning, 48-hour follow-up, medication reconciliation) on the **top 50% of high-risk patients** (~10K patients).
2. **Quantify ROI** — At **$750/patient** program cost and **15%** reduction in readmissions in that cohort: **~$17M savings**, **~$9.4M net benefit**, **123.7% ROI**.
3. **Maintain compliance** — Keep readmission rate below benchmark to avoid HRRP penalties; use model for ongoing monitoring and prioritization.
4. **Resource allocation** — Allocate case management and home health to diagnosis groups with highest cost (e.g., heart failure, diabetes) within the high-risk segment.

> **Impact statement:** *"Targeted discharge planning and transitional care for the top 50% of high-risk patients could reduce readmissions by 12%, avoid ~1,132 readmissions annually, generate $17.0M in savings, and deliver $9.4M net benefit at 123.7% ROI while improving quality scores."*

---

## ✅ Actionable Recommendations

| Priority | Action | Expected impact |
|----------|--------|------------------|
| 1 | Implement transitional care for top 50% high-risk (≈10,122 patients) | 1,132 readmissions avoided; $9.4M net benefit |
| 2 | Target heart failure and diabetes for specialized discharge protocols | Focus within high-risk cohort |
| 3 | Expand medication reconciliation for patients with 15+ medications | Reduce polypharmacy-related readmissions |
| 4 | Establish post-discharge follow-up within 48 hours | Support transitional care effectiveness |

---

## 🔮 Future Improvements

- **Model:** Try tree-based models (e.g., Random Forest, XGBoost) and calibration; add confidence intervals for odds ratios.
- **Data:** Incorporate labs (e.g., BNP, creatinine), social determinants, and post-discharge events if available.
- **Operational:** Integrate model into EMR/workflow for real-time risk scoring at discharge; automate reports.
- **Validation:** External validation on another health system or time period; sensitivity analyses on cost and effectiveness assumptions.

---

## 📁 Repository Structure

```
├── README.md                    # This file
├── WORKFLOW.md                  # Data cleaning → EDA → modeling → business impact
├── run_all.py                   # Run full pipeline (data → model → reports)
├── requirements.txt             # Python dependencies
│
├── data/                        # data_dictionary.md, sample_data.csv, raw CSVs, readmissions.db
├── scripts/                     # 01_load → 08_dashboard_data.sql, run_all.py
├── notebooks/                   # 01_exploratory_analysis, 02_model_development, 03_financial_analysis
├── outputs/                     # executive_summary, impact_statement, key_findings, CSVs
│   ├── visuals/                 # PNGs (model coefficients, financial dashboard, etc.)
│   └── model/                  # readmission_model.pkl, scaler.pkl, model_metadata.json
├── dashboard/                   # dashboard_design.md, tableau_prompts.md, screenshots
├── docs/                        # methodology, cms_penalty_calculation, roi_analysis
└── tests/                       # test_model.py, test_data_quality.py
```

*You can add `docs/presentation.pptx` manually for stakeholder slides.*

---

## 🔗 GitHub

**Repository:** [https://github.com/DRANI407/Hospital-Readmission-Reduction-Initiative](https://github.com/DRANI407/Hospital-Readmission-Reduction-Initiative)

To push updates from your machine:
```bash
git add .
git commit -m "Your message"
git push origin main
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Install dependencies: `pip install -r requirements.txt`  
  (Optional: `openpyxl` for Excel export; `skl2onnx`, `onnxruntime` for ONNX.)

### Run the full pipeline

From the repository root:

```bash
python run_all.py
```

This runs, in order: data load → cohort SQL → model data prep → logistic regression → financial analysis → dashboard build. Outputs are written to `readmission_project/outputs/` and `readmission_project/data/`.

### Load the model (example)

```python
import joblib
model = joblib.load('outputs/model/readmission_model.pkl')
scaler = joblib.load('outputs/model/scaler.pkl')
# Use scaler.transform(X) then model.predict_proba(X_scaled)[:, 1]
```

Feature list and preprocessing: see `data/data_dictionary.md` and `outputs/model/model_metadata.json`.

### Key outputs to review

- **Executive summary:** `outputs/executive_summary.md`
- **Impact statement:** `outputs/impact_statement.txt`
- **Key findings:** `outputs/key_findings.csv`
- **Dashboards:** `outputs/visuals/`

---

<p align="center">
  <em>Designed as a portfolio-ready healthcare analytics case study.</em><br>
  <em>Data · Modeling · Financial Impact · Actionable Recommendations</em>
</p>
