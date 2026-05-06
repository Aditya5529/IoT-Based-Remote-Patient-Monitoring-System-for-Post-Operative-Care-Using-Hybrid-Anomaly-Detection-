from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users. Only for Admin.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    # current_user: User = Depends(deps.get_current_active_superuser), # Open registration for demo simplicity? No, stick to Admin only or open reg.
    # Let's allow open registration for now or separate open reg endpoint. 
    # For this project, let's allow ANYONE to create a patient, but Admin to create doctors.
) -> Any:
    """
    Create new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    # Simple RBAC for creation:
    # If role is ADMIN, only existing ADMIN can create it? 
    # For simplicity:
    obj_in = jsonable_encoder(user_in)
    hashed_password = security.get_password_hash(user_in.password)
    del obj_in['password']
    
    db_obj = User(**obj_in, hashed_password=hashed_password)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/my-patients", response_model=List[UserResponse])
def read_my_patients(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of patients assigned to the current doctor.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=400, detail="Not a doctor")
    
    # Access the doctor profile
    doctor = current_user.doctor_profile
    if not doctor:
         # Should not happen if seeded correctly, but creating profile if missing?
         # For now return empty
         return []
         
    # Return the list of patients (User objects)
    # The relationship is doctor.patients -> List[Patient]
    # We want List[User] (UserResponse)
    # So we iterate over doctor.patients and get .user
    
    patient_users = [p.user for p in doctor.patients]
    return patient_users

@router.get("/my-doctors", response_model=List[UserResponse])
def read_my_doctors(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of doctors assigned to the current patient.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=400, detail="Not a patient")
    
    from app.models.patient import Patient
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
         return []
         
    doctor_users = [d.user for d in patient.doctors]
    return doctor_users
