# Model files (.pkl)

## Why you can't "open" them in an editor

`readmission_model.pkl` and `scaler.pkl` are **binary** files (serialized Python objects). They are not text, so opening them in Cursor/VS Code or a text editor will show unreadable characters or "binary" — that is expected and does **not** mean they are corrupted.

## 1. Check that the files are valid

From the **project root**:

```bash
python readmission_project/outputs/verify_model.py
```

You should see: `All checks passed. Model files are valid.`

## 2. Load and use in Python

**With joblib (recommended for sklearn):**

```python
import joblib
from pathlib import Path

OUTPUTS = Path('readmission_project/outputs')
model = joblib.load(OUTPUTS / 'readmission_model.pkl')
scaler = joblib.load(OUTPUTS / 'scaler.pkl')

# Example: one row of 15 features (same order as training)
import pandas as pd
X = pd.DataFrame([[...]], columns=feature_cols)  # your feature columns
X_scaled = scaler.transform(X)
prob = model.predict_proba(X_scaled)[:, 1]
pred = model.predict(X_scaled)
```

**With pickle (standard library):**

```python
import pickle
with open('readmission_project/outputs/readmission_model.pkl', 'rb') as f:
    model = pickle.load(f)
```

Full example script: `readmission_project/outputs/load_model_example.py`

## 3. Joblib vs pickle

| | joblib | pickle |
|---|--------|--------|
| **Use case** | Sklearn, numpy, large arrays | Any Python object |
| **Compression** | Optional (e.g. `compress=3`) | No |
| **Our files** | Saved with `joblib.dump()` | Can load with either |
| **Extension** | Often `.pkl` or `.joblib` | `.pkl` |

Both produce binary `.pkl` files. Always open them in Python (joblib or pickle), not in a text editor.

## 4. If you need to recreate the model

If the files were ever missing or corrupted, re-run the pipeline so the model is trained and saved again:

```bash
python run_all.py
```

Or only the modeling step:

```bash
python scripts/03_logistic_regression.py
```

This overwrites `readmission_model.pkl` and `scaler.pkl` in `readmission_project/outputs/`.
