import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def step(name):
    print(f"\n🔹 STEP: {name}")

def safe_json(r):
    try:
        return r.json()
    except:
        return {}

# 1. Register Patient
step("Register Patient")
pat_email = f"strict_pat_{int(time.time())}@test.com"
r = requests.post(f"{BASE_URL}/auth/register", json={
    "email": pat_email, "password": "password123", "full_name": "Strict Patient", "role": "patient"
})
print(f"Reg Status: {r.status_code}")
if r.status_code != 200: exit(1)
pat_id = safe_json(r)["id"]

# Login Patient
r = requests.post(f"{BASE_URL}/auth/login", data={"username": pat_email, "password": "password123"})
pat_token = safe_json(r)["access_token"]
pat_headers = {"Authorization": f"Bearer {pat_token}"}

# 2. Admin Login
step("Admin Login")
r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@rpm.com", "password": "admin123"})
if r.status_code != 200:
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@rpm.com", "password": "adminpassword"})
admin_token = safe_json(r)["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# 3. Get Doctor
step("Get/Create Doctor")
r = requests.get(f"{BASE_URL}/admin/doctors", headers=admin_headers)
docs = safe_json(r)
if not docs:
    # Create doctor
    doc_email = f"strict_doc_{int(time.time())}@rpm.com"
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": doc_email, "password": "password123", "full_name": "Strict Doctor", "role": "doctor"
    })
    doc_id = safe_json(r)["id"]
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": doc_email, "password": "password123"})
    doc_token = safe_json(r)["access_token"]
else:
    doc_id = docs[0]["id"]
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": docs[0]["email"], "password": "doc123"}) # Assumption
    if r.status_code != 200:
         # Try creating fresh one to be sure we have token
         doc_email = f"strict_doc_{int(time.time())}@rpm.com"
         r = requests.post(f"{BASE_URL}/auth/register", json={
             "email": doc_email, "password": "password123", "full_name": "Strict Doctor", "role": "doctor"
         })
         doc_id = safe_json(r)["id"]
         r = requests.post(f"{BASE_URL}/auth/login", data={"username": doc_email, "password": "password123"})
         doc_token = safe_json(r)["access_token"]
    else:
         doc_token = safe_json(r)["access_token"]

doc_headers = {"Authorization": f"Bearer {doc_token}"}
print(f"Doctor ID: {doc_id}")

# 4. blocked Message
step("Verify Blocked Message")
r = requests.post(f"{BASE_URL}/messages/", headers=pat_headers, json={"recipient_id": doc_id, "content": "Hello Blocked"})
print(f"Blocked Status: {r.status_code}")
if r.status_code != 403:
    print(f"❌ FAILED: msg allowed ({r.status_code})")
    exit(1)

# 5. Assign
step("Assign Patient")
r = requests.post(f"{BASE_URL}/admin/assign-doctor", headers=admin_headers, json={
    "doctor_id": doc_id, "patient_id": pat_id
})
print(f"Assign Status: {r.status_code} Body: {r.text}")
if r.status_code != 200: exit(1)

# 6. Verify List
step("Verify Doctor List")
r = requests.get(f"{BASE_URL}/doctor/my-patients", headers=doc_headers)
print(f"My Patients: {r.text}")
pats = safe_json(r)
if not any(p["id"] == pat_id for p in pats):
    print("❌ FAILED: Patient not in list")
    exit(1)

# 7. Allowed Message
step("Verify Allowed Message")
r = requests.post(f"{BASE_URL}/messages/", headers=pat_headers, json={"recipient_id": doc_id, "content": "Hello Allowed"})
print(f"Msg Status: {r.status_code}")
if r.status_code != 200:
    print(f"❌ FAILED: msg blocked ({r.text})")
    exit(1)

print("\n✅ FINAL SUCCESS")
