import time
import random
import requests
from uuid import UUID
import argparse

import os

# Configuration
API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api/v1/iot/vitals")
DEVICE_ID = os.environ.get("IOT_DEVICE_ID", "esp32-mock-device-01")
DEVICE_SECRET = os.environ.get("IOT_DEVICE_SECRET", "secret123")

def generate_vitals(patient_id: str, anomaly_prob: float = 0.1):
    is_anomaly = random.random() < anomaly_prob
    
    if is_anomaly:
        # Generate anomalous data
        anomaly_type = random.choice(["high_hr", "low_hr", "low_spo2", "high_temp"])
        if anomaly_type == "high_hr":
            hr = random.uniform(125, 180)
            spo2 = random.uniform(95, 99)
            temp = random.uniform(36.5, 37.2)
        elif anomaly_type == "low_hr":
            hr = random.uniform(35, 45)
            spo2 = random.uniform(95, 99)
            temp = random.uniform(36.5, 37.2)
        elif anomaly_type == "low_spo2":
            hr = random.uniform(80, 110)
            spo2 = random.uniform(85, 90)
            temp = random.uniform(36.5, 37.2)
        else:
            hr = random.uniform(80, 110)
            spo2 = random.uniform(95, 99)
            temp = random.uniform(38.5, 40.5)
        print(f"⚠️ Generated ANOMALY: {anomaly_type}")
    else:
        # Generate normal data
        hr = random.uniform(60, 90)
        spo2 = random.uniform(96, 100)
        temp = random.uniform(36.1, 37.2)
        
    payload = {
        "device_id": DEVICE_ID,
        "patient_id": patient_id,
        "heart_rate": round(hr, 1),
        "avg_bpm": round(hr, 1),
        "spo2": round(spo2, 1),
        "ir_value": random.randint(100000, 150000),
        "temperature": round(temp, 1),
        "accel_x": random.uniform(50, 150),
        "gyro_x": random.uniform(20, 80),
        "source": "esp32_mock"
    }
    return payload

def stream_data(patient_id: str):
    print(f"🚀 Starting Mock IoT Stream for patient {patient_id}")
    print(f"Endpoint: {API_URL}")
    
    headers = {
        "X-Device-Secret": DEVICE_SECRET,
        "Content-Type": "application/json"
    }
    
    try:
        while True:
            payload = generate_vitals(patient_id)
            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    print(f"✅ Sent successfully: HR={payload['heart_rate']}, SpO2={payload['spo2']}, Temp={payload['temperature']}")
                else:
                    print(f"❌ Failed to send: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error: {e}")
                
            time.sleep(random.uniform(3.0, 5.0))
    except KeyboardInterrupt:
        print("\n🛑 Stream stopped by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock IoT Vital Streamer")
    parser.add_argument("patient_id", type=str, help="UUID of the patient to map the device to")
    args = parser.parse_args()
    stream_data(args.patient_id)
