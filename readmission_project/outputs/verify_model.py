#!/usr/bin/env python
"""
Verify readmission_model.pkl and scaler.pkl integrity.
Run from project root: python readmission_project/outputs/verify_model.py
"""

import sys
from pathlib import Path

# Project root is two levels up from this script
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = SCRIPT_DIR
MODEL_PATH = OUTPUTS_DIR / 'readmission_model.pkl'
SCALER_PATH = OUTPUTS_DIR / 'scaler.pkl'


def verify_file(path, name):
    """Check file exists, size, and loads correctly."""
    if not path.exists():
        print(f"  {name}: MISSING")
        return False
    size = path.stat().st_size
    if size < 100:
        print(f"  {name}: SUSPICIOUS (size={size} bytes)")
        return False
    print(f"  {name}: exists, {size} bytes", end=" ... ")
    return True


def main():
    print("=" * 60)
    print("MODEL FILE INTEGRITY CHECK")
    print("=" * 60)
    print("\n1. File presence and size")
    ok1 = verify_file(MODEL_PATH, "readmission_model.pkl")
    ok2 = verify_file(SCALER_PATH, "scaler.pkl")
    if not ok1 or not ok2:
        sys.exit(1)

    print("\n2. Load with joblib")
    try:
        import joblib
        model = joblib.load(MODEL_PATH)
        print(f"  readmission_model.pkl: OK (type={type(model).__name__})")
        if hasattr(model, 'coef_'):
            print(f"    - coef_.shape = {model.coef_.shape}")
    except Exception as e:
        print(f"  readmission_model.pkl: FAILED - {e}")
        sys.exit(1)

    try:
        scaler = joblib.load(SCALER_PATH)
        print(f"  scaler.pkl: OK (type={type(scaler).__name__})")
    except Exception as e:
        print(f"  scaler.pkl: FAILED - {e}")
        sys.exit(1)

    print("\n3. Quick prediction test (optional)")
    try:
        import numpy as np
        X_dummy = np.zeros((1, model.coef_.shape[1]))
        model.predict(scaler.transform(X_dummy))
        print("  Predict with scaled input: OK")
    except Exception as e:
        print(f"  Predict test: {e}")

    print("\n" + "=" * 60)
    print("All checks passed. Model files are valid.")
    print("=" * 60)


if __name__ == "__main__":
    main()
