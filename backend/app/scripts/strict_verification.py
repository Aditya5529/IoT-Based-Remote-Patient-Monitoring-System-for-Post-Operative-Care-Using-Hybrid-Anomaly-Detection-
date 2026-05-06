import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def step(name):
    print(f"\n🔹 STEP: {name}")

def fail(msg):
    print(f"❌ FAILED: {msg}")
    exit(1)

def success(msg):
    print(f"✅ {msg}")

# 1. Register Patient
step("Register Patient")
pat_email = f"strict_pat_{int(time.time())}@test.com"
pat_pass = "password123"
r = requests.post(f"{BASE_URL}/auth/register", json={
    "email": pat_email, "password": pat_pass, "full_name": "Strict Patient", "role": "patient"
})
if r.status_code != 200: fail(f"Registration failed: {r.text}")
pat_data = r.json()
pat_id = pat_data["id"]
success(f"Registered Patient {pat_email} (ID: {pat_id})")

# Login Patient
r = requests.post(f"{BASE_URL}/auth/login", data={"username": pat_email, "password": pat_pass})
pat_token = r.json()["access_token"]
pat_headers = {"Authorization": f"Bearer {pat_token}"}

# 2. Get Admin Token
step("Get Admin Token")
# Try default seed password first
try_pass = "admin123"
r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@rpm.com", "password": try_pass})
if r.status_code != 200: 
    print("⚠️ Default admin login failed, trying 'adminpassword'...")
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@rpm.com", "password": "adminpassword"})

if r.status_code != 200:
    # All defaults failed, creating test admin not allowed usually without superuser.
    # We must rely on existence. Or maybe we can register an admin? Unlikely.
    # Let's hope admin123 works as per recent seed check.
    fail(f"Admin login failed. Reset DB if needed. Status: {r.status_code}")

admin_token = r.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# 3. Get Doctor (Assuming doctor@rpm.com exists)
step("Get Doctor Info")
r = requests.get(f"{BASE_URL}/admin/doctors", headers=admin_headers)
docs = r.json()
if not docs: fail("No doctors found")
doc = docs[0]
doc_id = doc["id"]
# Login Doctor
r = requests.post(f"{BASE_URL}/auth/login", data={"username": doc["email"], "password": "doctorpassword"}) # Assuming default password or we reset it
if r.status_code != 200: 
    # Try creating a fresh doctor if login fails
    step("Creating Fresh Doctor for Test")
    doc_email = f"strict_doc_{int(time.time())}@rpm.com"
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": doc_email, "password": "password123", "full_name": "Strict Doctor", "role": "doctor"
    })
    doc_id = r.json()["id"]
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": doc_email, "password": "password123"})
    doc_token = r.json()["access_token"]
else:
    doc_token = r.json()["access_token"]

doc_headers = {"Authorization": f"Bearer {doc_token}"}
success(f"Doctor Ready (ID: {doc_id})")

# 4. Verify No Access Before Assignment
step("Verify No Access Before Assignment")
r = requests.post(f"{BASE_URL}/messages/", headers=pat_headers, json={"recipient_id": doc_id, "content": "Hello unassigned"})
if r.status_code == 403:
    success("Correctly blocked messaging before assignment")
else:
    fail(f"Should have blocked unassigned message! Status: {r.status_code}")

# 5. Admin Assign
step("Admin Assigns Patient to Doctor")
r = requests.post(f"{BASE_URL}/admin/assign-doctor", headers=admin_headers, json={
    "doctor_id": doc_id, "patient_id": pat_id
})
if r.status_code != 200: fail(f"Assignment failed: {r.text}")
success("Assignment Successful")

# 6. Verify Doctor Sees Patient
step("Verify Doctor Sees Patient in List")
r = requests.get(f"{BASE_URL}/doctor/my-patients", headers=doc_headers)
my_patients = r.json()
if any(p["id"] == pat_id for p in my_patients):
    success("Patient found in Doctor's My Patients list")
else:
    fail("Patient NOT found in Doctor's list")

# 7. Messaging Verification (Success)
step("Verify Messaging After Assignment")
r = requests.post(f"{BASE_URL}/messages/", headers=pat_headers, json={"recipient_id": doc_id, "content": "Hello Assigned Doctor"})
if r.status_code == 200:
    success("Patient sent message to Doctor")
else:
    fail(f"Message failed: {r.text}")

r = requests.post(f"{BASE_URL}/messages/", headers=doc_headers, json={"recipient_id": pat_id, "content": "Hello Patient"})
if r.status_code == 200:
    success("Doctor replied to Patient")
else:
    fail(f"Reply failed: {r.text}")

# 8. Alert Verification
step("Verify Alert Generation")
# Create Critical Vital
r = requests.post(f"{BASE_URL}/vitals/", headers=pat_headers, json={
    "vital_type": "heart_rate", "value": 150, "unit": "bpm", "ts": "2024-01-01T12:00:00Z"
})
if r.status_code != 200: fail("Vital creation failed")
success("High HR Vital Submitted")

# Doctor Checks Alerts
r = requests.get(f"{BASE_URL}/alerts/", headers=doc_headers)
alerts = r.json()
# Filter for our patient
my_alerts = [a for a in alerts if a["patient_id"] == pat_id]
if my_alerts:
    success(f"Alert Found: {my_alerts[0]['reason']}")
else:
    fail("No alert generated for Critical Vital!")

print("\n🎉 ALL STRICT VERIFICATION STEPS PASSED")
