-- =============================================================================
-- 04_risk_factor_analysis.sql — Risk factor summaries for readmission
-- Run against data/readmissions.db after 03_readmission_cohorts.sql
-- =============================================================================

-- Readmission rate by length of stay bucket
SELECT 
    CASE 
        WHEN time_in_hospital <= 3 THEN '1-3'
        WHEN time_in_hospital <= 7 THEN '4-7'
        ELSE '8+'
    END AS los_bucket,
    COUNT(*) AS n,
    ROUND(100.0 * SUM(is_30day_readmit)/COUNT(*), 2) AS readmit_pct
FROM readmission_analytics
GROUP BY los_bucket ORDER BY los_bucket;

-- Readmission rate by number of medications (polypharmacy proxy)
SELECT 
    CASE WHEN num_medications > 15 THEN '15+' ELSE '<15' END AS med_bucket,
    COUNT(*) AS n,
    ROUND(100.0 * SUM(is_30day_readmit)/COUNT(*), 2) AS readmit_pct
FROM readmission_analytics
GROUP BY med_bucket;

-- Prior utilization: high vs low (inpatient >1 or emergency >2 or outpatient >5)
SELECT 
    CASE 
        WHEN number_inpatient > 1 OR number_emergency > 2 OR number_outpatient > 5 THEN 'High'
        ELSE 'Low'
    END AS prior_util,
    COUNT(*) AS n,
    ROUND(100.0 * SUM(is_30day_readmit)/COUNT(*), 2) AS readmit_pct
FROM readmission_analytics
GROUP BY prior_util;
