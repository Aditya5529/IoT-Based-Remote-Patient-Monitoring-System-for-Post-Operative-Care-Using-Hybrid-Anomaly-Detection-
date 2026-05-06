from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class AlertBase(BaseModel):
    vital_type: str
    measured_value: float
    severity: AlertSeverity
    reason: str
    status: AlertStatus

class AlertRead(AlertBase):
    id: UUID
    patient_id: UUID
    doctor_id: Optional[UUID]
    ts: datetime
    acknowledged_by: Optional[UUID]
    acknowledged_at: Optional[datetime]

    class Config:
        from_attributes = True
