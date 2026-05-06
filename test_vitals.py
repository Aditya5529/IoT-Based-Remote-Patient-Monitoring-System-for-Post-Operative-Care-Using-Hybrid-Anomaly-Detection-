import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_vitals():
    print("1. Logging in as Patient...")
    login_url = f"{BASE_URL}/auth/login"
    payload = {"username": "patient@rpm.com", "password": "pat123"}
    try:
        r = requests.post(login_url, data=payload)
        print(f"Login Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Login Response: {r.text}")
            sys.exit(1)
            
        token = r.json().get("access_token")
        print(f"Token acquired. Length: {len(token)}")
        
        print("2. Fetching Vitals History...")
        v_url = f"{BASE_URL}/vitals/history"
        headers = {"Authorization": f"Bearer {token}"}
        vr = requests.get(v_url, headers=headers)
        print(f"Vitals Status: {vr.status_code}")
        
        if vr.status_code == 200:
            data = vr.json()
            print(f"Vitals Count: {len(data)}")
            if len(data) > 0:
                print(f"First Vital: {data[0]}")
        else:
            print(f"Vitals Response: {vr.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_vitals()
