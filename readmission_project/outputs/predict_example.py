"""
Example: load model and scaler, then predict on new patient data.
Ensure new data has the same 15 features and encoding as in MODEL_CARD.md.
"""
import joblib
import pandas as pd
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


def predict_readmission_risk(X: pd.DataFrame) -> pd.DataFrame:
    """X must have columns FEATURE_COLS. Returns DataFrame with prob and class."""
    X = X[FEATURE_COLS]
    X_scaled = scaler.transform(X)
    prob = model.predict_proba(X_scaled)[:, 1]
    pred = model.predict(X_scaled)
    return pd.DataFrame({
        'prob_readmission': prob,
        'predicted_readmission': pred.astype(int)
    })


if __name__ == '__main__':
    # Example: one patient (values are illustrative)
    one_patient = pd.DataFrame([{
        'age_midpoint': 55,
        'time_in_hospital': 4,
        'num_lab_procedures': 40,
        'num_procedures': 2,
        'num_medications': 12,
        'number_diagnoses': 9,
        'diabetes_complications': 1,
        'cardiovascular': 1,
        'respiratory': 0,
        'renal': 0,
        'high_prior_utilization': 1,
        'long_los': 0,
        'polypharmacy': 0,
        'a1c_abnormal': 1,
        'insulin_level': 2,
    }])
    result = predict_readmission_risk(one_patient)
    print(result)
    print("Interpret: prob_readmission = P(30-day readmission); use risk tiers (e.g. High if > 0.5).")
