"""
Export readmission model coefficients and metadata to JSON.
Use for documentation, simple APIs, or reimplementing the model in other languages.
"""
import json
import joblib
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parent
model = joblib.load(OUT / 'readmission_model.pkl')
scaler = joblib.load(OUT / 'scaler.pkl')

FEATURE_COLS = [
    'age_midpoint', 'time_in_hospital', 'num_lab_procedures',
    'num_procedures', 'num_medications', 'number_diagnoses',
    'diabetes_complications', 'cardiovascular', 'respiratory', 'renal',
    'high_prior_utilization', 'long_los', 'polypharmacy',
    'a1c_abnormal', 'insulin_level'
]

payload = {
    "model_type": "LogisticRegression",
    "n_features": len(FEATURE_COLS),
    "feature_names": FEATURE_COLS,
    "intercept": float(model.intercept_[0]),
    "coefficients": {f: float(c) for f, c in zip(FEATURE_COLS, model.coef_[0])},
    "odds_ratios": {f: float(np.exp(c)) for f, c in zip(FEATURE_COLS, model.coef_[0])},
    "scaler_mean": {f: float(m) for f, m in zip(FEATURE_COLS, scaler.mean_)},
    "scaler_scale": {f: float(s) for f, s in zip(FEATURE_COLS, scaler.scale_)},
}

out_path = OUT / 'readmission_model_export.json'
with open(out_path, 'w') as f:
    json.dump(payload, f, indent=2)
print(f"Exported to {out_path}")
