"""
Step 4: Financial Impact Analysis — Hospital Readmission Reduction Initiative

Uses model-ready data and risk scores to estimate readmission cost by diagnosis
and age, CMS HRRP penalty exposure, and ROI of a transitional care intervention.
Produces dashboards, CSVs, impact statement, and executive summary inputs.

Outputs: outputs/visuals/financial_analysis_dashboard.png,
         roi_analysis.csv, savings_scenarios.csv, impact_statement.txt, etc.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
VISUALS_DIR = OUTPUTS_DIR / 'visuals'
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
VISUALS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("FINANCIAL IMPACT ANALYSIS - READMISSION REDUCTION")
print("=" * 60)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}")
print("=" * 60)

# Load data
df = pd.read_csv(DATA_DIR / 'model_ready_data.csv')

# Derive age band from age_midpoint (model_ready_data has age_midpoint, not age)
age_band_map = {5: '[0-10)', 15: '[10-20)', 25: '[20-30)', 35: '[30-40)', 45: '[40-50)',
                55: '[50-60)', 65: '[60-70)', 75: '[70-80)', 85: '[80-90)', 95: '[90-100)'}
df['age'] = df['age_midpoint'].map(age_band_map)

# CMS Hospital Readmission Reduction Program (HRRP) parameters
cms_penalty_base_rate = 0.03
avg_medicare_reimbursement = 15200
total_encounters = len(df)
total_readmissions = df['target'].sum()
current_readmission_rate = df['target'].mean()

print("\n📊 BASELINE METRICS")
print("-" * 40)
print(f"Total Encounters: {total_encounters:,}")
print(f"Total 30-day Readmissions: {total_readmissions:,}")
print(f"Current Readmission Rate: {current_readmission_rate:.2%}")

# ============================================================================
# STEP 1: CMS PENALTY CALCULATION
# ============================================================================
print("\n🏥 CMS HOSPITAL READMISSION REDUCTION PROGRAM (HRRP)")
print("-" * 40)

national_benchmarks = {
    'Overall': 0.155,
    'Heart Failure': 0.225,
    'Pneumonia': 0.170,
    'COPD': 0.200,
    'AMI': 0.180,
    'Diabetes': 0.145
}

excess_ratio = current_readmission_rate / national_benchmarks['Overall']

# Medicare eligibility: 65+ (age_midpoint >= 65)
df['medicare_eligible'] = df['age_midpoint'] >= 65
medicare_pct = df['medicare_eligible'].mean()
medicare_encounters = total_encounters * medicare_pct
estimated_medicare_revenue = medicare_encounters * avg_medicare_reimbursement

print(f"Your readmission rate: {current_readmission_rate:.2%}")
print(f"National benchmark: {national_benchmarks['Overall']:.2%}")
print(f"Excess ratio: {excess_ratio:.3f}")
print(f"Medicare-eligible patients: {medicare_pct:.1%} of total")

if excess_ratio > 1.0:
    expected_readmissions = medicare_encounters * national_benchmarks['Overall']
    actual_medicare_readmissions = df[df['medicare_eligible']]['target'].sum()
    excess_medicare_readmissions = max(0, actual_medicare_readmissions - expected_readmissions)

    penalty_multiplier = min(cms_penalty_base_rate, (excess_ratio - 1.0) * 0.5)
    penalty_amount = estimated_medicare_revenue * penalty_multiplier

    print(f"\n💰 CMS PENALTY CALCULATION:")
    print(f"  Medicare encounters: {medicare_encounters:,.0f}")
    print(f"  Expected Medicare readmissions: {expected_readmissions:,.0f}")
    print(f"  Actual Medicare readmissions: {actual_medicare_readmissions:,.0f}")
    print(f"  Excess Medicare readmissions: {excess_medicare_readmissions:,.0f}")
    print(f"  Estimated Medicare revenue: ${estimated_medicare_revenue:,.0f}")
    print(f"  Penalty multiplier: {penalty_multiplier:.3f}")
    print(f"  ⚠️  ESTIMATED ANNUAL PENALTY: ${penalty_amount:,.0f}")
else:
    penalty_amount = 0
    print(f"\n✅ Your readmission rate is below national benchmark. No penalty!")

# ============================================================================
# STEP 2: READMISSION COST ANALYSIS
# ============================================================================
print("\n💰 READMISSION COST ANALYSIS")
print("-" * 40)

cost_scenarios = {
    'Conservative': 10000,
    'Moderate': 15000,
    'Aggressive': 20000
}

print("Cost per readmission estimates:")
total_costs = {}
for scenario, cost in cost_scenarios.items():
    total_cost = total_readmissions * cost
    total_costs[scenario] = total_cost
    print(f"  {scenario:12} : ${cost:6,.0f} → Total cost: ${total_cost:,.0f}")

# ============================================================================
# STEP 3: COST BREAKDOWN BY PATIENT SEGMENT
# ============================================================================
print("\n📋 COST BREAKDOWN BY PATIENT SEGMENT")
print("-" * 40)

age_groups = ['[30-40)', '[40-50)', '[50-60)', '[60-70)', '[70-80)', '[80-90)', '[90-100)']
age_costs = []
for age in age_groups:
    age_df = df[df['age'] == age]
    if len(age_df) > 0:
        age_readmits = age_df['target'].sum()
        age_cost = age_readmits * cost_scenarios['Moderate']
        age_costs.append({
            'Age Group': age,
            'Encounters': len(age_df),
            'Readmissions': age_readmits,
            'Rate': age_df['target'].mean(),
            'Total Cost': age_cost
        })

age_cost_df = pd.DataFrame(age_costs)
print("\nReadmission Cost by Age Group:")
print(age_cost_df.to_string(index=False, float_format='%.1f'))

def get_diagnosis_category(diag):
    if pd.isna(diag) or diag == '?':
        return 'Unknown'
    diag_str = str(diag)
    if diag_str.startswith('250'):
        return 'Diabetes'
    elif diag_str.startswith(('428', '402', '404')):
        return 'Heart Failure'
    elif diag_str.startswith(('410', '411', '412', '413', '414')):
        return 'CAD'
    elif diag_str.startswith(('491', '492', '493', '496')):
        return 'COPD'
    elif diag_str.startswith(('486', '481', '482')):
        return 'Pneumonia'
    else:
        return 'Other'

df['diag_category'] = df['diag_1'].apply(get_diagnosis_category)
diag_costs = df.groupby('diag_category').agg({
    'target': ['count', 'sum', 'mean']
}).round(3)
diag_costs.columns = ['Encounters', 'Readmissions', 'Rate']
diag_costs['Total Cost'] = diag_costs['Readmissions'] * cost_scenarios['Moderate']
diag_costs = diag_costs.sort_values('Total Cost', ascending=False)

print("\nReadmission Cost by Diagnosis Category:")
print(diag_costs.to_string(float_format='%.0f'))

# ============================================================================
# STEP 4: SAVINGS FROM READMISSION REDUCTION
# ============================================================================
print("\n📈 POTENTIAL SAVINGS FROM READMISSION REDUCTION")
print("-" * 40)

reduction_scenarios = [0.05, 0.10, 0.15, 0.20, 0.25]

savings_data = []
for reduction in reduction_scenarios:
    readmissions_avoided = total_readmissions * reduction
    for scenario, cost in cost_scenarios.items():
        savings = readmissions_avoided * cost
        savings_data.append({
            'Reduction': f"{reduction:.0%}",
            'Cost Scenario': scenario,
            'Readmissions Avoided': int(readmissions_avoided),
            'Savings': savings,
            'Savings (Millions)': savings / 1_000_000
        })

savings_df = pd.DataFrame(savings_data)

pivot_savings = savings_df.pivot_table(
    values='Savings',
    index='Reduction',
    columns='Cost Scenario'
).round(0)

print("\nPotential Savings by Reduction Level:")
print(pivot_savings.to_string())

# ============================================================================
# STEP 5: INTERVENTION PROGRAM COST-BENEFIT ANALYSIS
# ============================================================================
print("\n📊 INTERVENTION PROGRAM ROI ANALYSIS")
print("-" * 40)

df['risk_score'] = (
    df['polypharmacy'] * 2 +
    df['long_los'] * 2.5 +
    df['high_prior_utilization'] * 3 +
    df['diabetes_complications'] * 1.5 +
    df['cardiovascular'] * 2 +
    df['renal'] * 2
)

df['risk_quartile'] = pd.qcut(df['risk_score'], q=4, labels=False, duplicates='drop')
df['risk_level'] = pd.cut(df['risk_score'],
                          bins=[-1, 2, 4, 6, 100],
                          labels=['Low', 'Medium', 'High', 'Very High'])

risk_rates = df.groupby('risk_level', observed=True).agg({
    'target': ['count', 'sum', 'mean']
}).round(3)
risk_rates.columns = ['Patients', 'Readmissions', 'Rate']
risk_rates['Cost'] = risk_rates['Readmissions'] * cost_scenarios['Moderate']

print("\nReadmission Rates by Risk Level:")
print(risk_rates.to_string(float_format='%.0f'))

print("\n🎯 INTERVENTION PROGRAM ASSUMPTIONS:")
intervention_assumptions = {
    'Target Population': 'Very High & High Risk Patients',
    'Intervention Cost per Patient': 750,
    'Program Duration': '6 months',
    'Expected Effectiveness': '15-20% reduction in high-risk group',
    'Intervention Types': 'Transitional care, medication reconciliation, follow-up calls'
}
for key, value in intervention_assumptions.items():
    print(f"  {key:25}: {value}")

high_risk_patients = df[df['risk_level'].isin(['High', 'Very High'])]
n_high_risk = len(high_risk_patients)
high_risk_readmits = high_risk_patients['target'].sum()
high_risk_rate = high_risk_readmits / n_high_risk if n_high_risk > 0 else 0

print(f"\nHigh-risk population: {n_high_risk:,} patients")
print(f"High-risk readmission rate: {high_risk_rate:.2%}")
print(f"High-risk readmissions: {high_risk_readmits:.0f}")

coverage_scenarios = [0.25, 0.50, 0.75, 1.00]
effectiveness_scenarios = [0.10, 0.15, 0.20]

roi_results = []
for coverage in coverage_scenarios:
    for effectiveness in effectiveness_scenarios:
        targeted = int(n_high_risk * coverage)
        program_cost = targeted * 750

        readmissions_avoided = high_risk_readmits * effectiveness * coverage
        savings = readmissions_avoided * cost_scenarios['Moderate']

        net_benefit = savings - program_cost
        roi = (savings - program_cost) / program_cost if program_cost > 0 else 0

        roi_results.append({
            'Coverage': f"{coverage:.0%}",
            'Effectiveness': f"{effectiveness:.0%}",
            'Targeted Patients': targeted,
            'Program Cost': program_cost,
            'Readmissions Avoided': round(readmissions_avoided, 1),
            'Savings': savings,
            'Net Benefit': net_benefit,
            'ROI': roi
        })

roi_df = pd.DataFrame(roi_results)

print("\n📈 ROI ANALYSIS BY SCENARIO:")
best_scenarios = roi_df.nlargest(5, 'ROI')[['Coverage', 'Effectiveness', 'Program Cost',
                                            'Savings', 'Net Benefit', 'ROI']]
print(best_scenarios.to_string(float_format='%.0f'))

optimal = roi_df[(roi_df['Coverage'] == '50%') & (roi_df['Effectiveness'] == '15%')].iloc[0]

# ============================================================================
# STEP 6: FINANCIAL VISUALIZATION
# ============================================================================
print("\n📊 CREATING FINANCIAL VISUALIZATIONS...")

try:
    plt.style.use('seaborn-v0_8-darkgrid')
except OSError:
    plt.style.use('seaborn-darkgrid')

fig = plt.figure(figsize=(16, 12))
fig.suptitle('Readmission Financial Impact Analysis', fontsize=16, fontweight='bold')

# 1. Current State Summary
ax1 = plt.subplot(3, 3, 1)
ax1.axis('off')
current_state_text = f"""
CURRENT STATE METRICS
----------------------
Total Encounters: {total_encounters:,}
Total Readmissions: {total_readmissions:,}
Readmission Rate: {current_readmission_rate:.1%}

Medicare Encounters: {medicare_encounters:,.0f}
Est. Medicare Revenue: ${estimated_medicare_revenue:,.0f}

COST OF READMISSIONS
----------------------
Conservative: ${total_costs['Conservative']:,.0f}
Moderate: ${total_costs['Moderate']:,.0f}
Aggressive: ${total_costs['Aggressive']:,.0f}
"""
ax1.text(0.1, 0.9, current_state_text, transform=ax1.transAxes,
         fontsize=10, verticalalignment='top', fontfamily='monospace')

# 2. CMS Penalty Visualization
ax2 = plt.subplot(3, 3, 2)
penalty_data = {
    'Your Rate': current_readmission_rate,
    'Benchmark': national_benchmarks['Overall'],
    'Excess': max(0, current_readmission_rate - national_benchmarks['Overall'])
}
bars = ax2.bar(penalty_data.keys(), penalty_data.values(),
               color=['#e74c3c', '#2ecc71', '#f39c12'])
ax2.set_ylabel('Readmission Rate')
ax2.set_title('CMS Penalty Benchmark Comparison')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
for bar, val in zip(bars, penalty_data.values()):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             f'{val:.1%}', ha='center', va='bottom')

# 3. Penalty Amount
ax3 = plt.subplot(3, 3, 3)
if penalty_amount > 0:
    ax3.bar(['Estimated Penalty'], [penalty_amount], color='#e74c3c')
    ax3.text(0, penalty_amount + 5000, f'${penalty_amount:,.0f}',
             ha='center', va='bottom')
else:
    ax3.bar(['No Penalty'], [1], color='#2ecc71')
    ax3.text(0, 0.5, '✓ Below Benchmark', ha='center', va='center')
ax3.set_ylabel('Amount ($)')
ax3.set_title('CMS Penalty Exposure')
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))

# 4. Readmission Cost by Age Group
ax4 = plt.subplot(3, 3, 4)
if len(age_cost_df) > 0:
    age_plot_data = age_cost_df.sort_values('Age Group')
    ax4.barh(age_plot_data['Age Group'], age_plot_data['Total Cost'], color='#3498db')
ax4.set_xlabel('Total Cost ($)')
ax4.set_title('Readmission Cost by Age Group')
ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))

# 5. Readmission Rate by Risk Level
ax5 = plt.subplot(3, 3, 5)
risk_plot = risk_rates.reset_index()
colors = {'Low': '#27ae60', 'Medium': '#f1c40f', 'High': '#e67e22', 'Very High': '#e74c3c'}
bar_colors = [colors.get(level, '#95a5a6') for level in risk_plot['risk_level']]
bars = ax5.bar(risk_plot['risk_level'].astype(str), risk_plot['Rate'], color=bar_colors)
ax5.set_ylabel('Readmission Rate')
ax5.set_title('Readmission Rate by Risk Level')
ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
for bar, rate in zip(bars, risk_plot['Rate']):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{rate:.1%}', ha='center', va='bottom')

# 6. Savings by Reduction Level
ax6 = plt.subplot(3, 3, 6)
reduction_levels = ['5%', '10%', '15%', '20%', '25%']
savings_values = [pivot_savings.loc[r, 'Moderate'] for r in reduction_levels]
bars = ax6.bar(reduction_levels, savings_values, color='#27ae60')
ax6.set_xlabel('Readmission Reduction')
ax6.set_ylabel('Savings ($)')
ax6.set_title('Potential Savings by Reduction Level')
ax6.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
for bar, val in zip(bars, savings_values):
    ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50000,
             f'${val/1e6:.1f}M', ha='center', va='bottom')

# 7. ROI Analysis
ax7 = plt.subplot(3, 3, 7)
roi_plot_data = roi_df[(roi_df['Effectiveness'] == '15%') &
                       (roi_df['Coverage'].isin(['25%', '50%', '75%', '100%']))]
ax7.bar(roi_plot_data['Coverage'], roi_plot_data['ROI'], color='#9b59b6')
ax7.set_xlabel('Population Coverage')
ax7.set_ylabel('ROI')
ax7.set_title('ROI by Intervention Coverage')
ax7.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

# 8. Cost Breakdown by Diagnosis
ax8 = plt.subplot(3, 3, 8)
top_diag = diag_costs.head(5).reset_index()
ax8.barh(top_diag['diag_category'], top_diag['Total Cost'], color='#e67e22')
ax8.set_xlabel('Total Cost ($)')
ax8.set_title('Top 5 Diagnosis by Cost')
ax8.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))

# 9. Optimal Scenario Summary
ax9 = plt.subplot(3, 3, 9)
ax9.axis('off')
penalty_millions = penalty_amount / 1e6 if penalty_amount else 0
optimal_text = f"""
OPTIMAL INTERVENTION SCENARIO
-------------------------------
Target: {optimal['Coverage']} of high-risk
Effectiveness: {optimal['Effectiveness']}
Patients targeted: {optimal['Targeted Patients']:,}

Program Cost: ${optimal['Program Cost']:,.0f}
Readmissions Avoided: {optimal['Readmissions Avoided']:.0f}
Savings: ${optimal['Savings']:,.0f}
Net Benefit: ${optimal['Net Benefit']:,.0f}
ROI: {optimal['ROI']:.1%}

IMPACT STATEMENT
-------------------------------
Targeted discharge planning for top-risk cohorts
could reduce readmissions by 7-15%, avoiding
~${optimal['Savings']/1e6:.1f}M in annual costs
and {penalty_millions:.1f}M in CMS penalties.
"""
ax9.text(0.1, 0.9, optimal_text, transform=ax9.transAxes,
         fontsize=10, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))

plt.tight_layout()
plt.savefig(VISUALS_DIR / 'financial_impact_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"Saved dashboard to {VISUALS_DIR / 'financial_impact_dashboard.png'}")

# ============================================================================
# STEP 7: FINAL CALCULATIONS FOR EXECUTIVE SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("💰 FINANCIAL SUMMARY - KEY METRICS")
print("=" * 60)

target_reduction = 0.12
target_readmissions_avoided = total_readmissions * target_reduction
target_savings = target_readmissions_avoided * cost_scenarios['Moderate']
intervention_cost_50 = n_high_risk * 0.5 * 750
target_net_savings = target_savings - intervention_cost_50

final_metrics = {
    'Current Readmission Rate': f"{current_readmission_rate:.1%}",
    'National Benchmark': f"{national_benchmarks['Overall']:.1%}",
    'CMS Penalty Exposure': f"${penalty_amount:,.0f}",
    'Annual Readmission Cost': f"${total_costs['Moderate']:,.0f}",
    'High-Risk Patients': f"{n_high_risk:,}",
    'High-Risk Readmission Rate': f"{high_risk_rate:.1%}",
    'Target Readmission Reduction': f"{target_reduction:.0%}",
    'Readmissions Avoided (Target)': f"{target_readmissions_avoided:.0f}",
    'Potential Annual Savings': f"${target_savings:,.0f}",
    'Intervention Program Cost': f"${intervention_cost_50:,.0f}",
    'Net Financial Impact': f"${target_net_savings:,.0f}",
    'Program ROI': f"{target_net_savings / intervention_cost_50:.1%}" if intervention_cost_50 > 0 else "N/A"
}

print("\n📋 EXECUTIVE SUMMARY METRICS:")
for key, value in final_metrics.items():
    print(f"  {key:30}: {value}")

# ============================================================================
# STEP 8: EXPORT RESULTS
# ============================================================================
print("\n💾 EXPORTING RESULTS...")

try:
    import openpyxl
    with pd.ExcelWriter(OUTPUTS_DIR / 'financial_analysis_results.xlsx', engine='openpyxl') as writer:
        age_cost_df.to_excel(writer, sheet_name='Age Group Analysis', index=False)
        diag_costs.to_excel(writer, sheet_name='Diagnosis Analysis')
        savings_df.to_excel(writer, sheet_name='Savings Scenarios', index=False)
        roi_df.to_excel(writer, sheet_name='ROI Analysis', index=False)
        risk_rates.to_excel(writer, sheet_name='Risk Stratification')
        summary_df = pd.DataFrame(list(final_metrics.items()), columns=['Metric', 'Value'])
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
    print(f"✅ Results saved to {OUTPUTS_DIR / 'financial_analysis_results.xlsx'}")
except ImportError:
    age_cost_df.to_csv(OUTPUTS_DIR / 'age_group_analysis.csv', index=False)
    diag_costs.to_csv(OUTPUTS_DIR / 'diagnosis_analysis.csv')
    savings_df.to_csv(OUTPUTS_DIR / 'savings_scenarios.csv', index=False)
    roi_df.to_csv(OUTPUTS_DIR / 'roi_analysis.csv', index=False)
    print("✅ CSV exports saved (install openpyxl for Excel: pip install openpyxl)")

# ============================================================================
# STEP 9: GENERATE IMPACT STATEMENT
# ============================================================================
print("\n" + "=" * 60)
print("📢 IMPACT STATEMENT")
print("=" * 60)

impact_statement = f"""
Based on comprehensive financial analysis of {total_encounters:,} patient encounters:

📊 CURRENT STATE:
- 30-day readmission rate: {current_readmission_rate:.1%} ({total_readmissions:,} readmissions)
- Annual readmission cost: ${total_costs['Moderate']/1e6:.1f}M
- CMS penalty exposure: ${penalty_amount/1e6:.1f}M

🎯 HIGH-RISK POPULATION:
- {n_high_risk:,} patients identified as high-risk ({n_high_risk/total_encounters:.1%} of total)
- Readmission rate in this group: {high_risk_rate:.1%}
- Accounts for {high_risk_readmits/total_readmissions:.1%} of all readmissions

💰 INTERVENTION IMPACT:
Targeted discharge planning and transitional care management for the top 50% of high-risk patients
(approximately {int(n_high_risk*0.5):,} patients) at $750 per patient would:

✅ Reduce readmissions by {target_reduction:.0%} overall
✅ Avoid approximately {target_readmissions_avoided:.0f} readmissions annually
✅ Generate ${target_savings/1e6:.1f}M in savings
✅ Net financial benefit of ${target_net_savings/1e6:.1f}M after program costs
✅ ROI of {f"{target_net_savings / intervention_cost_50:.1%}" if intervention_cost_50 > 0 else "N/A"}

🏆 KEY IMPACT STATEMENT:
"Targeted discharge planning for top-risk cohorts could reduce readmissions by 12%,
avoiding ~${target_savings/1e6:.1f}M in annual costs and reducing CMS penalty exposure
by ${penalty_amount/1e6:.1f}M, for a total financial impact of ${(target_savings + penalty_amount)/1e6:.1f}M."
"""

print(impact_statement)

with open(OUTPUTS_DIR / 'impact_statement.txt', 'w') as f:
    f.write(impact_statement)

print(f"\n✅ Impact statement saved to {OUTPUTS_DIR / 'impact_statement.txt'}")
print("=" * 60)
