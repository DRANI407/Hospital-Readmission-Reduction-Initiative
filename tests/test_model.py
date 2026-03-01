"""
Basic tests for the readmission prediction model.
Run from repo root: python -m pytest tests/test_model.py -v
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_model_loads():
    import joblib
    model_path = ROOT / 'outputs' / 'model' / 'readmission_model.pkl'
    scaler_path = ROOT / 'outputs' / 'model' / 'scaler.pkl'
    if not model_path.exists():
        return  # skip if pipeline not run
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    assert model.coef_.shape[1] == 15
    assert scaler.mean_.shape[0] == 15


def test_predict_proba_shape():
    import joblib
    import numpy as np
    model_path = ROOT / 'outputs' / 'model' / 'readmission_model.pkl'
    scaler_path = ROOT / 'outputs' / 'model' / 'scaler.pkl'
    if not model_path.exists():
        return
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    X = np.zeros((5, 15))  # 5 rows, 15 features
    X_scaled = scaler.transform(X)
    proba = model.predict_proba(X_scaled)[:, 1]
    assert proba.shape == (5,)
    assert (proba >= 0).all() and (proba <= 1).all()
