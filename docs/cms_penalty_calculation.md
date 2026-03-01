# CMS HRRP Penalty Calculation

Under the Hospital Readmission Reduction Program (HRRP), Medicare may reduce payments when a hospital's readmission rate exceeds the **national benchmark** (e.g. 15.5% overall).

- **Excess readmission ratio** = Hospital rate / Benchmark.
- If ratio > 1, penalty is based on Medicare revenue and the excess (capped at ~3% of revenue).
- In this project: readmission rate 9.5% is below 15.5%, so **penalty = $0**.
- See `07_financial_analysis.py` for the exact logic used.

Reference: [CMS HRRP](https://www.cms.gov/medicare/quality/patient-safety/hospital-readmission-reduction-program)
