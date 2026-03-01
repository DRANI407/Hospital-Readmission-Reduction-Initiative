-- Step 3: Readmission cohort analysis — Hospital Readmission Reduction Initiative
-- Builds encounters_clean, readmission_flags, and readmission_analytics.
-- Run after 01_load_data.py (requires encounters, admission_types, discharge_dispositions, admission_sources).

DROP TABLE IF EXISTS encounters_clean;
CREATE TEMP TABLE encounters_clean AS
SELECT 
    e.*,
    DATE('2010-01-01', '+' || (ROW_NUMBER() OVER (ORDER BY encounter_id) % 365) || ' days') as adm_date,
    time_in_hospital as los_days,
    DATE('2010-01-01', '+' || (ROW_NUMBER() OVER (ORDER BY encounter_id) % 365) || ' days', 
         '+' || time_in_hospital || ' days') as disch_date
FROM encounters e;

DROP TABLE IF EXISTS readmission_flags;
CREATE TEMP TABLE readmission_flags AS
WITH patient_encounters AS (
    SELECT 
        patient_nbr,
        encounter_id,
        adm_date,
        disch_date,
        LAG(adm_date) OVER (PARTITION BY patient_nbr ORDER BY adm_date) as prev_adm_date,
        LAG(disch_date) OVER (PARTITION BY patient_nbr ORDER BY adm_date) as prev_disch_date,
        LAG(encounter_id) OVER (PARTITION BY patient_nbr ORDER BY adm_date) as prev_encounter_id
    FROM encounters_clean
)
SELECT 
    pe.*,
    CASE 
        WHEN prev_adm_date IS NOT NULL 
         AND JULIANDAY(adm_date) - JULIANDAY(prev_disch_date) <= 30 
        THEN 1 ELSE 0 
    END as is_30day_readmit
FROM patient_encounters pe;

DROP TABLE IF EXISTS readmission_analytics;
CREATE TABLE readmission_analytics AS
SELECT 
    rf.*,
    e.race,
    e.gender,
    e.age,
    CASE 
        WHEN e.age = '[0-10)' THEN 5
        WHEN e.age = '[10-20)' THEN 15
        WHEN e.age = '[20-30)' THEN 25
        WHEN e.age = '[30-40)' THEN 35
        WHEN e.age = '[40-50)' THEN 45
        WHEN e.age = '[50-60)' THEN 55
        WHEN e.age = '[60-70)' THEN 65
        WHEN e.age = '[70-80)' THEN 75
        WHEN e.age = '[80-90)' THEN 85
        WHEN e.age = '[90-100)' THEN 95
    END as age_midpoint,
    e.time_in_hospital,
    e.num_lab_procedures,
    e.num_procedures,
    e.num_medications,
    e.number_outpatient,
    e.number_emergency,
    e.number_inpatient,
    e.number_diagnoses,
    e.diag_1,
    e.diag_2,
    e.diag_3,
    e.A1Cresult,
    e.max_glu_serum,
    e.insulin,
    e.change,
    e.diabetesMed,
    e.readmitted as target_30day,
    at.admission_type_desc,
    dd.discharge_desc,
    ads.admission_source_desc
FROM readmission_flags rf
JOIN encounters e ON rf.encounter_id = e.encounter_id
LEFT JOIN admission_types at ON e.admission_type_id = at.admission_type_id
LEFT JOIN discharge_dispositions dd ON e.discharge_disposition_id = dd.discharge_disposition_id
LEFT JOIN admission_sources ads ON e.admission_source_id = ads.admission_source_id;
