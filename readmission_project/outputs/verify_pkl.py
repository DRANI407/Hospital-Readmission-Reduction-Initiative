"""
Verify readmission_model.pkl and scaler.pkl: existence, size, and load test.
Run from project root: python readmission_project/outputs/verify_pkl.py
"""
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
model_path = OUT / 'readmission_model.pkl'
scaler_path = OUT / 'scaler.pkl'

def main():
    print("=" * 50)
    print("Checking .pkl files")
    print("=" * 50)

    # 1. Existence and size
    for name, p in [('readmission_model.pkl', model_path), ('scaler.pkl', scaler_path)]:
        exists = p.exists()
        size = p.stat().st_size if exists else 0
        print(f"\n1. {name}")
        print(f"   Exists: {exists}")
        print(f"   Size:   {size} bytes")
        if not exists or size == 0:
            print("   -> File missing or empty. Re-run: python scripts/03_logistic_regression.py")
            return 1

    # 2. Load with joblib (how the model was saved)
    print("\n2. Load with joblib (recommended)")
    try:
        import joblib
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("   readmission_model.pkl ->", type(model).__name__, "OK")
        print("   scaler.pkl            ->", type(scaler).__name__, "OK")
        print("   Model coef shape:", model.coef_.shape)
    except Exception as e:
        print("   FAILED:", e)
        return 1

    # 3. Try pickle (often works for joblib-saved sklearn objects, but not guaranteed)
    print("\n3. Load with pickle (optional)")
    try:
        import pickle
        with open(model_path, 'rb') as f:
            m2 = pickle.load(f)
        print("   readmission_model.pkl -> pickle.load OK")
    except Exception as e:
        print("   pickle.load failed (expected for some joblib dumps):", e)

    print("\n" + "=" * 50)
    print("Summary: Use joblib.load() in Python to load these files.")
    print("Do not open .pkl in a text editor — they are binary.")
    print("=" * 50)
    return 0

if __name__ == '__main__':
    sys.exit(main())
