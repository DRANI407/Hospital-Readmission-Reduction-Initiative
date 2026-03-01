-- =============================================================================
-- 02_explore_data.sql — Exploratory queries for readmission analytics
-- Run against data/readmissions.db after 01_load_data.py and 03_readmission_cohorts.sql
-- =============================================================================

-- Encounter count
SELECT COUNT(*) AS total_encounters FROM readmission_analytics;

-- Readmission rate overall
SELECT 
    SUM(is_30day_readmit) AS readmissions,
    COUNT(*) AS encounters,
    ROUND(100.0 * SUM(is_30day_readmit) / COUNT(*), 2) AS readmission_rate_pct
FROM readmission_analytics;

-- By admission type
SELECT admission_type_desc, COUNT(*) AS n, 
       ROUND(100.0 * SUM(is_30day_readmit)/COUNT(*), 2) AS readmit_pct
FROM readmission_analytics
GROUP BY admission_type_desc ORDER BY n DESC;

-- By age band
SELECT age, COUNT(*) AS n, 
       ROUND(100.0 * SUM(is_30day_readmit)/COUNT(*), 2) AS readmit_pct
FROM readmission_analytics
WHERE age IS NOT NULL
GROUP BY age ORDER BY age;
