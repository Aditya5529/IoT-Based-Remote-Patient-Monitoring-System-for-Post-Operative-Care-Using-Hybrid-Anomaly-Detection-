import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoints():
    print(f"Testing connectivity to {BASE_URL}...")
    
    # 1. Test Root/Health (if exists, checking API root)
    try:
        r = requests.get("http://localhost:8000/")
        print(f"GET /: {r.status_code} (Expect 200)")
    except Exception as e:
        print(f"GET / failed: {e}")

    # 2. Test Register Endpoint Existence (Method Not Allowed 405 is fine vs 404)
    reg_url = f"{BASE_URL}/auth/register"
    try:
        # We send empty body, expecting 422 (Validation Error), NOT 404.
        r = requests.post(reg_url, json={}) 
        print(f"POST {reg_url}: {r.status_code} (Expect 422, received {r.status_code})")
        if r.status_code == 404:
             print("!!! CRITICAL: Register Endpoint NOT FOUND")
    except Exception as e:
        print(f"POST {reg_url} failed: {e}")

    # 3. Test Login Endpoint Existence & Success
    login_url = f"{BASE_URL}/auth/login"
    try:
        # Test Empty (Expect 422)
        r = requests.post(login_url, data={})
        print(f"POST {login_url} (Empty): {r.status_code}")
        
        # Test Demo User (Expect 200)
        payload = {"username": "patient@rpm.com", "password": "pat123"}
        r = requests.post(login_url, data=payload) # Form Data
        print(f"POST {login_url} (Demo Creds): {r.status_code}")
        if r.status_code == 200:
            print(">>> LOGIN SUCCESSFUL! Token received.")
            token = r.json().get("access_token")
            
            # 5. Test Vitals History
            print(f"Testing /vitals/history with token...")
            headers = {"Authorization": f"Bearer {token}"}
            v_url = f"{BASE_URL}/vitals/history"
            try:
                vr = requests.get(v_url, headers=headers)
                print(f"GET {v_url}: {vr.status_code}")
                if vr.status_code == 200:
                    data = vr.json()
                    print(f"Records found: {len(data)}")
                    if len(data) > 0:
                        print(f"Sample: {data[0]}")
                else:
                    print(f"Error: {vr.text}")
            except Exception as e:
                print(f"Vitals check failed: {e}")

        else:
            print(f">>> LOGIN FAILED: {r.text}")

    except Exception as e:
        print(f"POST {login_url} failed: {e}")

    # 4. Test Register Success
    # Use random email to avoid conflict
    import time
    new_email = f"test_pt_{int(time.time())}@rpm.com"
    reg_payload = {
        "email": new_email,
        "password": "password123",
        "full_name": "Test User",
        "role": "patient"
    }
    try:
        r = requests.post(reg_url, json=reg_payload)
        print(f"POST {reg_url} (New User): {r.status_code}")
        if r.status_code == 200:
             print(f">>> REGISTER SUCCESSFUL! User: {new_email}")
        else:
             print(f">>> REGISTER FAILED: {r.text}")
    except Exception as e:
        print(f"POST {reg_url} failed: {e}")

if __name__ == "__main__":
    test_endpoints()
