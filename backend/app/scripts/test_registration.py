import requests
import time

url = "http://api:8000/api/v1/auth/register"  # Reaching the API from inside the backend container internally if needed, or localhost:8000
try:
    response = requests.post("http://localhost:8000/api/v1/auth/register", json={
        "email": "auto_test_background@rpm.com",
        "password": "autoPassword123",
        "full_name": "Auto Test Background",
        "role": "patient"
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(e)
