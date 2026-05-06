from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, UserRole
from app.models.vital import Vital
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.vital import VitalCreate, VitalRead
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/history", response_model=List[VitalRead])
def read_vitals_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[str] = None, # If doctor viewing specific patient
    vital_type: Optional[str] = None
) -> Any:
    """
    Retrieve vitals history.
    Patients see their own.
    Doctors can see assigned patients.
    """
    if current_user.role == UserRole.PATIENT:
        query = db.query(Vital).filter(Vital.patient_id == current_user.id)
    elif current_user.role == UserRole.DOCTOR:
        if not patient_id:
             return [] 
        
        # STRICT: Verify assignment via explicit query
        doctor_profile = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor_profile:
             raise HTTPException(status_code=403, detail="No doctor profile")
             
        # Check if patient_id is in my assigned list
        assigned_ids = [str(p.user_id) for p in doctor_profile.patients]
        if str(patient_id) not in assigned_ids:
             raise HTTPException(status_code=403, detail="You are not assigned to this patient.")

        query = db.query(Vital).filter(Vital.patient_id == patient_id)
    else:
        # Admin
        if patient_id:
             query = db.query(Vital).filter(Vital.patient_id == patient_id)
        else:
             query = db.query(Vital)

    if vital_type:
        query = query.filter(Vital.vital_type == vital_type)

    return query.order_by(Vital.ts.desc()).offset(skip).limit(limit).all()

from app.services.alert_rules import check_vital_alert

from app.services.alert_rules import check_vital_alert

@router.post("/", response_model=VitalRead)
def create_vital(
    *,
    db: Session = Depends(deps.get_db),
    vital_in: VitalCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new vital record.
    """
    # If patient, force patient_id
    if current_user.role == UserRole.PATIENT:
        vital_in.patient_id = current_user.id
    
    vital = Vital(
        patient_id=vital_in.patient_id,
        ts=vital_in.ts,
        vital_type=vital_in.vital_type,
        value=vital_in.value,
        unit=vital_in.unit,
        source=vital_in.source,
        activity_label=vital_in.activity_label,
        raw_meta=vital_in.raw_meta
    )
    db.add(vital)
    db.commit()
    db.refresh(vital)
    
    # Trigger Alert Check
    check_vital_alert(db, vital)
    db.commit()
    
    # Trigger Alert Check
    check_vital_alert(db, vital)
    db.commit()
    
    return vital
