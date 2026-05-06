from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.iot import IoTVitalCreate, IoTVitalResponse
from app.models.iot import IoTVital, IoTDevice
from app.models.patient import Patient
from app.services.iot_processing import process_iot_vitals_background
from app.core.config import settings
from datetime import datetime
import requests

router = APIRouter()

@router.post("/vitals", response_model=IoTVitalResponse)
def create_iot_vital(
    vital_in: IoTVitalCreate,
    background_tasks: BackgroundTasks,
    x_device_secret: str = Header(...),
    db: Session = Depends(deps.get_db),
):
    if x_device_secret != settings.IOT_DEVICE_SECRET:
        raise HTTPException(status_code=401, detail="Invalid device secret")
        
    # Verify Patient Exists
    patient = db.query(Patient).filter(Patient.user_id == vital_in.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Create IoT Vital
    new_vital = IoTVital(
        patient_id=vital_in.patient_id,
        source=vital_in.source,
        heart_rate=vital_in.heart_rate,
        avg_bpm=vital_in.avg_bpm,
        spo2=vital_in.spo2,
        ir_value=vital_in.ir_value,
        temperature=vital_in.temperature,
        accel_x=vital_in.accel_x,
        gyro_x=vital_in.gyro_x
    )
    db.add(new_vital)
    
    # Update Device Last Seen
    device = db.query(IoTDevice).filter(IoTDevice.device_id == vital_in.device_id).first()
    if device:
        device.last_seen = datetime.utcnow()
    else:
        # Auto-register if not exists (for testing ease)
        new_device = IoTDevice(
            device_id=vital_in.device_id,
            patient_id=vital_in.patient_id,
            last_seen=datetime.utcnow()
        )
        db.add(new_device)
        
    db.commit()
    db.refresh(new_vital)
    
    # Trigger Background ML Processing
    background_tasks.add_task(process_iot_vitals_background, str(new_vital.id))
    
    return IoTVitalResponse(
        status="success",
        stored=True,
        anomaly=False, # Processed async
        risk_score=0.0,
        alert_created=False
    )

@router.get("/thingspeak/latest")
def fetch_thingspeak_latest():
    if not settings.THINGSPEAK_CHANNEL_ID or not settings.THINGSPEAK_READ_API_KEY:
        raise HTTPException(status_code=400, detail="ThingSpeak credentials not configured")
        
    url = f"https://api.thingspeak.com/channels/{settings.THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={settings.THINGSPEAK_READ_API_KEY}&results=1"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        if not data.get("feeds"):
            return {"status": "empty", "data": None}
        feed = data["feeds"][0]
        
        return {
            "status": "success",
            "data": {
                "beatsPerMinute": feed.get("field1"),
                "beatAvg": feed.get("field2"),
                "irValue": feed.get("field3"),
                "ax": feed.get("field4"),
                "gx": feed.get("field5"),
                "temperatureC": feed.get("field6"),
                "timestamp": feed.get("created_at")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest/{patient_id}")
def get_latest_iot_vitals(patient_id: str, db: Session = Depends(deps.get_db)):
    vital = db.query(IoTVital).filter(IoTVital.patient_id == patient_id).order_by(IoTVital.timestamp.desc()).first()
    if not vital:
        return {"status": "not_found"}
    
    return {
        "status": "success",
        "data": {
            "heart_rate": vital.heart_rate,
            "avg_bpm": vital.avg_bpm,
            "spo2": vital.spo2,
            "temperature": vital.temperature,
            "accel_x": vital.accel_x,
            "gyro_x": vital.gyro_x,
            "source": vital.source,
            "timestamp": vital.timestamp
        }
    }

@router.get("/devices")
def get_iot_devices(db: Session = Depends(deps.get_db)):
    # Allow admin to view devices
    devices = db.query(IoTDevice).all()
    return [{"device_id": d.device_id, "patient_id": str(d.patient_id), "last_seen": d.last_seen} for d in devices]
