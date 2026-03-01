# Tableau Dashboard Specification
## Readmission Performance & Financial Impact

---

## Overview

| Item | Value |
|------|-------|
| Dashboard Name | Readmission Performance & Financial Impact |
| Data Source | `readmission_project/data/readmissions.db` (SQLite) |
| Extract SQL File | `tableau_extracts.sql` |
| Layout | 7 sheets + filters |

---

## Sheet 1: KPI Cards

| Card | Data Source | Field | Format |
|------|-------------|-------|--------|
| Total Encounters | KPI extract | `value` where `kpi_name = 'Total Encounters'` | #,##0 |
| Readmission Rate | KPI extract | `value` where `kpi_name = 'Readmission Rate %'` | 0.0% |
| Benchmark Comparison | KPI extract | `benchmark` (15.5%) | Reference line / text |
| Estimated Cost | KPI extract | `value` where `kpi_name = 'Est. Cost of Readmissions'` | $#,##0 |
| CMS Penalty | KPI extract | `value` where `kpi_name = 'CMS Penalty Exposure'` | $#,##0 |

**Tableau Calculated Field – Above/Below Benchmark:**
```
IF [Readmission Rate %] > [National Benchmark] THEN "Above" ELSE "Below" END
```

---

## Sheet 2: Readmission Trend Line

**Chart Type:** Line chart

| Axis/Element | Field |
|--------------|-------|
| Columns (X) | `month` or `month_date` |
| Rows (Y) | `readmission_rate` |
| Reference Line | 15.5 (national benchmark) |
| Color | `benchmark_status` (Above = red, Below = green) |
| Tooltip | month, encounters, readmissions, readmission_rate |

**Data Source:** Trend extract from SQL

---

## Sheet 3: Risk Factor Heat Map

**Chart Type:** Heat map / Filled map

| Dimension | Field |
|-----------|-------|
| Rows | `age` |
| Columns | `medication_category` |
| Color (intensity) | `readmission_rate` – use diverging or sequential color palette |
| Size | `encounter_count` |
| Tooltip | age, medication_category, encounter_count, readmission_count, readmission_rate |

**Color Scale:** Sequential (e.g., white → red) or diverging from benchmark

---

## Sheet 4: Diagnosis Impact

**Chart Type:** Horizontal bar chart

| Axis/Element | Field |
|--------------|-------|
| Rows | `diag_code` or `diag_category` |
| Columns | `total_cost` |
| Color | `readmission_rate` (gradient) |
| Tooltip | diag_code, diag_category, encounters, readmissions, readmission_rate, total_cost |

**Filter:** Top 10 by total_cost (already in SQL)

---

## Sheet 5: Geographic/Provider Variation

**Chart Type:** Bar chart (or map if geography available)

| Axis | Field |
|------|-------|
| Rows | `segment` (admission_type_desc in current data) |
| Columns | `readmission_rate` |
| Tooltip | segment, encounters, readmissions, readmission_rate |

**Note:** Dataset has no geography. Use `admission_type_desc` as proxy. Replace with provider_id or hospital_id when available.

---

## Sheet 6: Intervention ROI Simulator

**Chart Type:** Text/KPI + parameter controls

### Parameters

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Coverage % | Float | 25–100 | 50 |
| Effectiveness % | Float | 5–25 | 15 |
| Cost per intervention | Currency | $500–$1000 | $750 |

### Calculated Fields (Tableau LOD or formula)

```
Patients Targeted = [Patients] * [Coverage %] / 100
Program Cost = [Patients Targeted] * [Cost per intervention]
Readmissions Avoided = [Readmissions] * [Effectiveness %] / 100 * [Coverage %] / 100
Savings = [Readmissions Avoided] * 15000
Net Benefit = [Savings] - [Program Cost]
ROI = [Net Benefit] / [Program Cost]
```

**Display:** Text objects with dynamic values, or custom KPI cards driven by parameters.

**Data Source:** ROI risk_segments extract (join parameters via blend or calculated fields)

---

## Sheet 7: High-Risk Patient Profile

**Chart Type:** Grouped bar or summary table

| Dimension | Field | Description |
|-----------|-------|-------------|
| Rows | age, race, gender, admission_type_desc | Demographics |
| Rows | los_days, num_medications, prior_utilization | Utilization |
| Rows | primary_diagnosis | Clinical |
| Values | patient_count, readmissions, readmission_rate | Metrics |

**Filter:** Top 20% risk only (already in SQL `risk_quintile = 1`)

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [KPI Card 1] [KPI Card 2] [KPI Card 3] [KPI Card 4]      [Filters]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Sheet 2: Readmission Trend]              [Sheet 3: Risk Heat Map]    │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Sheet 4: Diagnosis Impact]                [Sheet 7: High-Risk Profile]│
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Sheet 6: ROI Simulator]                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Global Filters

| Filter | Field | Behavior |
|--------|-------|----------|
| Date range | `adm_date` | Filter all sheets |
| Age group | `age` | Multi-select |
| Risk level | `risk_level` | Multi-select |
| Diagnosis category | `diag_category` | Multi-select |

---

## Color Palette Suggestions

| Use | Colors |
|-----|--------|
| Above benchmark | #e74c3c |
| Below benchmark | #27ae60 |
| Readmission rate (low) | #f8f9fa |
| Readmission rate (high) | #c0392b |
| Risk levels | Low=#27ae60, Medium=#f1c40f, High=#e67e22, Very High=#e74c3c |

---

## Connection Notes

- **SQLite:** Tableau can connect via ODBC driver or export SQL results to CSV.
- **CSV Export:** Run each query in `tableau_extracts.sql` and save as separate CSVs (e.g., `kpi_cards.csv`, `trend.csv`, etc.).
- **Refresh:** Re-run SQL after `readmission_analytics` is updated.
