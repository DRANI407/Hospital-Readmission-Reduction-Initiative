"""
Create a professional PNG of model coefficients (odds ratios).
Run from project root: python3 readmission_project/outputs/model_coefficients_viz.py
"""
import joblib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent
model_path = OUT / 'readmission_model.pkl'

feature_names = [
    'age_midpoint', 'time_in_hospital', 'num_lab_procedures',
    'num_procedures', 'num_medications', 'number_diagnoses',
    'diabetes_complications', 'cardiovascular', 'respiratory', 'renal',
    'high_prior_utilization', 'long_los', 'polypharmacy',
    'a1c_abnormal', 'insulin_level'
]

model = joblib.load(model_path)
odds_ratios = np.exp(model.coef_[0])

# Sort by odds ratio so narrative is clear (protective first, then risk)
order = np.argsort(odds_ratios)
labels = [feature_names[i] for i in order]
values = odds_ratios[order]
colors = ['#2e7d32' if v < 1 else '#c62828' for v in values]  # green protective, red risk

fig, ax = plt.subplots(figsize=(10, 8))
y_pos = np.arange(len(labels))
bars = ax.barh(y_pos, values, color=colors, height=0.65, edgecolor='white', linewidth=0.8)
ax.axvline(x=1.0, color='#37474f', linestyle='--', linewidth=1.5, label='No effect (OR=1)')
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel('Odds ratio (per 1 SD)', fontsize=11)
ax.set_title('30-day readmission model: feature odds ratios', fontsize=13, fontweight='bold')
ax.set_xlim(0.5, 2.0)
ax.legend(loc='lower right', frameon=True)
ax.grid(axis='x', alpha=0.3, linestyle='-')
fig.tight_layout()

out_path = OUT / 'model_viz.png'
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"Saved: {out_path}")
