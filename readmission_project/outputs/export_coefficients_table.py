"""
Export model coefficients to CSV and Excel.
Run from project root: python3 readmission_project/outputs/export_coefficients_table.py
"""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Outputs dir (same folder as this script)
OUT = Path(__file__).resolve().parent
model_path = OUT / 'readmission_model.pkl'

feature_names = [
    'age_midpoint', 'time_in_hospital', 'num_lab_procedures',
    'num_procedures', 'num_medications', 'number_diagnoses',
    'diabetes_complications', 'cardiovascular', 'respiratory', 'renal',
    'high_prior_utilization', 'long_los', 'polypharmacy',
    'a1c_abnormal', 'insulin_level'
]

# Load model
model = joblib.load(model_path)

# Coefficient table
coef_table = pd.DataFrame({
    'Feature': feature_names,
    'Coefficient': model.coef_[0],
    'Odds_Ratio': np.exp(model.coef_[0]),
    'Abs_Coefficient': np.abs(model.coef_[0])
}).sort_values('Abs_Coefficient', ascending=False)

# CSV (always)
csv_path = OUT / 'feature_importance.csv'
coef_table.to_csv(csv_path, index=False)
print(f"✅ CSV saved: {csv_path}")

# Excel (if openpyxl installed)
try:
    import openpyxl  # noqa: F401
    xlsx_path = OUT / 'model_coefficients.xlsx'
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        coef_table.to_excel(writer, sheet_name='Coefficients', index=False)
        summary = pd.DataFrame({
            'Metric': ['Model Type', 'Number of Features', 'Intercept'],
            'Value': ['Logistic Regression', len(feature_names), model.intercept_[0]]
        })
        summary.to_excel(writer, sheet_name='Model Info', index=False)
    print(f"✅ Excel saved: {xlsx_path}")
except ImportError:
    print("   (Install openpyxl for Excel: pip install openpyxl)")
