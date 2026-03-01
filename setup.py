"""
Hospital Readmission Reduction Initiative — Package setup.
Enables: pip install -e . (editable install from repo root).
"""
from setuptools import setup, find_packages

setup(
    name="hospital-readmission-reduction",
    version="1.0.0",
    description="Data-driven analytics for 30-day hospital readmission reduction and value-based care",
    author="Hospital Readmission Reduction Initiative",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests", "notebooks", "docs"]),
    install_requires=[
        "pandas>=1.3",
        "numpy>=1.21",
        "scikit-learn>=1.0",
        "matplotlib>=3.5",
        "seaborn>=0.12",
        "statsmodels>=0.13",
    ],
    extras_require={
        "excel": ["openpyxl"],
        "onnx": ["skl2onnx", "onnxruntime"],
    },
)
