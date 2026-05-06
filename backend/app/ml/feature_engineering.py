import pandas as pd
import numpy as np

def create_features(vitals_df):
    """
    Input: DataFrame with columns: [ts, vital_type, value]
    Output: Dictionary or DataFrame row ready for inference
    
    For Review-1 we keep it simple:
    Feature vector = [HR, SpO2, Temp, Glucose, SysBP, DiaBP]
    
    If 'vitals_df' is a single dictionary (inference time), we just structure it.
    If 'vitals_df' is historical data for training, we pivot it.
    """
    
    # If training (historical dataframe)
    if isinstance(vitals_df, pd.DataFrame):
        # Pivot to get one row per timestamp (bucketing by activity or time window)
        # This is complex for raw stream.
        # SIMPLIFICATION: We assume the simulator outputs blocks of vitals close in time.
        # But for outlier detection on SINGLE vital, we might just look at Uni-variate or Multi-variate if available.
        # Let's pivot by 'vital_type' and forward fill
        
        # Resample to 1-minute intervals?
        # vitals_df['ts'] = pd.to_datetime(vitals_df['ts'])
        # pivoted = vitals_df.pivot_table(index='ts', columns='vital_type', values='value')
        # pivoted = pivoted.resample('1T').mean().ffill()
        return vitals_df # Placeholder for training script to handle
        
    return None

def normalize_vital_vector(vital_dict):
    """
    Takes a snapshot of latest vitals for a patient.
    {'heart_rate': 80, 'spo2': 98, ...}
    Returns list in fixed order.
    """
    order = ['heart_rate', 'spo2', 'temperature', 'glucose', 'blood_pressure_sys', 'blood_pressure_dia']
    vector = []
    for k in order:
        val = vital_dict.get(k, 0) # 0 or NaN? 0 is bad for ML.
        # If missing, maybe use simple imputation (normal value)
        if not val:
            if k == 'spo2': val = 98
            elif k == 'temperature': val = 37.0
            else: val = 0 # Dangerous but IsolationForest might handle
        vector.append(val)
    return [vector]
