import time
import random
import requests
import json
from datetime import datetime
import uuid

import os

API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api/v1")
PATIENT_ID = "00000000-0000-0000-0000-000000000000" # Placeholder, fetch via API or Seed

# We need to login as Admin/Doctor to get the patient ID or just hardcode the seed ID.
# Seed ID for Tony Stark (Patient)
PATIENT_EMAIL = os.environ.get("TEST_PATIENT_EMAIL", "patient@rpm.com")
PATIENT_PASSWORD = os.environ.get("TEST_PATIENT_PASSWORD", "pat123")

def get_token():
    try:
        response = requests.post(f"{API_URL}/auth/login", data={"username": PATIENT_EMAIL, "password": PATIENT_PASSWORD})
        if response.status_code == 200:
            return response.json()["access_token"]
        print(f"Login failed: {response.text}")
        return None
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def get_patient_id(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/users/me", headers=headers)
    if response.status_code == 200:
        return response.json()["id"]
    return None

def simulate_vitals(patient_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Base values
    hr = 70
    spo2 = 98
    temp = 37.0
    
    print(f"Starting simulation for patient {patient_id}...")
    
    while True:
        # Simulate Activity
        activity = random.choice(["sitting", "walking", "running", "resting"])
        
        # Adjust vitals based on activity
        if activity == "running":
            hr = random.randint(110, 150)
            temp += 0.1
        elif activity == "walking":
            hr = random.randint(90, 110)
        else:
            hr = random.randint(60, 85)
            temp = 37.0 + random.uniform(-0.2, 0.2)
        
        # Random fluctuations
        spo2 = max(90, min(100, 98 + random.randint(-2, 1)))
        
        # Occasional spike
        if random.random() < 0.05:
            hr += 20 
        
        vitals = [
            {"vital_type": "HR", "value": hr, "unit": "bpm"},
            {"vital_type": "SpO2", "value": spo2, "unit": "%"},
            {"vital_type": "Temp", "value": round(temp, 1), "unit": "C"},
        ]
        
        for v in vitals:
            payload = {
                "patient_id": patient_id,
                "ts": datetime.utcnow().isoformat(),
                "vital_type": v["vital_type"],
                "value": float(v["value"]),
                "unit": v["unit"],
                "source": "simulated",
                "activity_label": activity
            }
            try:
                res = requests.post(f"{API_URL}/vitals/ingest", json=payload, headers=headers)
                if res.status_code == 200:
                    print(f"[{activity}] Ingested {v['vital_type']}: {v['value']}")
                else:
                    print(f"Failed to ingest: {res.text}")
            except Exception as e:
                print(f"Error ingesting: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    # Wait for API to be ready
    token = None
    while not token:
        print("Waiting for API...")
        token = get_token()
        time.sleep(2)
    
    pid = get_patient_id(token)
    if pid:
        simulate_vitals(pid, token)
    else:
        print("Could not get patient ID")
