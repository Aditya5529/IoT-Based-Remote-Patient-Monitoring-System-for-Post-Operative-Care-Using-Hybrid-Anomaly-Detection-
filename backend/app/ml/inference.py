import os
import joblib
import numpy as np
from app.ml.feature_engineering import normalize_vital_vector

_MODEL = None

def load_model():
    global _MODEL
    try:
        path = os.path.join(os.path.dirname(__file__), "artifacts", "model.joblib")
        if os.path.exists(path):
            _MODEL = joblib.load(path)
            print("✅ ML Model loaded successfully.")
        else:
            print("⚠️ ML Model artifact not found. Inference will be skipped.")
    except Exception as e:
        print(f"❌ Failed to load ML model: {e}")

def predict_anomaly(vital_dict):
    """
    Input: dict {'heart_rate': 80, ...}
    Output: (is_anomaly: bool, anomaly_score: float)
    """
    global _MODEL
    if _MODEL is None:
        load_model()
        if _MODEL is None:
            return False, 0.0
            
    try:
        # Preprocess
        vector = normalize_vital_vector(vital_dict)
        
        # Predict
        # IsolationForest: 1 = normal, -1 = anomaly
        pred = _MODEL.predict(vector)[0]
        
        # Decision Function: negative values are anomalies, positive are normal
        score = _MODEL.decision_function(vector)[0] 
        
        # We transform score to a "Severity" metric?
        # Lower score = more anomalous.
        
        is_anomaly = True if pred == -1 else False
        
        return is_anomaly, float(score)
        
    except Exception as e:
        print(f"Inference error: {e}")
        return False, 0.0
