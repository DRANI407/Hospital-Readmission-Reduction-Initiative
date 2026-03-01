"""
Load readmission_model.pkl and print its contents in a readable format.
Run from project root: python3 readmission_project/outputs/display_model_contents.py
"""
import joblib
import numpy as np
from pathlib import Path

# Paths (run from project root)
OUT = Path('readmission_project/outputs')
model = joblib.load(OUT / 'readmission_model.pkl')
scaler = joblib.load(OUT / 'scaler.pkl')

# Feature names: use model's if available (sklearn 1.0+), else known list
FEATURE_NAMES = [
    'age_midpoint', 'time_in_hospital', 'num_lab_procedures',
    'num_procedures', 'num_medications', 'number_diagnoses',
    'diabetes_complications', 'cardiovascular', 'respiratory', 'renal',
    'high_prior_utilization', 'long_los', 'polypharmacy',
    'a1c_abnormal', 'insulin_level'
]
if hasattr(model, 'feature_names_in_') and model.feature_names_in_ is not None:
    feature_names = list(model.feature_names_in_)
else:
    feature_names = FEATURE_NAMES

coef = model.coef_[0]
intercept = float(model.intercept_[0])
odds_ratios = np.exp(coef)

# --- Readable output ---
print("=" * 60)
print("READMISSION MODEL — READABLE CONTENTS")
print("=" * 60)

print("\n--- Model ---")
print(f"  Type:        {type(model).__name__}")
print(f"  Penalty:     {model.penalty}")
print(f"  C:           {model.C}")
print(f"  Class weight: {model.class_weight}")
print(f"  Solver:      {model.solver}")
print(f"  Max iterations: {model.max_iter}")
print(f"  Classes:     {model.classes_}")

print("\n--- Intercept ---")
print(f"  {intercept:.6f}  (log-odds when all features at mean)")

print("\n--- Coefficients (log-odds per 1 SD) & Odds Ratios ---")
print("-" * 60)
print(f"  {'Feature':<28} {'Coefficient':>12} {'Odds Ratio':>10}")
print("-" * 60)
for name, c, or_val in zip(feature_names, coef, odds_ratios):
    print(f"  {name:<28} {c:>12.4f} {or_val:>10.4f}")
print("-" * 60)

print("\n--- Scaler (StandardScaler) ---")
print(f"  Mean (per feature):  {scaler.mean_.round(4).tolist()}")
print(f"  Scale (per feature): {scaler.scale_.round(4).tolist()}")

print("\n--- Summary ---")
print(f"  Number of features: {len(feature_names)}")
print(f"  Coefficient shape:  {model.coef_.shape}")
print("=" * 60)
