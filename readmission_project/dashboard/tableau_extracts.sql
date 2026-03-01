-- =============================================================================
-- TABLEAU DASHBOARD EXTRACTS
-- Run against readmission_project/data/readmissions.db
-- Export results as CSV or connect Tableau directly to SQLite
-- =============================================================================

-- Parameters (use as Tableau parameters or in calculated fields)
-- National benchmark: 0.155 (15.5%)
-- Cost per readmission: 15000
-- CMS penalty base: 0.03

-- =============================================================================
-- SHEET 1: KPI CARDS
-- =============================================================================
SELECT 
    (SELECT COUNT(*) FROM readmission_analytics) as total_encounters,
    (SELECT ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) 
     FROM readmission_analytics) as readmission_rate_pct,
    0.155 as national_benchmark_pct,
    (SELECT SUM(is_30day_readmit) * 15000 FROM readmission_analytics) as estimated_cost,
    0 as cms_penalty_exposure;  -- Replace with actual penalty calc if > benchmark


-- Alternative: One row per KPI for easier Tableau use
-- KPI_CARDS extract (pivot in Tableau or use as separate data source)
SELECT 'Total Encounters' as kpi_name, 
       CAST(COUNT(*) AS REAL) as value, 
       NULL as benchmark 
FROM readmission_analytics
UNION ALL
SELECT 'Readmission Rate %', 
       ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2), 
       15.5 
FROM readmission_analytics
UNION ALL
SELECT 'Est. Cost of Readmissions', 
       SUM(is_30day_readmit) * 15000, 
       NULL 
FROM readmission_analytics
UNION ALL
SELECT 'CMS Penalty Exposure', 
       0,  -- Update if above benchmark
       NULL 
FROM readmission_analytics;


-- =============================================================================
-- SHEET 2: READMISSION TREND LINE
-- =============================================================================
SELECT 
    strftime('%Y-%m', adm_date) as month,
    strftime('%Y-%m-01', adm_date) as month_date,  -- For proper sorting
    COUNT(*) as encounters,
    SUM(is_30day_readmit) as readmissions,
    ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) as readmission_rate,
    15.5 as national_benchmark,
    CASE WHEN 100.0 * SUM(is_30day_readmit) / COUNT(*) > 15.5 THEN 'Above' ELSE 'Below' END as benchmark_status
FROM readmission_analytics
GROUP BY month, month_date
ORDER BY month_date;


-- =============================================================================
-- SHEET 3: RISK FACTOR HEAT MAP (Age x Medications)
-- =============================================================================
SELECT 
    age,
    CASE 
        WHEN num_medications <= 5 THEN '0-5'
        WHEN num_medications <= 10 THEN '6-10'
        WHEN num_medications <= 15 THEN '11-15'
        WHEN num_medications <= 20 THEN '16-20'
        ELSE '21+'
    END as medication_category,
    COUNT(*) as encounter_count,
    SUM(is_30day_readmit) as readmission_count,
    ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) as readmission_rate
FROM readmission_analytics
GROUP BY age, medication_category
ORDER BY age, medication_category;


-- =============================================================================
-- SHEET 4: DIAGNOSIS IMPACT (Top 10 by Cost)
-- =============================================================================
WITH diag_cat AS (
    SELECT *,
        CASE 
            WHEN substr(COALESCE(diag_1,''),1,3) IN ('250') OR diag_1 LIKE '250%' THEN 'Diabetes'
            WHEN substr(COALESCE(diag_1,''),1,3) IN ('428','402','404') THEN 'Heart Failure'
            WHEN substr(COALESCE(diag_1,''),1,3) IN ('410','411','412','413','414') THEN 'CAD'
            WHEN substr(COALESCE(diag_1,''),1,3) IN ('491','492','493','496') THEN 'COPD'
            WHEN substr(COALESCE(diag_1,''),1,3) IN ('486','481','482') THEN 'Pneumonia'
            WHEN diag_1 IS NULL OR diag_1 = '?' THEN 'Unknown'
            ELSE 'Other'
        END as diag_category
    FROM readmission_analytics
    WHERE diag_1 IS NOT NULL AND diag_1 != '?' AND length(diag_1) >= 3
),
diag_summary AS (
    SELECT 
        substr(diag_1, 1, 3) as diag_code,
        diag_category,
        COUNT(*) as encounters,
        SUM(is_30day_readmit) as readmissions,
        ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) as readmission_rate,
        SUM(is_30day_readmit) * 15000 as total_cost
    FROM diag_cat
    GROUP BY diag_code, diag_category
)
SELECT * FROM diag_summary
ORDER BY total_cost DESC
LIMIT 10;


-- =============================================================================
-- SHEET 5: GEOGRAPHIC/PROVIDER VARIATION
-- (Data not available - use hospital_id or encounter_id aggregation if present)
-- Placeholder: Readmission rate by admission_type as proxy for "variation"
-- =============================================================================
SELECT 
    admission_type_desc as segment,
    COUNT(*) as encounters,
    SUM(is_30day_readmit) as readmissions,
    ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) as readmission_rate
FROM readmission_analytics
GROUP BY admission_type_desc
ORDER BY readmission_rate DESC;


-- =============================================================================
-- SHEET 6: INTERVENTION ROI SIMULATOR (Base data for parameter-driven calc)
-- Use Tableau Parameters: Coverage %, Effectiveness %, Cost per intervention
-- =============================================================================
WITH risk_data AS (
    SELECT 
        (num_medications > 15)*2 + (time_in_hospital > 7)*2.5 +
        (CASE WHEN number_inpatient > 1 OR number_emergency > 2 OR number_outpatient > 5 THEN 3 ELSE 0 END) +
        (CASE WHEN diag_1 LIKE '250.%' AND length(diag_1) >= 5 AND substr(diag_1,5,1) IN ('4','5','6','7','8','9') THEN 1.5 ELSE 0 END) +
        (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('410','411','412','414','428','429','401','402','403','404','405') THEN 2 ELSE 0 END) +
        (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('584','585','586','587','588','589','590') THEN 2 ELSE 0 END) as risk_score,
        is_30day_readmit
    FROM readmission_analytics
),
risk_segments AS (
    SELECT 
        CASE WHEN risk_score < 2 THEN 'Low' WHEN risk_score < 4 THEN 'Medium' 
             WHEN risk_score < 6 THEN 'High' ELSE 'Very High' END as risk_level,
        COUNT(*) as patients,
        SUM(is_30day_readmit) as readmissions,
        ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) as rate
    FROM risk_data
    GROUP BY risk_level
)
SELECT * FROM risk_segments;


-- Pre-calculated ROI scenarios (for quick display)
WITH risk_base AS (
    SELECT 
        CASE 
            WHEN ((num_medications > 15)*2 + (time_in_hospital > 7)*2.5 +
                  (CASE WHEN number_inpatient > 1 OR number_emergency > 2 OR number_outpatient > 5 THEN 3 ELSE 0 END) +
                  (CASE WHEN diag_1 LIKE '250.%' AND length(diag_1) >= 5 AND substr(diag_1,5,1) IN ('4','5','6','7','8','9') THEN 1.5 ELSE 0 END) +
                  (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('410','411','412','414','428','429','401','402','403','404','405') THEN 2 ELSE 0 END) +
                  (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('584','585','586','587','588','589','590') THEN 2 ELSE 0 END)) < 2 THEN 'Low'
            WHEN ((num_medications > 15)*2 + (time_in_hospital > 7)*2.5 +
                  (CASE WHEN number_inpatient > 1 OR number_emergency > 2 OR number_outpatient > 5 THEN 3 ELSE 0 END) +
                  (CASE WHEN diag_1 LIKE '250.%' AND length(diag_1) >= 5 AND substr(diag_1,5,1) IN ('4','5','6','7','8','9') THEN 1.5 ELSE 0 END) +
                  (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('410','411','412','414','428','429','401','402','403','404','405') THEN 2 ELSE 0 END) +
                  (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('584','585','586','587','588','589','590') THEN 2 ELSE 0 END)) < 4 THEN 'Medium'
            WHEN ((num_medications > 15)*2 + (time_in_hospital > 7)*2.5 +
                  (CASE WHEN number_inpatient > 1 OR number_emergency > 2 OR number_outpatient > 5 THEN 3 ELSE 0 END) +
                  (CASE WHEN diag_1 LIKE '250.%' AND length(diag_1) >= 5 AND substr(diag_1,5,1) IN ('4','5','6','7','8','9') THEN 1.5 ELSE 0 END) +
                  (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('410','411','412','414','428','429','401','402','403','404','405') THEN 2 ELSE 0 END) +
                  (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('584','585','586','587','588','589','590') THEN 2 ELSE 0 END)) < 6 THEN 'High'
            ELSE 'Very High' END as risk_level,
        is_30day_readmit
    FROM readmission_analytics
)
SELECT 
    risk_level,
    COUNT(*) as patients,
    SUM(is_30day_readmit) as readmissions,
    ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) as rate,
    COUNT(*) * 0.5 as patients_targeted_50pct,
    COUNT(*) * 0.5 * 750 as program_cost_50pct_750,
    SUM(is_30day_readmit) * 0.15 as avoided_15pct,
    SUM(is_30day_readmit) * 0.15 * 15000 as savings_15pct,
    (SUM(is_30day_readmit) * 0.15 * 15000) - (COUNT(*) * 0.5 * 750) as net_benefit_50_15_750
FROM risk_base
GROUP BY risk_level;


-- =============================================================================
-- SHEET 7: HIGH-RISK PATIENT PROFILE
-- Top 20% by risk score
-- =============================================================================
WITH ra AS (
    SELECT *,
        (num_medications > 15)*2 + (time_in_hospital > 7)*2.5 +
        (CASE WHEN number_inpatient > 1 OR number_emergency > 2 OR number_outpatient > 5 THEN 3 ELSE 0 END) +
        (CASE WHEN diag_1 LIKE '250.%' AND length(diag_1) >= 5 AND substr(diag_1,5,1) IN ('4','5','6','7','8','9') THEN 1.5 ELSE 0 END) +
        (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('410','411','412','414','428','429','401','402','403','404','405') THEN 2 ELSE 0 END) +
        (CASE WHEN substr(COALESCE(diag_1,''),1,3) IN ('584','585','586','587','588','589','590') THEN 2 ELSE 0 END) as risk_score
    FROM readmission_analytics
),
ranked AS (
    SELECT *, NTILE(5) OVER (ORDER BY risk_score DESC) as risk_quintile
    FROM ra
)
SELECT 
    age,
    race,
    gender,
    admission_type_desc,
    CASE WHEN time_in_hospital <= 3 THEN '1-3' WHEN time_in_hospital <= 7 THEN '4-7' ELSE '8+' END as los_days,
    num_medications,
    number_inpatient + number_emergency + number_outpatient as prior_utilization,
    CASE 
        WHEN diag_1 LIKE '250%' THEN 'Diabetes'
        WHEN substr(COALESCE(diag_1,''),1,3) IN ('428','402','404') THEN 'Heart Failure'
        WHEN substr(COALESCE(diag_1,''),1,3) IN ('491','492','493','496') THEN 'COPD'
        ELSE substr(diag_1,1,3)
    END as primary_diagnosis,
    COUNT(*) as patient_count,
    SUM(is_30day_readmit) as readmissions,
    ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) as readmission_rate
FROM ranked
WHERE risk_quintile = 1  -- Top 20% highest risk
GROUP BY age, race, gender, admission_type_desc, los_days, num_medications, prior_utilization, primary_diagnosis
ORDER BY readmission_rate DESC;
