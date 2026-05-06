from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api import deps
from app.models.user import User, UserRole
from app.models.doctor import Doctor, doctor_patient_map
from app.models.patient import Patient
from app.schemas.user import UserResponse as UserSchema
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

class AssignDoctorRequest(BaseModel):
    doctor_id: UUID
    patient_id: UUID

@router.get("/system-health")
def get_system_health(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Admin Only: Check DB, ML status, counts.
    """
    # 1. DB Check
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    # 2. Counts
    total_patients = db.query(User).filter(User.role == UserRole.PATIENT).count()
    total_doctors = db.query(User).filter(User.role == UserRole.DOCTOR).count()
    total_alerts = 0 # Query Alert model count if imported
    
    # 3. ML Status (Check if model artifact exists)
    import os
    ml_path = os.path.join("app", "ml", "artifacts", "model.joblib")
    ml_status = "loaded" if os.path.exists(ml_path) else "not_found"

    return {
        "db_status": db_status,
        "ml_engine_status": ml_status,
        "counts": {
            "patients": total_patients,
            "doctors": total_doctors
        }
    }

@router.get("/doctors", response_model=List[UserSchema])
def get_all_doctors(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    doctors = db.query(User).filter(User.role == UserRole.DOCTOR).all()
    return doctors

@router.get("/patients", response_model=List[UserSchema])
def get_all_patients(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    patients = db.query(User).filter(User.role == UserRole.PATIENT).all()
    return patients

@router.post("/assign-doctor")
def assign_doctor(
    request: AssignDoctorRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # Verify Doctor Exists
    doctor_user = db.query(User).filter(User.id == request.doctor_id).first()
    if not doctor_user:
         raise HTTPException(status_code=404, detail="Doctor User not found")
    if doctor_user.role != UserRole.DOCTOR:
         raise HTTPException(status_code=400, detail="Selected user is not a Doctor")
    
    # Explicitly fetch profile
    doctor_profile = db.query(Doctor).filter(Doctor.user_id == doctor_user.id).first()
    if not doctor_profile:
         raise HTTPException(status_code=404, detail=f"Doctor {doctor_user.email} has no DoctorProfile.")

    # Verify Patient Exists
    patient_user = db.query(User).filter(User.id == request.patient_id).first()
    if not patient_user:
         raise HTTPException(status_code=404, detail="Patient User not found")
    if patient_user.role != UserRole.PATIENT:
         raise HTTPException(status_code=400, detail="Selected user is not a Patient")
    
    # Explicitly fetch profile
    patient_profile = db.query(Patient).filter(Patient.user_id == patient_user.id).first()
    if not patient_profile:
         raise HTTPException(status_code=404, detail=f"Patient {patient_user.email} has no PatientProfile.")
        
    # Create Association Directly (Nuclear Option)
    # Check if assignment exists
    stmt_check = doctor_patient_map.select().where(
        doctor_patient_map.c.doctor_id == doctor_profile.id,
        doctor_patient_map.c.patient_id == patient_profile.id
    )
    existing = db.execute(stmt_check).first()
    if existing:
        return {"detail": "Already assigned"}
        
    stmt_insert = doctor_patient_map.insert().values(
        doctor_id=doctor_profile.id,
        patient_id=patient_profile.id
    )
    db.execute(stmt_insert)
    db.commit()
    
    # Auto-update db_users.txt
    from app.scripts.view_all_users import view_all_users
    import os
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../db_users.txt"))
    background_tasks.add_task(view_all_users, output_path)
    
    return {"detail": "Assignment successful"}
