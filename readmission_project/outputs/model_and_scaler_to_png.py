"""
Create one PNG from readmission_model.pkl + scaler.pkl: model odds ratios + scaler (mean/scale).
Run from project root: python3 readmission_project/outputs/model_and_scaler_to_png.py
"""
import joblib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent
feature_names = [
    'age_midpoint', 'time_in_hospital', 'num_lab_procedures',
    'num_procedures', 'num_medications', 'number_diagnoses',
    'diabetes_complications', 'cardiovascular', 'respiratory', 'renal',
    'high_prior_utilization', 'long_los', 'polypharmacy',
    'a1c_abnormal', 'insulin_level'
]

model = joblib.load(OUT / 'readmission_model.pkl')
scaler = joblib.load(OUT / 'scaler.pkl')

odds_ratios = np.exp(model.coef_[0])
order = np.argsort(odds_ratios)
labels = [feature_names[i] for i in order]
or_values = odds_ratios[order]
colors = ['#2e7d32' if v < 1 else '#c62828' for v in or_values]

fig = plt.figure(figsize=(12, 12))
fig.suptitle('Readmission model & scaler (from .pkl)', fontsize=14, fontweight='bold', y=0.98)

# --- Top: Model odds ratios ---
ax1 = fig.add_subplot(2, 1, 1)
y_pos = np.arange(len(labels))
ax1.barh(y_pos, or_values, color=colors, height=0.65, edgecolor='white', linewidth=0.8)
ax1.axvline(x=1.0, color='#37474f', linestyle='--', linewidth=1.5, label='No effect (OR=1)')
ax1.set_yticks(y_pos)
ax1.set_yticklabels(labels, fontsize=9)
ax1.set_xlabel('Odds ratio (per 1 SD)', fontsize=10)
ax1.set_title('Model: LogisticRegression — feature odds ratios', fontsize=11, fontweight='bold')
ax1.set_xlim(0.5, 2.0)
ax1.legend(loc='lower right', frameon=True)
ax1.grid(axis='x', alpha=0.3)

# --- Bottom: Scaler mean & scale ---
ax2 = fig.add_subplot(2, 1, 2)
mean_vals = scaler.mean_
scale_vals = scaler.scale_
x = np.arange(len(feature_names))
w = 0.35
bars1 = ax2.bar(x - w/2, mean_vals, w, label='Mean', color='#1565c0', alpha=0.85)
bars2 = ax2.bar(x + w/2, scale_vals, w, label='Scale', color='#6a1b9a', alpha=0.85)
ax2.set_xticks(x)
ax2.set_xticklabels(feature_names, rotation=45, ha='right', fontsize=8)
ax2.set_ylabel('Value', fontsize=10)
ax2.set_title('Scaler: StandardScaler — mean and scale per feature', fontsize=11, fontweight='bold')
ax2.legend(loc='upper right')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out_path = OUT / 'model_and_scaler.png'
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"Saved: {out_path}")
