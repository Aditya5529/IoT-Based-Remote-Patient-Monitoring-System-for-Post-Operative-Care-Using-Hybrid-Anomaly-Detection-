import requests
from datetime import datetime
import time
import uuid

# Hardcode patient user_id from seeded DB (patient@rpm.com)
pat_id = None
try:
    # Login to get token
    res = requests.post("http://localhost:8000/api/v1/auth/login", data={"username":"patient@rpm.com","password":"pat123"})
    token = res.json()["access_token"]
    # Get me
    res_me = requests.get("http://localhost:8000/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    pat_id = res_me.json()["id"]
except Exception as e:
    print("Could not login", e)

print(f"Got Patient ID: {pat_id}")

t1 = time.time()
res = requests.post('http://localhost:8000/api/v1/vitals/', headers={"Authorization": f"Bearer {token}"}, json={
    "vital_type": "heart_rate",
    "value": 160,
    "unit": "bpm",
    "patient_id": pat_id,
    "ts": datetime.utcnow().isoformat()
})
t2 = time.time()
print("Submission Status:", res.status_code)
print("Submission Result:", res.text)
print(f"ML Engine + API Pipeline took {(t2-t1)*1000:.2f} ms")
