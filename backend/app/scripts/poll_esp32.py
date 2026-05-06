import time
import socket
import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ESP32_Poller")

import os

ESP32_IP = os.environ.get("ESP32_IP", "172.20.10.3")
ESP32_PORT = int(os.environ.get("ESP32_PORT", 80))
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api/v1/iot/vitals")
DEVICE_SECRET = os.environ.get("IOT_DEVICE_SECRET", "secret123")
PATIENT_EMAIL = os.environ.get("TEST_PATIENT_EMAIL", "patient@rpm.com")
PATIENT_PASSWORD = os.environ.get("TEST_PATIENT_PASSWORD", "pat123")

def get_patient_id():
    try:
        r = requests.post("http://localhost:8000/api/v1/auth/login", data={"username": PATIENT_EMAIL, "password": PATIENT_PASSWORD})
        token = r.json().get("access_token")
        if not token:
            return None
        r2 = requests.get("http://localhost:8000/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        return r2.json().get("id")
    except Exception as e:
        logger.error(f"Failed to get patient ID: {e}")
        return None

PATIENT_ID = get_patient_id()
if not PATIENT_ID:
    logger.error("Could not fetch PATIENT_ID. Exiting.")
    exit(1)

def poll_and_forward():
    logger.info("Starting Subprocess (curl) ESP32 Poller...")
    while True:
        try:
            import subprocess
            json_str = ""
            for _ in range(10):
                result = subprocess.run(["curl.exe", f"http://{ESP32_IP}:{ESP32_PORT}"], capture_output=True, text=True, timeout=5)
                out = result.stdout.strip()
                if out.startswith('{') and out.endswith('}'):
                    json_str = out
                    break
                time.sleep(0.5)
                
            if not json_str:
                logger.error(f"Failed to fetch valid data via curl after retries.")
                time.sleep(5)
                continue
            # Extract JSON if there are HTTP headers included by accident, though -s should only print body
            if json_str.startswith('{') and json_str.endswith('}'):
                data = json.loads(json_str)
                
                payload = {
                    "device_id": "ESP32_001",
                    "patient_id": PATIENT_ID,
                    "heart_rate": float(data.get("bpm", 0)),
                    "avg_bpm": float(data.get("avg_bpm", 0)),
                    "spo2": 98.0,
                    "ir_value": float(data.get("ir", 0)),
                    "temperature": float(data.get("temp", 0)),
                    "accel_x": float(data.get("ax", 0)),
                    "gyro_x": float(data.get("gx", 0)),
                    "source": "esp32"
                }
                
                headers = {
                    "X-Device-Secret": DEVICE_SECRET,
                    "Content-Type": "application/json"
                }
                post_res = requests.post(BACKEND_API_URL, json=payload, headers=headers)
                
                if post_res.status_code == 200:
                    logger.info(f"Forwarded data: HR={payload['heart_rate']} Temp={payload['temperature']}")
                else:
                    logger.error(f"Failed to forward data: {post_res.status_code} - {post_res.text}")
            else:
                logger.error(f"Invalid JSON received: {json_str}")
                
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from ESP32: {json_str}")
        except Exception as e:
            logger.error(f"ESP32 Polling Error: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    poll_and_forward()
