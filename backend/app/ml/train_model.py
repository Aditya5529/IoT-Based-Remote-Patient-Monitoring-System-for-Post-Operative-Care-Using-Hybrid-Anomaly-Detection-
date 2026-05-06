import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from app.ml.feature_engineering import normalize_vital_vector

# Mock data generator for training (since DB might be empty)
def generate_training_data(n_samples=1000):
    # WESAD-like 'Normal' Data
    # HR: 60-100, SpO2: 95-100, Temp: 36.5-37.5
    rng = np.random.RandomState(42)
    
    X_train = []
    
    for _ in range(n_samples):
        # Generate a "Normal" vector
        hr = rng.normal(80, 10)
        spo2 = rng.normal(97, 2)
        temp = rng.normal(37, 0.5)
        glucose = rng.normal(100, 20)
        bp_sys = rng.normal(120, 10)
        bp_dia = rng.normal(80, 5)
        
        # Fixed order matches feature_engineering
        vector = [hr, min(spo2, 100), temp, glucose, bp_sys, bp_dia]
        X_train.append(vector)
        
    return np.array(X_train)

def train_and_save():
    print("🤖 Training ML Anomaly Detection Model...")
    
    X_train = generate_training_data()
    
    # Isolation Forest
    # contamination='auto' or low value like 0.05
    clf = IsolationForest(random_state=42, contamination=0.05)
    clf.fit(X_train)
    
    # Save
    artifact_path = os.path.join(os.path.dirname(__file__), "artifacts")
    os.makedirs(artifact_path, exist_ok=True)
    model_path = os.path.join(artifact_path, "model.joblib")
    
    joblib.dump(clf, model_path)
    print(f"✅ Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save()
