# IoT-Based Remote Patient Monitoring System for Post-Operative Care Using Hybrid Anomaly Detection

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19.2.0-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-Scikit_Learn-F7931E?logo=scikit-learn&logoColor=white)
![IoT](https://img.shields.io/badge/IoT-ESP32-E53935?logo=espressif&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)

---

## Project Overview

The **IoT-Based Remote Patient Monitoring System** is an advanced, full-stack healthcare application designed for post-operative care. It bridges the gap between physical health monitoring and digital healthcare delivery by integrating real-time IoT sensor data with a robust Machine Learning engine to predict physiological anomalies before they become critical.

The system features dynamic role-based dashboards (Admin, Doctor, Patient), secure patient-doctor communication, and a hybrid architecture capable of handling simulated mock data, direct hardware ingestion, and cloud-based fallback logic via ThingSpeak.

---

## Features

- **Real-Time IoT Vitals Ingestion:** Stream Heart Rate, SpO2, Temperature, and accelerometer/gyroscope data.
- **Machine Learning Anomaly Detection:** Real-time ML pipeline using **Isolation Forest** (with planned DAGMM integration) to identify high-risk physiological patterns.
- **Dynamic Dashboards:** Dedicated interactive portals for Patients, Doctors, and System Admins.
- **Instant Alert Generation:** Automated alerting mechanism triggered by threshold breaches and ML anomalies.
- **Patient-Doctor Messaging:** Built-in secure messaging and consultation flow.
- **Multi-tenant Architecture:** Secure JWT-based authentication supporting role-based access control (RBAC).
- **Dockerized Environment:** Fully containerized setup for rapid deployment and scaling.
- **ThingSpeak Fallback:** Redundant cloud integration to prevent data loss during direct server downtime.

---

## System Architecture

The architecture follows a modern **micro-services-inspired monolith** pattern:

1. **Hardware Layer (ESP32):** Captures analog and I2C signals from MAX30102, LM35, and MPU6050.
2. **Network/Ingestion Layer:** Devices transmit JSON payloads via HTTP POST to the FastAPI endpoints or via lightweight local proxy fetchers.
3. **Core Backend (FastAPI):** Validates payloads securely, stores raw data in PostgreSQL, and routes data to the ML Inference Engine.
4. **Machine Learning Engine:** Analyzes normalized feature vectors and calculates anomaly severity scores.
5. **Presentation Layer (React):** Real-time interactive UI consuming backend REST APIs.

### Workflow
`ESP32 / Mock Simulator` ➔ `FastAPI Backend` ➔ `PostgreSQL Database` ➔ `ML Risk Engine` ➔ `Alert Service` ➔ `React Dashboards`

---

## Technology Stack

### Hardware Components
| Component | Function |
| :--- | :--- |
| **ESP32** | Wi-Fi enabled microcontroller serving as the central hub. |
| **MAX30102/MAX30105** | Pulse Oximeter and Heart Rate sensor. |
| **LM35** | Precision analog temperature sensor. |
| **MPU6050** | 6-axis Accelerometer and Gyroscope for fall/movement detection. |

### Software Components
| Technology | Description |
| :--- | :--- |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic |
| **Database** | PostgreSQL 15, Redis 7 (Caching), SQLAlchemy, Alembic |
| **Machine Learning** | Scikit-Learn, Pandas, NumPy, Joblib, PyTorch |
| **Frontend** | React 19, Vite, TypeScript, TailwindCSS, Framer Motion, Recharts |
| **Infrastructure** | Docker, Docker Compose |

---

## Machine Learning Models

The anomaly detection engine relies on an **Isolation Forest** model to detect subtle deviations in a patient's vitals that standard fixed thresholds might miss. 
- **Feature Engineering:** Normalizes Heart Rate, SpO2, Temperature, Glucose, and Blood Pressure.
- **Inference:** Outputs a binary classification (`1` = normal, `-1` = anomaly) and a decision function score to indicate severity.
- **Hybrid Approach:** The project title references *Hybrid Anomaly Detection (DAGMM)*. Currently, Isolation Forest serves as the robust baseline implementation, with architecture mapped for future Deep Autoencoding Gaussian Mixture Model (DAGMM) integration.

---

## Folder Structure

```
├── backend/                  # Python FastAPI Backend
│   ├── app/                  # Application Core
│   │   ├── api/v1/           # API Routers & Endpoints
│   │   ├── core/             # Configuration & Security
│   │   ├── ml/               # Machine Learning Pipeline (Training & Inference)
│   │   ├── models/           # SQLAlchemy Database Models
│   │   └── scripts/          # IoT Pollers, Seeders, and Simulators
│   ├── alembic/              # Database Migrations
│   ├── requirements.txt      # Python Dependencies
│   └── Dockerfile            # Backend Containerization
├── frontend_new/             # React 19 + Vite Frontend
│   ├── src/                  # Components, Pages, Services
│   ├── package.json          # Node Dependencies
│   └── Dockerfile            # Frontend Containerization
├── docs/                     # Documentation
├── screenshots/              # UI Screenshots
├── docker-compose.yml        # Multi-container orchestration
├── .env.example              # Environment Variable Template
└── START_PROJECT.bat         # Quick start utility
```

---

## Installation Instructions

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (if not using Docker)
- Docker Desktop (Recommended)

### A. WITH DOCKER (Recommended)
This is the easiest way to run the entire stack.
1. Clone the repository: `git clone https://github.com/Aditya5529/IoT-Based-Remote-Patient-Monitoring-System-for-Post-Operative-Care-Using-Hybrid-Anomaly-Detection-.git`
2. Create your `.env` file by copying `.env.example` to `.env` and adding your secrets.
3. Build and launch containers:
   ```bash
   docker-compose up --build -d
   ```
4. Access the frontend at `http://localhost:5173` and backend API docs at `http://localhost:8000/docs`.

### B. WITHOUT DOCKER (Local Development)

#### 1. Database Setup
- Ensure PostgreSQL is running.
- Create a database named `rpm_db`.
- Update `.env` with your `DATABASE_URL`.

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
alembic upgrade head      # Run database migrations
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Frontend Setup
```bash
cd frontend_new
npm install
npm run dev
```

---

## Running the System

Once the system is running (either via Docker or Locally), you can interact with it using three primary roles:
- **Admin**: Oversees device assignment and system health.
- **Doctor**: Monitors assigned patients, acknowledges alerts, and communicates.
- **Patient**: Views their own vitals and consults with their doctor.

### Running Mock IoT Simulator
If you do not have physical ESP32 hardware, you can stream simulated realistic vitals (with random anomaly injections):
```bash
cd backend/app/scripts
python mock_iot_stream.py <PATIENT_UUID>
```

### Real ESP32 Integration
If you have the physical IoT device:
1. Ensure the ESP32 and your backend host machine are on the **same Wi-Fi network**.
2. Flash the ESP32 firmware pointing to your local Wi-Fi.
3. The device typically hosts a simple server at its local IP (e.g., `http://172.20.10.3`).
4. Run the local fetcher service to securely pipe data into the backend without dealing with ESP32 TCP-reset limitations:
   ```bash
   cd backend/app/scripts
   python poll_esp32.py
   ```

### ThingSpeak Integration (Fallback)
If the primary backend server goes offline, the ESP32 is configured to push data directly to ThingSpeak. 
- Ensure `THINGSPEAK_CHANNEL_ID` and `THINGSPEAK_READ_API_KEY` are configured in your `.env`.

---

## API Endpoints (Highlights)

| Method | Endpoint | Description | Sample Payload |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/auth/login` | Authenticate and retrieve JWT token | `{"username": "admin@rpm.com", "password": "..."}` |
| **POST** | `/api/v1/auth/register` | Register a new user | `{"email": "...", "password": "...", "role": "patient"}` |
| **POST** | `/api/v1/iot/vitals` | Hardware ingestion (Requires `X-Device-Secret`) | `{"patient_id": "...", "heart_rate": 80, "temperature": 37.1}` |
| **GET** | `/api/v1/iot/latest/{patient_id}` | Retrieve latest IoT reading for dashboards | *None* |
| **GET** | `/api/v1/iot/thingspeak/latest` | Fetch fallback cloud data | *None* |

*For complete interactive documentation, visit `http://localhost:8000/docs` while the backend is running.*

---

## Troubleshooting Guide

- **ESP32 TCP Connection Reset (Error 56):** If standard HTTP clients fail to read from the ESP32, use the provided `poll_esp32.py` script. It wraps `curl` with a retry loop to mitigate the hardware's premature TCP RST packets.
- **Database Connection Refused:** Ensure your PostgreSQL server is active. If using Docker, ensure the `db` service is healthy before the backend starts.
- **CORS Issues:** If the frontend cannot communicate with the backend, verify that `http://localhost:5173` is listed in `ALLOWED_ORIGINS` in your backend `.env` file.
- **Missing Packages:** Ensure you run `pip install -r requirements.txt` from inside the activated virtual environment.
- **Port Conflicts:** Ensure ports `8000` (FastAPI), `5173` (Vite), `5432` (Postgres), and `6379` (Redis) are available on your host machine.

---

---

## Future Enhancements

- **Deep Learning Upgrade:** Full deployment of DAGMM to replace Isolation Forest for multi-dimensional time-series anomaly detection.
- **Mobile Application:** React Native port for patients.
- **Video Consultation:** WebRTC integration for live doctor-patient remote sessions.

---

## Contributors

- **Aditya, Jenil** - Lead Developer & Architect

## License

This project is licensed under the MIT License - see the LICENSE file for details.
