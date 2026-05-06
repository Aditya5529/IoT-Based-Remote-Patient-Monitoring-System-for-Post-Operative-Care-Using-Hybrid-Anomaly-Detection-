from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from app.api import deps
from app.models.user import User, UserRole
from app.models.alert import Alert, AlertStatus
from app.schemas.alert import AlertRead

router = APIRouter()

@router.get("/", response_model=List[AlertRead])
def read_alerts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve alerts.
    - Doctors see alerts for their patients.
    - Patients see their own alerts.
    """
    query = db.query(Alert)
    
    if current_user.role == UserRole.PATIENT:
        query = query.filter(Alert.patient_id == current_user.id)
    elif current_user.role == UserRole.DOCTOR:
        # Show alerts assigned to this doctor OR where doctor is unassigned but patient is mine
        # For Review-1 with population fix: check doctor_id
        query = query.filter(Alert.doctor_id == current_user.id)
        
    query = query.order_by(Alert.ts.desc())
    return query.offset(skip).limit(limit).all()

@router.put("/{alert_id}/acknowledge", response_model=AlertRead)
def acknowledge_alert(
    alert_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    # Permission check
    if current_user.role == UserRole.DOCTOR:
        # Allow
        pass
    elif current_user.role == UserRole.PATIENT:
        if alert.patient_id != current_user.id:
             raise HTTPException(status_code=400, detail="Not your alert")
    
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert

