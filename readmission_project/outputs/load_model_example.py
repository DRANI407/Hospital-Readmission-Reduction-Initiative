"""Load the readmission model and scaler. Run from project root."""
import joblib

model = joblib.load('readmission_project/outputs/readmission_model.pkl')
scaler = joblib.load('readmission_project/outputs/scaler.pkl')

print("Model:", type(model).__name__)
print("Coefficients shape:", model.coef_.shape)
print("Scaler:", type(scaler).__name__)
# Example: model.predict(X_scaled), model.predict_proba(X_scaled)[:, 1]
