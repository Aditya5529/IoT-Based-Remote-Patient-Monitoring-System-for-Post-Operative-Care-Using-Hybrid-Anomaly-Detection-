from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from uuid import UUID

class VitalBase(BaseModel):
    vital_type: str
    value: float
    unit: str
    source: Optional[str] = "manual"
    activity_label: Optional[str] = None
    raw_meta: Optional[dict] = None
    ts: datetime

class VitalCreate(VitalBase):
    patient_id: Optional[UUID] = None # If doctor creates it, else inferred from current user

class VitalRead(VitalBase):
    id: UUID
    patient_id: UUID

    class Config:
        from_attributes = True
