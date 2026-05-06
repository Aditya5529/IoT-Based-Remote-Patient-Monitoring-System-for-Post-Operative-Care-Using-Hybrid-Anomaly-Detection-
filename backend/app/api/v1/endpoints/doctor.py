from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/my-patients", response_model=List[UserResponse])
def get_my_patients(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get list of patients assigned to the current doctor.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Not a doctor")
        
    # Explicitly fetch profile to avoid list attribute error
    doctor_profile = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor_profile:
        return []
        
    # Access patients via relationship
    return [patient.user for patient in doctor_profile.patients]
