# Tableau Dashboard Prompts

Use these prompts when building the readmission dashboard in Tableau.

1. **Connect to data:** Connect to `data/readmissions.db` (SQLite) or run `scripts/08_dashboard_data.sql` and import the result CSVs.
2. **KPI cards:** Create a dashboard with 4 KPI cards: Total Encounters, Readmission Rate %, Est. Cost of Readmissions, CMS Penalty Exposure. Use the KPI extract (one row per metric).
3. **Trend line:** Line chart of readmission rate by month; add a reference line at 15.5% (national benchmark).
4. **Risk heat map:** Heat map of readmission rate by age and medication category (use the risk heat map extract).
5. **Diagnosis cost:** Bar chart of total cost by diagnosis category (top 10).
6. **ROI simulator:** Use parameters for coverage % and effectiveness %; show net benefit and ROI from the ROI extract.

See `dashboard_design.md` for full sheet specifications.
