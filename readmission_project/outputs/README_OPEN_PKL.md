# How to Open / Use .pkl Files

## Important: Don’t open .pkl in a text editor

- **`.pkl` files are binary.** Opening them in Cursor, VS Code, or Notepad shows unreadable characters or “garbage” — that’s normal.
- You **cannot** view or edit the model by opening the file like a text file. You must load it in **Python**.

---

## 1. Check that the file exists and has content

From the project root:

```bash
ls -la readmission_project/outputs/readmission_model.pkl
```

You should see a non-zero size (e.g. ~1500 bytes). If the file is missing or 0 bytes, re-create it (see section 4).

---

## 2. Load with joblib (correct method for this project)

This model and scaler were saved with **joblib**. Use the same to load:

```python
import joblib
from pathlib import Path

out = Path('readmission_project/outputs')
model = joblib.load(out / 'readmission_model.pkl')
scaler = joblib.load(out / 'scaler.pkl')

# Quick check
print(type(model))   # <class 'sklearn.linear_model.LogisticRegression'>
print(model.coef_.shape)  # (1, 15)
```

---

## 3. Load with pickle (alternative)

`pickle` can sometimes load joblib-saved objects, but **joblib is preferred** for sklearn models (handles numpy arrays and compatibility better).

```python
import pickle

with open('readmission_project/outputs/readmission_model.pkl', 'rb') as f:
    model = pickle.load(f)
```

If you get errors, use `joblib.load()` instead.

---

## 4. If the file is corrupted or missing: re-create it

From the **project root** (the folder that contains `scripts/` and `readmission_project/`):

```bash
# Ensure train/test data exist (run if you get file-not-found)
python scripts/02_prepare_model_data.py

# Train and save model + scaler
python scripts/03_logistic_regression.py
```

This writes:

- `readmission_project/outputs/readmission_model.pkl`
- `readmission_project/outputs/scaler.pkl`

---

## 5. Verify everything works

Run the verification script from the project root:

```bash
python readmission_project/outputs/verify_pkl.py
```

It checks that both files exist, have content, and load correctly with joblib.

---

## Summary

| Goal                    | Action |
|-------------------------|--------|
| “Open” / inspect model  | Load in Python with `joblib.load(...)`, then use `model.coef_`, `model.intercept_`, etc. |
| Check file is valid     | Run `verify_pkl.py` |
| File missing/corrupt    | Run `02_prepare_model_data.py` then `03_logistic_regression.py` |
