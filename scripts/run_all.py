#!/usr/bin/env python
"""
Master execution script — runs full pipeline: 01 load → 02–04 SQL → 05 prepare → 06 model → 07 financial → 08 dashboard SQL.
Run from repository root: python scripts/run_all.py
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
SCRIPTS_DIR = ROOT / 'scripts'
DB = DATA_DIR / 'readmissions.db'

def run_python(script: str):
    subprocess.run([sys.executable, str(SCRIPTS_DIR / script)], cwd=str(ROOT), check=True)

def run_sql(script: str):
    with open(SCRIPTS_DIR / script) as f:
        sql = f.read()
    import sqlite3
    conn = sqlite3.connect(str(DB))
    conn.executescript(sql)
    conn.close()

print("=" * 70)
print("HOSPITAL READMISSION REDUCTION INITIATIVE — FULL PIPELINE")
print("=" * 70)

steps = [
    ("01_load_data.py", lambda: run_python("01_load_data.py")),
    ("03_readmission_cohorts.sql", lambda: run_sql("03_readmission_cohorts.sql")),
    ("02_explore_data.sql", lambda: run_sql("02_explore_data.sql")),
    ("04_risk_factor_analysis.sql", lambda: run_sql("04_risk_factor_analysis.sql")),
    ("05_prepare_model_data.py", lambda: run_python("05_prepare_model_data.py")),
    ("06_logistic_regression.py", lambda: run_python("06_logistic_regression.py")),
    ("07_financial_analysis.py", lambda: run_python("07_financial_analysis.py")),
    ("08_dashboard_data.sql", lambda: run_sql("08_dashboard_data.sql")),
]
for i, (name, fn) in enumerate(steps, 1):
    print(f"\n[{i}/{len(steps)}] {name} ...")
    start = time.time()
    fn()
    print(f"  ✓ {time.time()-start:.1f}s")

print("\n" + "=" * 70)
print("✅ PIPELINE COMPLETE. Outputs in outputs/ and outputs/visuals/ and outputs/model/")
print("=" * 70)
