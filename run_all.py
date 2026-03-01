#!/usr/bin/env python
"""Run full pipeline from repo root. Delegates to scripts/run_all.py."""
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'run_all.py')], cwd=str(ROOT), check=True)
