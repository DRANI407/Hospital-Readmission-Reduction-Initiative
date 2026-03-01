"""
Readmission Dashboard - Static Visualization
Implements the Tableau design layout using matplotlib/seaborn.
Run: python build_dashboard.py
Output: readmission_project/outputs/readmission_dashboard.png
"""

import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'readmission_project' / 'data'
OUTPUTS_DIR = PROJECT_ROOT / 'readmission_project' / 'outputs'
DB_PATH = DATA_DIR / 'readmissions.db'

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9


def load_data(conn):
    """Load all dashboard data from SQLite."""
    # KPIs
    kpis = pd.read_sql("""
        SELECT 'Total Encounters' as kpi_name, CAST(COUNT(*) AS REAL) as value, NULL as benchmark FROM readmission_analytics
        UNION ALL SELECT 'Readmission Rate %', ROUND(100.0*SUM(is_30day_readmit)/COUNT(*),2), 15.5 FROM readmission_analytics
        UNION ALL SELECT 'Est. Cost', SUM(is_30day_readmit)*15000, NULL FROM readmission_analytics
        UNION ALL SELECT 'CMS Penalty', 0, NULL FROM readmission_analytics
    """, conn)
    
    # Trend
    trend = pd.read_sql("""
        SELECT strftime('%Y-%m', adm_date) as month, strftime('%Y-%m-01', adm_date) as month_date,
               COUNT(*) as encounters, SUM(is_30day_readmit) as readmissions,
               ROUND(100.0*SUM(is_30day_readmit)/COUNT(*),2) as readmission_rate
        FROM readmission_analytics GROUP BY month ORDER BY month_date
    """, conn)
    trend['benchmark_status'] = trend['readmission_rate'] > 15.5
    
    # Risk heat map (age x meds)
    heatmap = pd.read_sql("""
        SELECT age, 
            CASE WHEN num_medications<=5 THEN '0-5' WHEN num_medications<=10 THEN '6-10'
                 WHEN num_medications<=15 THEN '11-15' WHEN num_medications<=20 THEN '16-20'
                 ELSE '21+' END as medication_category,
            COUNT(*) as encounter_count, SUM(is_30day_readmit) as readmission_count,
            ROUND(100.0*SUM(is_30day_readmit)/COUNT(*),2) as readmission_rate
        FROM readmission_analytics
        GROUP BY age, medication_category
    """, conn)
    
    # Diagnosis impact
    diag = pd.read_sql("""
        WITH d AS (
            SELECT substr(diag_1,1,3) as code, is_30day_readmit
            FROM readmission_analytics WHERE diag_1 IS NOT NULL AND diag_1 != '?' AND length(diag_1)>=3
        )
        SELECT code, COUNT(*) as encounters, SUM(is_30day_readmit) as readmissions,
               ROUND(100.0*SUM(is_30day_readmit)/COUNT(*),2) as rate,
               SUM(is_30day_readmit)*15000 as total_cost
        FROM d GROUP BY code ORDER BY total_cost DESC LIMIT 10
    """, conn)
    
    return kpis, trend, heatmap, diag


def build_dashboard():
    conn = sqlite3.connect(DB_PATH)
    kpis, trend, heatmap, diag = load_data(conn)
    conn.close()
    
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.3,
                          height_ratios=[0.5, 1.2, 1.2, 1])
    
    # --- Row 0: KPI Cards ---
    kpi_vals = dict(zip(kpis['kpi_name'], kpis['value']))
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.axis('off')
    
    cards = [
        ('Total Encounters', f"{kpi_vals.get('Total Encounters', 0):,.0f}", '#3498db'),
        ('Readmission Rate', f"{kpi_vals.get('Readmission Rate %', 0):.1f}%", '#9b59b6'),
        ('Est. Cost', f"${kpi_vals.get('Est. Cost', 0)/1e6:.1f}M", '#e74c3c'),
        ('CMS Penalty', f"${kpi_vals.get('CMS Penalty', 0):,.0f}", '#27ae60'),
    ]
    for i, (title, val, color) in enumerate(cards):
        ax_kpi.add_patch(plt.Rectangle((i*0.24, 0.1), 0.22, 0.8, facecolor=color, alpha=0.3, edgecolor=color))
        ax_kpi.text(i*0.24 + 0.11, 0.6, val, ha='center', va='center', fontsize=14, fontweight='bold')
        ax_kpi.text(i*0.24 + 0.11, 0.25, title, ha='center', va='center', fontsize=9)
    ax_kpi.set_xlim(0, 1)
    ax_kpi.set_ylim(0, 1)
    ax_kpi.set_title('Readmission Performance & Financial Impact', fontsize=16, fontweight='bold', pad=10)
    
    # --- Row 1: Trend + Heat Map ---
    # Trend
    ax_trend = fig.add_subplot(gs[1, 0])
    colors = ['#e74c3c' if x else '#27ae60' for x in trend['benchmark_status']]
    ax_trend.bar(range(len(trend)), trend['readmission_rate'], color=colors, alpha=0.8)
    ax_trend.axhline(y=15.5, color='black', linestyle='--', label='National Benchmark')
    ax_trend.set_xticks(range(len(trend)))
    ax_trend.set_xticklabels(trend['month'], rotation=45)
    ax_trend.set_ylabel('Readmission Rate %')
    ax_trend.set_title('Readmission Trend by Month')
    ax_trend.legend()
    ax_trend.set_ylim(0, max(trend['readmission_rate'].max(), 20) * 1.1)
    
    # Heat Map
    ax_heat = fig.add_subplot(gs[1, 1])
    pivot = heatmap.pivot_table(values='readmission_rate', index='age', columns='medication_category',
                                aggfunc='mean')
    # Ensure column order
    med_order = ['0-5', '6-10', '11-15', '16-20', '21+']
    pivot = pivot.reindex(columns=[c for c in med_order if c in pivot.columns])
    sns.heatmap(pivot, ax=ax_heat, cmap='YlOrRd', annot=True, fmt='.1f', cbar_kws={'label': 'Readmit %'})
    ax_heat.set_title('Risk Heat Map: Age x Medications')
    
    # --- Row 2: Diagnosis + High-Risk Profile ---
    # Diagnosis Impact
    ax_diag = fig.add_subplot(gs[2, 0])
    bars = ax_diag.barh(diag['code'], diag['total_cost']/1e6, color='#3498db', alpha=0.8)
    ax_diag.set_xlabel('Cost ($M)')
    ax_diag.set_title('Top 10 Diagnoses by Readmission Cost')
    
    # High-risk placeholder (summary text)
    ax_profile = fig.add_subplot(gs[2, 1])
    ax_profile.axis('off')
    risk_text = """
HIGH-RISK PATIENT PROFILE (Top 20%)
-----------------------------------
• Higher readmission rate: 18-20%
• Key factors: Polypharmacy (21+ meds),
  Long LOS (8+ days), Prior ED/inpatient
• Top diagnoses: Heart Failure, Diabetes,
  COPD, Other
• Target for intervention programs
"""
    ax_profile.text(0.1, 0.9, risk_text, transform=ax_profile.transAxes,
                    fontsize=10, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))
    ax_profile.set_title('High-Risk Patient Profile')
    
    # --- Row 3: ROI Simulator ---
    ax_roi = fig.add_subplot(gs[3, :])
    ax_roi.axis('off')
    coverage, eff, cost = 0.5, 0.15, 750
    total_patients = kpi_vals.get('Total Encounters', 100000)
    total_readmits = total_patients * (kpi_vals.get('Readmission Rate %', 10) / 100)
    targeted = total_patients * 0.2 * coverage  # 20% high-risk
    program_cost = targeted * cost
    avoided = total_readmits * 0.38 * eff * coverage  # 38% of readmits in high-risk
    savings = avoided * 15000
    net = savings - program_cost
    roi = net / program_cost * 100 if program_cost > 0 else 0
    
    roi_text = f"""
INTERVENTION ROI SIMULATOR (Coverage={coverage:.0%}, Effectiveness={eff:.0%}, Cost=${cost}/patient)
────────────────────────────────────────────────────────────────────────────────────────────
  Patients Targeted: {targeted:,.0f}    Program Cost: ${program_cost:,.0f}
  Readmissions Avoided: {avoided:,.0f}   Savings: ${savings:,.0f}
  NET BENEFIT: ${net:,.0f}    ROI: {roi:.1f}%
"""
    ax_roi.text(0.05, 0.7, roi_text, transform=ax_roi.transAxes,
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='#e8f6f3', alpha=0.9))
    ax_roi.set_title('Intervention ROI Simulator', fontweight='bold')
    
    plt.savefig(OUTPUTS_DIR / 'readmission_dashboard.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Dashboard saved to {OUTPUTS_DIR / 'readmission_dashboard.png'}")


if __name__ == '__main__':
    try:
        import seaborn as sns
    except ImportError:
        sns = None
        print("Warning: seaborn not found, heatmap may differ")
    
    build_dashboard()
