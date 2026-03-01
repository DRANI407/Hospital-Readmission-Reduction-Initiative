"""
05_prepare_model_data.py — Feature engineering and train/test split.
Requires 01_load_data.py and 03_readmission_cohorts.sql. Outputs to data/.
"""
import pandas as pd
import sqlite3
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

conn = sqlite3.connect(DATA_DIR / 'readmissions.db')
query = """
SELECT 
    encounter_id, patient_nbr, is_30day_readmit as target,
    age_midpoint, time_in_hospital, num_lab_procedures, num_procedures,
    num_medications, number_outpatient, number_emergency, number_inpatient,
    number_diagnoses, admission_type_desc, discharge_desc, admission_source_desc,
    race, gender, A1Cresult, max_glu_serum, insulin, change, diabetesMed,
    diag_1, diag_2
FROM readmission_analytics
WHERE age IS NOT NULL AND race != '?' AND gender IN ('Male', 'Female')
"""
df = pd.read_sql_query(query, conn)
conn.close()

df['age_group'] = pd.cut(df['age_midpoint'], bins=[0, 30, 50, 65, 80, 100], labels=['<30', '30-49', '50-64', '65-79', '80+'])
diag1_str = df['diag_1'].fillna('').astype(str)
df['diabetes_complications'] = ((diag1_str.str.startswith('250')) & (diag1_str.str.len() >= 5) & (diag1_str.str[4].isin(['4','5','6','7','8','9']))).astype(int)
cardio_codes = ['410', '411', '412', '413', '414', '428', '429', '401', '402', '403', '404', '405']
df['cardiovascular'] = diag1_str.str[:3].isin(cardio_codes).astype(int)
resp_codes = ['466', '480', '481', '482', '483', '484', '485', '486', '487', '490', '491', '492', '493', '494', '496']
df['respiratory'] = diag1_str.str[:3].isin(resp_codes).astype(int)
renal_codes = ['584', '585', '586', '587', '588', '589', '590']
df['renal'] = diag1_str.str[:3].isin(renal_codes).astype(int)
df['high_prior_utilization'] = ((df['number_inpatient'] > 1) | (df['number_emergency'] > 2) | (df['number_outpatient'] > 5)).astype(int)
df['long_los'] = (df['time_in_hospital'] > 7).astype(int)
df['polypharmacy'] = (df['num_medications'] > 15).astype(int)
df['a1c_abnormal'] = df['A1Cresult'].apply(lambda x: 1 if x in ['>7', '>8'] else 0 if x == 'None' else np.nan)
df['insulin_level'] = df['insulin'].map({'No': 0, 'Down': 1, 'Steady': 2, 'Up': 3})

df.to_csv(DATA_DIR / 'model_ready_data.csv', index=False)

feature_cols = [
    'age_midpoint', 'time_in_hospital', 'num_lab_procedures', 'num_procedures',
    'num_medications', 'number_diagnoses', 'diabetes_complications', 'cardiovascular',
    'respiratory', 'renal', 'high_prior_utilization', 'long_los', 'polypharmacy',
    'a1c_abnormal', 'insulin_level'
]
model_df = df[feature_cols + ['target']].dropna()
X = model_df[feature_cols]
y = model_df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

X_train.to_csv(DATA_DIR / 'X_train.csv', index=False)
X_test.to_csv(DATA_DIR / 'X_test.csv', index=False)
y_train.to_csv(DATA_DIR / 'y_train.csv', index=False)
y_test.to_csv(DATA_DIR / 'y_test.csv', index=False)
print(f"Saved model_ready_data.csv and train/test splits to {DATA_DIR}")
