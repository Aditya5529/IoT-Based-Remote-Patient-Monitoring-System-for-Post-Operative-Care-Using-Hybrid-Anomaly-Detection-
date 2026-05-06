from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class IoTVitalCreate(BaseModel):
    device_id: str
    patient_id: UUID
    heart_rate: Optional[float] = None
    avg_bpm: Optional[float] = None
    spo2: Optional[float] = None
    ir_value: Optional[float] = None
    temperature: Optional[float] = None
    accel_x: Optional[float] = None
    gyro_x: Optional[float] = None
    source: str = "esp32"

class IoTVitalResponse(BaseModel):
    status: str
    stored: bool
    anomaly: bool
    risk_score: float
    alert_created: bool
