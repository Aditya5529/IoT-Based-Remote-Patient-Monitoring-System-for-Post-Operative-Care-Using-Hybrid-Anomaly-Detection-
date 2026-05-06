import requests
import sys
import time

# Internal URL inside container (localhost works if port mapped, otherwise 0.0.0.0)
# But since we are inside the container, localhost:8000 should work if uvicorn listens on 0.0.0.0
BASE_URL = "http://localhost:8000/api/v1"

def test_internal():
    # Wait for server to be likely up
    # time.sleep(2) 
    
    # 1. Login
    url = f"{BASE_URL}/auth/login"
    payload = {"username": "patient@rpm.com", "password": "pat123"}
    print(f"Internal Login Test to {url}")
    try:
        r = requests.post(url, data=payload)
        print(f"Login Status: {r.status_code}")
        print(f"Login Body: {r.text[:200]}")
    except Exception as e:
        print(f"Login Exception: {e}")

    # 2. Register
    url_reg = f"{BASE_URL}/auth/register"
    reg_payload = {"email": "internal_test@rpm.com", "password": "test", "full_name": "Int Test", "role": "patient"}
    print(f"Internal Register Test to {url_reg}")
    try:
        r = requests.post(url_reg, json=reg_payload)
        print(f"Register Status: {r.status_code}")
        print(f"Register Body: {r.text[:200]}")
    except Exception as e:
        print(f"Register Exception: {e}")

if __name__ == "__main__":
    test_internal()
