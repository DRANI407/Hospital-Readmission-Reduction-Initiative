"""
Step 2b: Model Data Preparation — Hospital Readmission Reduction Initiative

Reads the readmission_analytics view from SQLite, applies filters (non-null age,
known race/gender), and engineers 15 features (comorbidities, utilization,
polypharmacy, A1C, insulin). Outputs model_ready_data.csv and train/test splits
for logistic regression. Requires 01_load_data.py and 02_readmission_cohorts.sql
to have been run first.

Outputs: readmission_project/data/model_ready_data.csv, X_train/test, y_train/test
"""
import pandas as pd
import sqlite3
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

# Resolve data path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'readmission_project' / 'data'

# Connect to database
conn = sqlite3.connect(DATA_DIR / 'readmissions.db')

# Load analytics table
query = """
SELECT 
    encounter_id,
    patient_nbr,
    is_30day_readmit as target,
    age_midpoint,
    time_in_hospital,
    num_lab_procedures,
    num_procedures,
    num_medications,
    number_outpatient,
    number_emergency,
    number_inpatient,
    number_diagnoses,
    admission_type_desc,
    discharge_desc,
    admission_source_desc,
    race,
    gender,
    A1Cresult,
    max_glu_serum,
    insulin,
    change,
    diabetesMed,
    diag_1,
    diag_2
FROM readmission_analytics
WHERE age IS NOT NULL
  AND race != '?'
  AND gender IN ('Male', 'Female')
"""
df = pd.read_sql_query(query, conn)
conn.close()

print(f"Loaded {len(df)} encounters with {df['target'].sum()} readmissions")
print(f"Readmission rate: {df['target'].mean():.2%}")

# Feature engineering
print("\n--- Engineering Features ---")

# Create age groups
df['age_group'] = pd.cut(df['age_midpoint'], 
                          bins=[0, 30, 50, 65, 80, 100], 
                          labels=['<30', '30-49', '50-64', '65-79', '80+'])

# Flag for diabetes complications (250.4-250.9) - vectorized
diag1_str = df['diag_1'].fillna('').astype(str)
df['diabetes_complications'] = (
    (diag1_str.str.startswith('250')) & 
    (diag1_str.str.len() >= 5) & 
    (diag1_str.str[4].isin(['4','5','6','7','8','9']))
).astype(int)

# Flag for cardiovascular conditions - vectorized
cardio_codes = ['410', '411', '412', '413', '414', '428', '429', '401', '402', '403', '404', '405']
df['cardiovascular'] = diag1_str.str[:3].isin(cardio_codes).astype(int)

# Flag for respiratory conditions - vectorized
resp_codes = ['466', '480', '481', '482', '483', '484', '485', '486', '487', '490', '491', '492', '493', '494', '496']
df['respiratory'] = diag1_str.str[:3].isin(resp_codes).astype(int)

# Flag for renal conditions - vectorized
renal_codes = ['584', '585', '586', '587', '588', '589', '590']
df['renal'] = diag1_str.str[:3].isin(renal_codes).astype(int)

# Flag for prior healthcare utilization
df['high_prior_utilization'] = ((df['number_inpatient'] > 1) | 
                                 (df['number_emergency'] > 2) | 
                                 (df['number_outpatient'] > 5)).astype(int)

# Flag for long LOS
df['long_los'] = (df['time_in_hospital'] > 7).astype(int)

# Flag for polypharmacy
df['polypharmacy'] = (df['num_medications'] > 15).astype(int)

# Convert A1C result to categorical
df['a1c_abnormal'] = df['A1Cresult'].apply(
    lambda x: 1 if x in ['>7', '>8'] else 0 if x == 'None' else np.nan
)

# Convert insulin to ordered categories
insulin_map = {'No': 0, 'Down': 1, 'Steady': 2, 'Up': 3}
df['insulin_level'] = df['insulin'].map(insulin_map)

# Save processed data
df.to_csv(DATA_DIR / 'model_ready_data.csv', index=False)
print("Saved model-ready data to data/model_ready_data.csv")

# Prepare for modeling - select features
feature_cols = [
    'age_midpoint', 'time_in_hospital', 'num_lab_procedures', 
    'num_procedures', 'num_medications', 'number_diagnoses',
    'diabetes_complications', 'cardiovascular', 'respiratory', 'renal',
    'high_prior_utilization', 'long_los', 'polypharmacy',
    'a1c_abnormal', 'insulin_level'
]

# Drop rows with missing values
model_df = df[feature_cols + ['target']].dropna()

print(f"\nFinal modeling dataset: {len(model_df)} rows")
print(f"Features: {feature_cols}")
print(f"Target distribution: {model_df['target'].value_counts().to_dict()}")

# Split data
X = model_df[feature_cols]
y = model_df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"\nTrain set: {len(X_train)} rows, Test set: {len(X_test)} rows")
print(f"Train readmission rate: {y_train.mean():.2%}")
print(f"Test readmission rate: {y_test.mean():.2%}")

# Save splits
X_train.to_csv(DATA_DIR / 'X_train.csv', index=False)
X_test.to_csv(DATA_DIR / 'X_test.csv', index=False)
y_train.to_csv(DATA_DIR / 'y_train.csv', index=False)
y_test.to_csv(DATA_DIR / 'y_test.csv', index=False)
print("\nSaved train/test splits to data/")
