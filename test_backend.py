import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": "patient@rpm.com",
        "password": "pat123"
    }
    # Requests automatically sends as application/x-www-form-urlencoded compatible form data
    # if using 'data='. If using 'files=', it uses multipart. 
    # Login.tsx uses FormData, which axios sends as multipart/form-data with bounds.
    # To mimic 'data', we use data.
    
    print(f"Testing Login [POST] {url}...")
    try:
        resp = requests.post(url, data=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Login SUCCESS!")
            print(resp.json())
        else:
            print(f"Login FAILED: {resp.text}")
    except Exception as e:
        print(f"Login Request Failed: {e}")

def test_register():
    url = f"{BASE_URL}/auth/register"
    # UserCreate schema expects JSON body
    payload = {
        "email": "newuser@rpm.com",
        "password": "newpassword123",
        "full_name": "Test User",
        "role": "patient"
    }
    print(f"\nTesting Register [POST] {url}...")
    try:
        resp = requests.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Register SUCCESS!")
            print(resp.json())
        elif resp.status_code == 400 and "already exists" in resp.text:
             print("Register verified (User already exists).")
        else:
            print(f"Register FAILED: {resp.text}")
    except Exception as e:
        print(f"Register Request Failed: {e}")

if __name__ == "__main__":
    test_login()
    test_register()
