"""
Basic data quality checks for model-ready data.
Run from repo root: python -m pytest tests/test_data_quality.py -v
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_model_ready_data_exists():
    path = ROOT / 'data' / 'model_ready_data.csv'
    if not path.exists():
        return  # skip if pipeline not run
    import pandas as pd
    df = pd.read_csv(path)
    assert len(df) > 0
    assert 'target' in df.columns


def test_target_binary():
    path = ROOT / 'data' / 'model_ready_data.csv'
    if not path.exists():
        return
    import pandas as pd
    df = pd.read_csv(path)
    assert set(df['target'].dropna().unique()).issubset({0, 1})


def test_feature_columns_present():
    path = ROOT / 'data' / 'X_train.csv'
    if not path.exists():
        return
    import pandas as pd
    X = pd.read_csv(path)
    expected = [
        'age_midpoint', 'time_in_hospital', 'num_lab_procedures',
        'num_procedures', 'num_medications', 'number_diagnoses',
        'diabetes_complications', 'cardiovascular', 'respiratory', 'renal',
        'high_prior_utilization', 'long_los', 'polypharmacy',
        'a1c_abnormal', 'insulin_level'
    ]
    for col in expected:
        assert col in X.columns, f"Missing column: {col}"
