import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# Login Admin
r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@rpm.com", "password": "admin123"})
if r.status_code != 200:
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@rpm.com", "password": "adminpassword"})
print(f"Admin Login Status: {r.status_code}")
token = r.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Get Doctor/Patient
docs = requests.get(f"{BASE_URL}/admin/doctors", headers=headers).json()
pats = requests.get(f"{BASE_URL}/admin/patients", headers=headers).json()

if not docs or not pats:
    print("Missing doctors or patients")
    exit(1)

doc_id = docs[0]["id"]
pat_id = pats[0]["id"]
print(f"Assigning {pat_id} to {doc_id}")

r = requests.post(f"{BASE_URL}/admin/assign-doctor", headers=headers, json={"doctor_id": doc_id, "patient_id": pat_id})
print(f"Assignment Status: {r.status_code}")
print(f"Response Body: {r.text}")
