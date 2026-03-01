# Notebooks

Jupyter notebooks for **exploratory data analysis (EDA)** and ad-hoc analysis.

| Notebook | Description |
|----------|-------------|
| **01_eda_readmissions.ipynb** | Load model-ready data and SQLite; summarize readmission rate, demographics, and key risk factors. |

**Prerequisites:** Run the pipeline at least once so that `readmission_project/data/model_ready_data.csv` and `readmission_project/data/readmissions.db` exist. From repo root: `pip install -r requirements.txt` and `python run_all.py`.

**Kernel:** Use a Python environment that has `pandas`, `numpy`, `matplotlib`, `seaborn`, and (for SQL) `sqlite3` (stdlib).
