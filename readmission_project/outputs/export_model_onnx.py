"""
Export readmission model + scaler pipeline to ONNX for production use.
Requires: pip install skl2onnx onnxruntime
"""
from pathlib import Path
import joblib

OUT = Path(__file__).resolve().parent
model = joblib.load(OUT / 'readmission_model.pkl')
scaler = joblib.load(OUT / 'scaler.pkl')

try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
except ImportError:
    print("Install: pip install skl2onnx onnxruntime")
    raise

# ONNX expects a pipeline; wrap scaler + model in a single pipeline for export
from sklearn.pipeline import Pipeline
pipe = Pipeline([('scaler', scaler), ('clf', model)])

n_features = 15
initial_type = [('float_input', FloatTensorType([None, n_features]))]
onnx_model = convert_sklearn(pipe, initial_types=initial_type, target_opset=12)

out_path = OUT / 'readmission_model.onnx'
with open(out_path, 'wb') as f:
    f.write(onnx_model.SerializeToString())
print(f"Exported to {out_path}")

# Quick check
import onnxruntime as ort
sess = ort.InferenceSession(str(out_path))
print("ONNX session created successfully. Input name:", sess.get_inputs()[0].name)
