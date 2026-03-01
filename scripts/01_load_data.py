"""
Step 1: Data Load — Hospital Readmission Reduction Initiative

Loads raw CSV sources (diabetic_data.csv, IDS_mapping.csv) into a SQLite database
(readmissions.db) with normalized tables for encounters, admission types,
discharge dispositions, and admission sources. Required before running
cohort SQL and model data preparation.

Output: readmission_project/data/readmissions.db
"""
import pandas as pd
import sqlite3
import numpy as np
from pathlib import Path

# Resolve data path (data lives in readmission_project/data/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'readmission_project' / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Create database connection
conn = sqlite3.connect(DATA_DIR / 'readmissions.db')

# Load main dataset
print("Loading diabetic_data.csv...")
df_main = pd.read_csv(DATA_DIR / 'diabetic_data.csv')

# Load mapping file
print("Loading IDS_mapping.csv...")
with open(DATA_DIR / 'IDS_mapping.csv', 'r') as f:
    content = f.read()

# Parse the mapping file (it's a bit messy with multiple sections)
sections = content.strip().split(',\n\n')
    
# Create separate mapping dataframes
admission_map = pd.DataFrame({
    'admission_type_id': ['1','2','3','4','5','6','7','8'],
    'admission_type_desc': ['Emergency','Urgent','Elective','Newborn','Not Available',
                           'NULL','Trauma Center','Not Mapped']
})

discharge_map = pd.DataFrame({
    'discharge_disposition_id': [str(i) for i in range(1,31) if i != 29] + ['29'],
    'discharge_desc': [
        'Discharged to home','Transferred to short term hospital','Transferred to SNF',
        'Transferred to ICF','Transferred to other inpatient care','Home with home health service',
        'Left AMA','Home under Home IV provider','Admitted as inpatient','Neonate discharged',
        'Expired','Still patient','Hospice/home','Hospice/medical facility',
        'Transferred to swing bed','Transferred/referred for outpatient services',
        'Referred to this institution for outpatient','NULL',
        'Expired at home (Medicaid hospice)','Expired in medical facility (Medicaid hospice)',
        'Expired place unknown (Medicaid hospice)','Transferred to rehab facility',
        'Transferred to long term care hospital','Transferred to nursing facility (Medicaid only)',
        'Not Mapped','Unknown/Invalid',
        'Transferred to federal health care facility',
        'Transferred to psychiatric hospital','Transferred to Critical Access Hospital',
        'Discharged/transferred to other health care institution'
    ]
})

source_map = pd.DataFrame({
    'admission_source_id': [str(i) for i in range(1,26)],
    'admission_source_desc': [
        'Physician Referral','Clinic Referral','HMO Referral','Transfer from hospital',
        'Transfer from SNF','Transfer from other facility','Emergency Room',
        'Court/Law Enforcement','Not Available','Transfer from critical access hospital',
        'Normal Delivery','Premature Delivery','Sick Baby','Extramural Birth',
        'Not Available','NULL','Transfer from home health agency',
        'Readmission to same home health agency','Not Mapped','Unknown/Invalid',
        'Transfer from hospital inpatient/same facility','Born inside hospital',
        'Born outside hospital','Transfer from Ambulatory Surgery Center',
        'Transfer from Hospice'
    ]
})

# Save to database
df_main.to_sql('encounters', conn, if_exists='replace', index=False)
admission_map.to_sql('admission_types', conn, if_exists='replace', index=False)
discharge_map.to_sql('discharge_dispositions', conn, if_exists='replace', index=False)
source_map.to_sql('admission_sources', conn, if_exists='replace', index=False)

print("Data loaded successfully!")
conn.close()
