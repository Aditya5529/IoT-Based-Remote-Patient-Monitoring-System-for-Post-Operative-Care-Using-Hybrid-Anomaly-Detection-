# ESP32 Backend Integration Guide

This document outlines how to securely connect an ESP32 or similar IoT microcontroller to the RPM Vitals Collection backend.

## 1. Network Requirements
For local development, ensure your ESP32 is connected to the same Wi-Fi network as the machine running the backend server.

Your endpoint URL will be your computer's local IP address (e.g., `192.168.1.150`).
- **Endpoint:** `http://<YOUR_LOCAL_IP>:8000/api/v1/iot/vitals`

## 2. Authentication
The backend requires a custom header `X-Device-Secret` to verify the hardware.

- Header Name: `X-Device-Secret`
- Value: `secret123` (configurable in `.env` via `IOT_DEVICE_SECRET`)

## 3. JSON Payload Format
The backend expects a JSON POST request. Required fields are `device_id` and `patient_id`.

```json
{
  "device_id": "esp32-rpm-001",
  "patient_id": "<TARGET_PATIENT_UUID>",
  "heart_rate": 82,
  "avg_bpm": 80,
  "spo2": 97,
  "ir_value": 123456,
  "temperature": 36.7,
  "accel_x": 100,
  "gyro_x": 50,
  "source": "esp32"
}
```

## 4. Example Arduino/C++ Snippet
```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Use your laptop's local IP
const char* serverName = "http://192.168.1.150:8000/api/v1/iot/vitals";

void sendVitalData() {
    if(WiFi.status() == WL_CONNECTED){
        HTTPClient http;
        http.begin(serverName);
        
        // Add Headers
        http.addHeader("Content-Type", "application/json");
        http.addHeader("X-Device-Secret", "secret123");
        
        // Create JSON string
        String jsonPayload = "{\"device_id\":\"esp32-001\", \"patient_id\":\"UUID-HERE\", \"heart_rate\":75, \"spo2\":98, \"temperature\":36.6}";
        
        int httpResponseCode = http.POST(jsonPayload);
        
        if (httpResponseCode > 0) {
            Serial.print("HTTP Response code: ");
            Serial.println(httpResponseCode);
        } else {
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi Disconnected");
    }
}
```

## 5. ThingSpeak Fallback
If you prefer to route data through ThingSpeak instead of direct POST:
1. Ensure your ESP32 pushes to ThingSpeak channels as normal.
2. In the backend `.env`, set `THINGSPEAK_CHANNEL_ID` and `THINGSPEAK_READ_API_KEY`.
3. The backend provides a `GET /api/v1/iot/thingspeak/latest` endpoint to fetch the most recent entry as a fallback mechanism.
