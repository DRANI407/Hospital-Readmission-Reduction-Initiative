#!/usr/bin/env python
"""
Master script to run all analyses for Project 1
"""

import subprocess
import sys
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / 'readmission_project' / 'data'
OUTPUTS_DIR = PROJECT_ROOT / 'readmission_project' / 'outputs'
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'

print("=" * 70)
print("PROJECT 1: VALUE-BASED CARE READMISSION ANALYSIS")
print("=" * 70)

# Create directories if they don't exist
for dir_name in ['readmission_project/data', 'readmission_project/outputs', 'readmission_project/dashboard', 'scripts']:
    os.makedirs(PROJECT_ROOT / dir_name, exist_ok=True)

# Step 1: Load data
print("\n[1/7] Loading data into SQLite database...")
start = time.time()
subprocess.run([sys.executable, str(SCRIPTS_DIR / '01_load_data.py')], cwd=str(PROJECT_ROOT), check=True)
print(f"✓ Completed in {time.time()-start:.1f} seconds")

# Step 2: Run SQL cohort analysis
print("\n[2/7] Running SQL cohort analysis...")
start = time.time()
import sqlite3

conn = sqlite3.connect(str(DATA_DIR / 'readmissions.db'))
with open(SCRIPTS_DIR / '02_readmission_cohorts.sql', 'r') as f:
    conn.executescript(f.read())
conn.close()
print(f"✓ Completed in {time.time()-start:.1f} seconds")

# Step 3: Prepare model data
print("\n[3/7] Preparing data for modeling...")
start = time.time()
subprocess.run([sys.executable, str(SCRIPTS_DIR / '02_prepare_model_data.py')], cwd=str(PROJECT_ROOT), check=True)
print(f"✓ Completed in {time.time()-start:.1f} seconds")

# Step 4: Run logistic regression
print("\n[4/7] Building predictive model...")
start = time.time()
subprocess.run([sys.executable, str(SCRIPTS_DIR / '03_logistic_regression.py')], cwd=str(PROJECT_ROOT), check=True)
print(f"✓ Completed in {time.time()-start:.1f} seconds")

# Step 5: Run financial analysis
print("\n[5/7] Calculating financial impact...")
start = time.time()
subprocess.run([sys.executable, str(SCRIPTS_DIR / '04_financial_impact_analysis.py')], cwd=str(PROJECT_ROOT), check=True)
print(f"✓ Completed in {time.time()-start:.1f} seconds")

# Step 6: Build dashboard
print("\n[6/7] Building readmission dashboard...")
start = time.time()
result = subprocess.run(
    [sys.executable, str(PROJECT_ROOT / 'readmission_project' / 'dashboard' / 'build_dashboard.py')],
    cwd=str(PROJECT_ROOT),
    capture_output=True,
    text=True,
)
print(f"✓ Completed in {time.time()-start:.1f} seconds" if result.returncode == 0 else f"  Skipped: {result.stderr or 'dashboard error'}")

# Step 7: Done
print("\n[7/7] All steps complete.")

print("\n" + "=" * 70)
print("✅ PROJECT COMPLETE!")
print("=" * 70)
print("\nOutput files generated:")
print("  📊 readmission_project/outputs/model_performance.png - Model performance visualizations")
print("  💰 readmission_project/outputs/financial_analysis_dashboard.png - Financial analysis charts")
print("  📈 readmission_project/outputs/financial_analysis_results.xlsx (or .csv) - Detailed financial data")
print("  📝 readmission_project/outputs/impact_statement.txt - Executive impact statement")
print("  🤖 readmission_project/outputs/readmission_model.pkl - Trained prediction model")
print("\nNext steps:")
print("  1. Open Tableau and connect to readmission_project/data/readmissions.db")
print("  2. Build dashboard using readmission_project/dashboard/ (TABLEAU_DASHBOARD_SPEC.md, tableau_extracts.sql)")
print("  3. Present readmission_project/outputs/EXECUTIVE_SUMMARY.md to stakeholders")
print("=" * 70)
