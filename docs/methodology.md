# Methodology — Hospital Readmission Reduction Initiative

## 1. Data sources and cohort

- **Source:** Diabetes 130-US hospitals dataset (UCI); encounter-level data with demographics, diagnoses (ICD-9), procedures, medications, and prior utilization.
- **Cohort:** All encounters with valid age, known race/gender; 30-day readmission flag derived from discharge and next admission date (≤30 days).
- **Database:** Raw CSVs loaded into SQLite (`data/readmissions.db`); cohort and analytics view built via `scripts/03_readmission_cohorts.sql`.

## 2. Feature engineering

- **Demographic:** Age band midpoint (5, 15, …, 95).
- **Clinical:** Time in hospital, num_lab_procedures, num_procedures, num_medications, number_diagnoses.
- **Comorbidities (ICD-9):** Diabetes complications (250.4x–250.9x), cardiovascular, respiratory, renal.
- **Utilization:** High prior utilization (inpatient>1 or emergency>2 or outpatient>5), long LOS (>7 days), polypharmacy (>15 medications).
- **Diabetes:** A1C abnormal (>7 or >8), insulin level (No/Down/Steady/Up → 0–3).

## 3. Modeling

- **Algorithm:** Logistic regression (L2, balanced class weight, max_iter=1000).
- **Preprocessing:** StandardScaler on training data; same scaler applied at prediction time.
- **Train/test:** 75/25 stratified split; metrics: ROC-AUC, sensitivity, specificity, PPV, NPV.
- **Output:** Coefficients, odds ratios, risk quartiles; model and scaler saved to `outputs/model/`.

## 4. Financial and ROI

- **Cost:** $15,000 per readmission (moderate scenario); total cost by diagnosis and age.
- **CMS HRRP:** National benchmark 15.5%; penalty logic applied if rate exceeds benchmark.
- **Intervention:** Transitional care at $750/patient; ROI for coverage × effectiveness scenarios (e.g. 50% high-risk, 15% reduction → net benefit, ROI %).

## 5. Execution order

Run `python scripts/run_all.py` from repo root: 01 load → 03 cohorts SQL → 02 explore SQL → 04 risk factor SQL → 05 prepare → 06 model → 07 financial → 08 dashboard SQL.
