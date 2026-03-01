"""
06_logistic_regression.py — Train readmission prediction model. Writes to outputs/model/ and outputs/visuals/.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix, roc_curve, precision_recall_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib
import json
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
MODEL_DIR = OUTPUTS_DIR / 'model'
VISUALS_DIR = OUTPUTS_DIR / 'visuals'
MODEL_DIR.mkdir(parents=True, exist_ok=True)
VISUALS_DIR.mkdir(parents=True, exist_ok=True)

X_train = pd.read_csv(DATA_DIR / 'X_train.csv')
X_test = pd.read_csv(DATA_DIR / 'X_test.csv')
y_train = pd.read_csv(DATA_DIR / 'y_train.csv').squeeze()
y_test = pd.read_csv(DATA_DIR / 'y_test.csv').squeeze()

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)

model = LogisticRegression(C=1.0, class_weight='balanced', random_state=42, max_iter=1000)
model.fit(X_train_scaled, y_train)

odds_ratios = pd.DataFrame({'OR': np.exp(model.coef_[0])}, index=X_train.columns)
feature_importance = pd.DataFrame({
    'feature': X_train.columns,
    'coef': model.coef_[0],
    'abs_coef': np.abs(model.coef_[0])
}).sort_values('abs_coef', ascending=False)

y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
y_pred = model.predict(X_test_scaled)
auc = roc_auc_score(y_test, y_pred_proba)
print(f"ROC-AUC: {auc:.4f}")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
axes[0,0].plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC (AUC = {auc:.3f})')
axes[0,0].plot([0, 1], [0, 1], 'k--', alpha=0.5)
axes[0,0].set_xlabel('False Positive Rate'); axes[0,0].set_ylabel('True Positive Rate')
axes[0,0].set_title('ROC Curve'); axes[0,0].legend(); axes[0,0].grid(True, alpha=0.3)
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
axes[0,1].plot(recall, precision, 'g-', linewidth=2)
axes[0,1].set_xlabel('Recall'); axes[0,1].set_ylabel('Precision')
axes[0,1].set_title('Precision-Recall Curve'); axes[0,1].grid(True, alpha=0.3)
top = feature_importance.head(10)
axes[1,0].barh(range(len(top)), top['coef'].values, color=['green' if x > 0 else 'red' for x in top['coef']])
axes[1,0].set_yticks(range(len(top))); axes[1,0].set_yticklabels(top['feature'].values)
axes[1,0].set_xlabel('Coefficient'); axes[1,0].set_title('Top 10 Coefficients'); axes[1,0].axvline(x=0, color='k', lw=0.5)
or_top = odds_ratios.sort_values('OR', ascending=False).head(10)
axes[1,1].barh(range(len(or_top)), or_top['OR'].values, color=['green' if x > 1 else 'red' for x in or_top['OR']])
axes[1,1].set_yticks(range(len(or_top))); axes[1,1].set_yticklabels(or_top.index, fontsize=8)
axes[1,1].set_xlabel('Odds Ratio'); axes[1,1].set_title('Top 10 Odds Ratios'); axes[1,1].axvline(x=1, color='k', lw=0.5)
plt.tight_layout()
plt.savefig(VISUALS_DIR / 'model_performance.png', dpi=150, bbox_inches='tight')
plt.close()

joblib.dump(model, MODEL_DIR / 'readmission_model.pkl')
joblib.dump(scaler, MODEL_DIR / 'scaler.pkl')
metadata = {
    'model_type': 'LogisticRegression',
    'n_features': len(X_train.columns),
    'feature_names': list(X_train.columns),
    'intercept': float(model.intercept_[0]),
    'roc_auc': float(auc),
    'n_train': int(len(X_train)),
    'n_test': int(len(X_test)),
}
with open(MODEL_DIR / 'model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

feature_importance.to_csv(OUTPUTS_DIR / 'feature_importance.csv', index=False)
pd.DataFrame({'feature': X_train.columns, 'coefficient': model.coef_[0], 'odds_ratio': np.exp(model.coef_[0])}).to_csv(OUTPUTS_DIR / 'model_coefficients.csv', index=False)
print(f"Model saved to {MODEL_DIR}; visuals to {VISUALS_DIR}")
