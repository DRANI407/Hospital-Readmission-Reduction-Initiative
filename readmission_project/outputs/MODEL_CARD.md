# Readmission Prediction Model — Model Card

---

## 📋 MODEL SUMMARY

| Attribute | Value |
|-----------|--------|
| **Model architecture** | Logistic Regression (binary classifier) |
| **Implementation** | `sklearn.linear_model.LogisticRegression` |
| **Hyperparameters** | `C=1.0`, `class_weight='balanced'`, `penalty='l2'`, `max_iter=1000`, `random_state=42` |
| **Training features** | 15 (list below) |
| **Training samples** | 8,768 encounters |
| **Test samples** | 2,923 encounters |
| **Target** | `is_30day_readmit` (1 = readmitted within 30 days, 0 = not) |
| **Preprocessing** | StandardScaler (zero mean, unit variance) fitted on training data |

### Feature list (order matters for prediction)

1. `age_midpoint` — Age band midpoint (5, 15, …, 95)  
2. `time_in_hospital` — Length of stay (days)  
3. `num_lab_procedures` — Number of lab procedures  
4. `num_procedures` — Number of procedures  
5. `num_medications` — Number of medications  
6. `number_diagnoses` — Number of diagnoses  
7. `diabetes_complications` — 0/1 (ICD-9 250.4x–250.9x)  
8. `cardiovascular` — 0/1 (ICD-9 410–414, 428–429, 401–405)  
9. `respiratory` — 0/1 (ICD-9 respiratory codes)  
10. `renal` — 0/1 (ICD-9 584–590)  
11. `high_prior_utilization` — 0/1 (inpatient>1 OR emergency>2 OR outpatient>5)  
12. `long_los` — 0/1 (time_in_hospital > 7)  
13. `polypharmacy` — 0/1 (num_medications > 15)  
14. `a1c_abnormal` — 0/1 (>7 or >8); 0 if None  
15. `insulin_level` — 0=No, 1=Down, 2=Steady, 3=Up  

---

## 📊 FEATURE IMPORTANCE

**Coefficients** are log-odds per 1 standard deviation increase (features are standardized). **Odds ratio** = exp(coef); OR > 1 → higher readmission odds.

### Top 10 risk factors (by |coefficient|)

| Rank | Feature | Coefficient | Odds ratio | Clinical interpretation |
|------|---------|-------------|------------|---------------------------|
| 1 | high_prior_utilization | +0.516 | 1.68 | Prior high use (ED/inpatient/outpatient) strongly increases 30-day readmission odds. |
| 2 | number_diagnoses | +0.306 | 1.36 | More diagnoses (comorbidity burden) → higher readmission risk. |
| 3 | num_procedures | -0.183 | 0.83 | More procedures in stay → slightly lower readmission (possible confounding: elective/complex cases). |
| 4 | polypharmacy | +0.157 | 1.17 | >15 medications at discharge → higher readmission risk. |
| 5 | time_in_hospital | +0.117 | 1.12 | Longer stay → higher readmission odds. |
| 6 | age_midpoint | -0.110 | 0.90 | Older age (in this cohort) associated with slightly lower readmission (after adjusting for other factors). |
| 7 | num_lab_procedures | -0.109 | 0.90 | More labs → slightly lower readmission (may reflect care intensity). |
| 8 | num_medications | -0.108 | 0.90 | In presence of polypharmacy flag, raw count has a small negative association. |
| 9 | insulin_level | +0.096 | 1.10 | Higher insulin use (Up/Steady) → higher readmission risk. |
| 10 | diabetes_complications | +0.076 | 1.08 | Diabetes with complications (250.4x–250.9x) → higher risk. |

### Other features

| Feature | Coef | OR | Interpretation |
|---------|------|-----|-----------------|
| cardiovascular | +0.057 | 1.06 | Cardiovascular comorbidity increases risk. |
| renal | +0.050 | 1.05 | Renal comorbidity increases risk. |
| respiratory | +0.025 | 1.03 | Respiratory comorbidity slight increase. |
| long_los | +0.012 | 1.01 | LOS > 7 days flag adds small extra risk. |
| a1c_abnormal | ~0 | 1.00 | In this model, minimal additional effect beyond other features. |

**Intercept:** -0.218 (log-odds when all features are at mean; corresponds to baseline probability ~0.45 on standardized scale).

---

## 🎯 HOW TO USE

### 1. Load model and scaler

```python
import joblib
from pathlib import Path

MODEL_DIR = Path('readmission_project/outputs')
model = joblib.load(MODEL_DIR / 'readmission_model.pkl')
scaler = joblib.load(MODEL_DIR / 'scaler.pkl')
```

### 2. Feature order and preprocessing

New data must have the **same 15 features**, in this **exact order**, and same encoding:

- **Numeric:** age_midpoint, time_in_hospital, num_lab_procedures, num_procedures, num_medications, number_diagnoses  
- **Binary 0/1:** diabetes_complications, cardiovascular, respiratory, renal, high_prior_utilization, long_los, polypharmacy, a1c_abnormal  
- **Categorical 0–3:** insulin_level (No=0, Down=1, Steady=2, Up=3)  

Then apply the **same scaler** used in training (do not refit):

```python
import pandas as pd

FEATURE_COLS = [
    'age_midpoint', 'time_in_hospital', 'num_lab_procedures',
    'num_procedures', 'num_medications', 'number_diagnoses',
    'diabetes_complications', 'cardiovascular', 'respiratory', 'renal',
    'high_prior_utilization', 'long_los', 'polypharmacy',
    'a1c_abnormal', 'insulin_level'
]

# One or more rows
X_new = pd.DataFrame([[...]], columns=FEATURE_COLS)
X_new_scaled = scaler.transform(X_new)
```

### 3. Predict

```python
# Probability of 30-day readmission
prob_readmit = model.predict_proba(X_new_scaled)[:, 1]

# Binary prediction (0 or 1)
pred_class = model.predict(X_new_scaled)
```

### 4. How to interpret

- **prob_readmit** (e.g. 0.15): estimated probability of readmission within 30 days.  
- **pred_class**: 1 = predicted readmission, 0 = predicted no readmission (default 0.5 threshold).  
- For **risk tiers**, use probability, e.g. Low &lt; 0.2, Medium 0.2–0.5, High &gt; 0.5.  
- In training, **ROC-AUC ≈ 0.71**; use for ranking risk rather than as a definitive outcome predictor.

---

## 💾 SAVE OPTIONS

### Current format (joblib)

- **Files:** `readmission_model.pkl`, `scaler.pkl`  
- **Load:** `joblib.load(path)`  
- **Use case:** Python services, notebooks, same environment as training.

### 1. JSON (coefficients + metadata)

Good for documentation, simple APIs, or non-Python runtimes. Only stores coefficients and intercept (linear model); preprocessing (scaler, feature order) must be implemented separately.

See script: `readmission_project/outputs/export_model_json.py`

### 2. ONNX

Good for production deployment across languages/frameworks. Requires `skl2onnx` and `onnxruntime`.

```bash
pip install skl2onnx onnxruntime
```

See script: `readmission_project/outputs/export_model_onnx.py`

### 3. Production checklist

- **Versioning:** Store model + scaler with a version tag (e.g. date or git commit).  
- **Feature contract:** Document and validate the 15 features and allowed ranges.  
- **Scaler:** Always use the saved scaler; never refit on production data.  
- **Monitoring:** Log inputs, predictions, and (when available) outcomes for drift and performance.

---

*Generated from `readmission_model.pkl` and training pipeline (scripts 02_prepare_model_data.py, 03_logistic_regression.py).*
