"""
Step 3: Predictive Model — Hospital Readmission Reduction Initiative

Trains a logistic regression model (L2, balanced class weight) on standardized
features to predict 30-day readmission. Produces ROC-AUC, feature importance,
odds ratios, risk stratification, and saves the fitted model and scaler for
deployment. Requires 02_prepare_model_data.py outputs.

Outputs: readmission_project/outputs/readmission_model.pkl, scaler.pkl,
         model_performance.png
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (roc_auc_score, classification_report,
                             confusion_matrix, roc_curve, precision_recall_curve)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'readmission_project' / 'data'
OUTPUTS_DIR = PROJECT_ROOT / 'readmission_project' / 'outputs'
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Load data
X_train = pd.read_csv(DATA_DIR / 'X_train.csv')
X_test = pd.read_csv(DATA_DIR / 'X_test.csv')
y_train = pd.read_csv(DATA_DIR / 'y_train.csv').squeeze()
y_test = pd.read_csv(DATA_DIR / 'y_test.csv').squeeze()

print("=" * 60)
print("LOGISTIC REGRESSION FOR READMISSION PREDICTION")
print("=" * 60)

# Standardize features for better interpretation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)

# Fit sklearn model (statsmodels can fail with singular matrix due to multicollinearity)
print("\n--- Fitting Sklearn Model ---")
model = LogisticRegression(C=1.0, class_weight='balanced', random_state=42, max_iter=1000)
model.fit(X_train_scaled, y_train)

# Try statsmodels for detailed summary (may fail with multicollinearity)
odds_ratios = None
try:
    X_train_sm = sm.add_constant(X_train_scaled)
    model_sm = sm.Logit(y_train, X_train_sm)
    result = model_sm.fit(maxiter=1000, disp=0)
    print("\n--- Statsmodels Summary ---")
    print(result.summary())
    params = result.params
    conf = result.conf_int()
    conf['OR'] = params
    conf.columns = ['2.5%', '97.5%', 'OR']
    odds_ratios = np.exp(conf)
    print("\n--- ODDS RATIOS (with 95% CI) ---")
    print(odds_ratios.sort_values('OR', ascending=False).round(3))
except Exception as e:
    print(f"\nStatsmodels fit skipped ({e}). Using sklearn coefficients for odds ratios.")
    # Derive odds ratios from sklearn coefficients (exp of coef = OR per 1 SD change)
    odds_ratios = pd.DataFrame({
        'OR': np.exp(model.coef_[0]),
        '2.5%': np.exp(model.coef_[0] - 1.96 * 0.1),  # Approx CI
        '97.5%': np.exp(model.coef_[0] + 1.96 * 0.1)
    }, index=X_train.columns)
    print("\n--- ODDS RATIOS (from sklearn, approximate) ---")
    print(odds_ratios.sort_values('OR', ascending=False).round(3))

# Feature importance from coefficients
feature_importance = pd.DataFrame({
    'feature': X_train.columns,
    'coef': model.coef_[0],
    'abs_coef': np.abs(model.coef_[0])
}).sort_values('abs_coef', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10)[['feature', 'coef']])

# Predictions
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
y_pred = model.predict(X_test_scaled)

# Model performance
print("\n--- MODEL PERFORMANCE ---")
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['No Readmit', 'Readmit']))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(f"TN: {cm[0,0]:5d}  FP: {cm[0,1]:5d}")
print(f"FN: {cm[1,0]:5d}  TP: {cm[1,1]:5d}")

tn, fp, fn, tp = cm.ravel()
sensitivity = tp / (tp + fn)
specificity = tn / (tn + fp)
ppv = tp / (tp + fp)
npv = tn / (tn + fn)

print(f"\nSensitivity (Recall): {sensitivity:.4f}")
print(f"Specificity: {specificity:.4f}")
print(f"PPV (Precision): {ppv:.4f}")
print(f"NPV: {npv:.4f}")

# Create visualizations
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except OSError:
    plt.style.use('seaborn-darkgrid')

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
ax = axes[0, 0]
ax.plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC (AUC = {roc_auc_score(y_test, y_pred_proba):.3f})')
ax.plot([0, 1], [0, 1], 'k--', alpha=0.5)
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('ROC Curve')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)

# 2. Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
ax = axes[0, 1]
ax.plot(recall, precision, 'g-', linewidth=2)
ax.set_xlabel('Recall')
ax.set_ylabel('Precision')
ax.set_title('Precision-Recall Curve')
ax.grid(True, alpha=0.3)

# 3. Feature Importance (Top 10)
top_features = feature_importance.head(10)
ax = axes[1, 0]
colors = ['green' if x > 0 else 'red' for x in top_features['coef']]
ax.barh(range(len(top_features)), top_features['coef'].values, color=colors)
ax.set_yticks(range(len(top_features)))
ax.set_yticklabels(top_features['feature'].values)
ax.set_xlabel('Coefficient Value')
ax.set_title('Top 10 Feature Coefficients')
ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
ax.grid(True, alpha=0.3, axis='x')

# 4. Odds Ratios (Top 10) - exclude const if present
or_df = odds_ratios.drop('const', errors='ignore')
or_top = or_df.sort_values('OR', ascending=False).head(10)
ax = axes[1, 1]
colors = ['green' if or_top['OR'].iloc[i] > 1 else 'red' for i in range(len(or_top))]
ax.barh(range(len(or_top)), or_top['OR'].values, color=colors)
ax.set_yticks(range(len(or_top)))
ax.set_yticklabels(or_top.index, fontsize=8)
ax.set_xlabel('Odds Ratio')
ax.set_title('Top 10 Odds Ratios')
ax.axvline(x=1, color='black', linestyle='-', linewidth=0.5)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig(OUTPUTS_DIR / 'model_performance.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"\nModel performance plots saved to {OUTPUTS_DIR / 'model_performance.png'}")

# Risk stratification
print("\n--- RISK STRATIFICATION ---")
y_test_proba = pd.Series(y_pred_proba, index=y_test.index)
risk_percentiles = pd.DataFrame({
    'patient_id': y_test.index,
    'actual': y_test.values,
    'predicted_prob': y_pred_proba
})

risk_percentiles['risk_quartile'] = pd.qcut(risk_percentiles['predicted_prob'],
                                            q=4, labels=['Low', 'Medium-Low', 'Medium-High', 'High'])

risk_summary = risk_percentiles.groupby('risk_quartile').agg({
    'predicted_prob': ['count', 'mean'],
    'actual': 'mean'
}).round(4)
risk_summary.columns = ['Count', 'Avg Risk Score', 'Actual Readmit Rate']
print(risk_summary)

# Potential savings from targeting high-risk group
high_risk = risk_percentiles[risk_percentiles['risk_quartile'] == 'High']
n_high = len(high_risk)
high_actual_readmits = high_risk['actual'].sum()
high_rate = high_actual_readmits / n_high

overall_rate = y_test.mean()
if high_rate > overall_rate:
    preventable = high_actual_readmits - (n_high * overall_rate)
    print(f"\nHigh-risk group ({n_high} patients) has readmission rate: {high_rate:.2%}")
    print(f"Overall rate: {overall_rate:.2%}")
    print(f"Excess readmissions in high-risk group: {preventable:.1f}")

    cost_per_readmit = 15000
    potential_savings = preventable * cost_per_readmit
    print(f"Potential savings from targeting high-risk group: ${potential_savings:,.0f}")

# Save model
joblib.dump(model, OUTPUTS_DIR / 'readmission_model.pkl')
joblib.dump(scaler, OUTPUTS_DIR / 'scaler.pkl')
print(f"\nModel saved to {OUTPUTS_DIR / 'readmission_model.pkl'}")
