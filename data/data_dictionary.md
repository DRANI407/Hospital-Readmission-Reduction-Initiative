# Data Dictionary — Hospital Readmission Reduction Initiative

## Source: Diabetes 130-US Hospitals Dataset (UCI)

---

## Raw encounter-level data (`diabetic_data.csv`)

| Field | Type | Description |
|-------|------|-------------|
| encounter_id | int | Unique encounter identifier |
| patient_nbr | int | Unique patient identifier (anonymized) |
| race | str | Race (Caucasian, AfricanAmerican, Asian, Hispanic, Other, ?) |
| gender | str | Male, Female |
| age | str | Age band (e.g. [0-10), [10-20), ..., [90-100)) |
| admission_type_id | int | 1=Emergency, 2=Urgent, 3=Elective, etc. |
| discharge_disposition_id | int | Discharge destination (home, transfer, etc.) |
| admission_source_id | int | Source (ER, referral, transfer, etc.) |
| time_in_hospital | int | Length of stay (days) |
| num_lab_procedures | int | Number of lab procedures |
| num_procedures | int | Number of procedures |
| num_medications | int | Number of medications |
| number_outpatient | int | Number of outpatient visits (prior year) |
| number_emergency | int | Number of emergency visits (prior year) |
| number_inpatient | int | Number of inpatient visits (prior year) |
| number_diagnoses | int | Number of diagnoses |
| diag_1, diag_2, diag_3 | str | Primary/secondary/tertiary diagnosis (ICD-9) |
| max_glu_serum | str | Max glucose serum (None, Norm, >200, >300) |
| A1Cresult | str | A1C result (None, Norm, >7, >8) |
| insulin | str | Insulin (No, Down, Steady, Up) |
| change | str | Diabetes medication change (Ch, No) |
| diabetesMed | str | Diabetes medication (Yes, No) |
| readmitted | str | 30-day readmission (NO, <30, >30) — used to derive target |

---

## Model-ready features (after pipeline)

| Field | Type | Description |
|-------|------|-------------|
| target | int | 30-day readmission (1=yes, 0=no) |
| age_midpoint | int | Midpoint of age band (5, 15, …, 95) |
| time_in_hospital | int | Length of stay (days) |
| num_lab_procedures | int | Number of lab procedures |
| num_procedures | int | Number of procedures |
| num_medications | int | Number of medications |
| number_diagnoses | int | Number of diagnoses |
| diabetes_complications | 0/1 | ICD-9 250.4x–250.9x present |
| cardiovascular | 0/1 | ICD-9 410–414, 428–429, 401–405 |
| respiratory | 0/1 | Respiratory diagnosis codes |
| renal | 0/1 | ICD-9 584–590 |
| high_prior_utilization | 0/1 | inpatient>1 OR emergency>2 OR outpatient>5 |
| long_los | 0/1 | time_in_hospital > 7 |
| polypharmacy | 0/1 | num_medications > 15 |
| a1c_abnormal | 0/1 | A1C >7 or >8 |
| insulin_level | 0–3 | No=0, Down=1, Steady=2, Up=3 |

---

## Mapping files

- **IDS_mapping.csv** — Descriptions for admission_type_id, discharge_disposition_id, admission_source_id (see load script for full mapping).
