from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api import deps
from app.models.user import User, UserRole
from app.models.message import Message
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.message import MessageCreate, MessageRead

router = APIRouter()

@router.get("/{other_user_id}", response_model=List[MessageRead])
def read_conversation(
    other_user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve messages between current user and other_user_id.
    Sort by timestamp asc for chat bubble UI.
    """
    messages = db.query(Message).filter(
        or_(
            (Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id),
            (Message.sender_id == other_user_id) & (Message.recipient_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).offset(skip).limit(limit).all()
    
    return messages

@router.get("/", response_model=List[MessageRead])
def read_all_messages(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all messages for current user (sent or received).
    Sort by timestamp desc.
    """
    messages = db.query(Message).filter(
        or_(
            Message.sender_id == current_user.id,
            Message.recipient_id == current_user.id
        )
    ).order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
    
    return messages

@router.post("/", response_model=MessageRead)
def create_message(
    *,
    db: Session = Depends(deps.get_db),
    msg_in: MessageCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Send a message. STRICT: Users must be assigned to each other.
    """
    # 1. Identify Sender Profile
    sender_is_patient = current_user.role == UserRole.PATIENT
    sender_is_doctor = current_user.role == UserRole.DOCTOR
    
    if not (sender_is_patient or sender_is_doctor):
         # Admin maybe? For now strict
         raise HTTPException(status_code=403, detail="Only doctors and patients can messages")
         
    recipient = db.query(User).filter(User.id == msg_in.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    # 2. Verify Assignment
    is_assigned = False
    
    # Case A: Patient sending to Doctor
    if sender_is_patient:
        # Check if recipient is a doctor assigned to this patient
        # DB Query is safer than object traversal here
        is_assigned = db.query(User).join(Doctor, User.id == Doctor.user_id)\
            .filter(User.id == msg_in.recipient_id)\
            .filter(Doctor.patients.any(user_id=current_user.id))\
            .count() > 0
            
    # Case B: Doctor sending to Patient
    elif sender_is_doctor:
        # Check if recipient is a patient assigned to this doctor
        is_assigned = db.query(User).join(Patient, User.id == Patient.user_id)\
            .filter(User.id == msg_in.recipient_id)\
            .filter(Patient.doctors.any(user_id=current_user.id))\
             .count() > 0 
        # Wait, Patient.doctors backref might be flaky as seen before.
        # Better: Check if Doctor (current) has Patient (recipient)
        
        is_assigned = db.query(Doctor)\
            .filter(Doctor.user_id == current_user.id)\
            .filter(Doctor.patients.any(user_id=msg_in.recipient_id))\
            .count() > 0
            
    if not is_assigned:
        raise HTTPException(status_code=403, detail="You are not assigned to this user.")

    msg = Message(
        sender_id=current_user.id,
        recipient_id=msg_in.recipient_id,
        content=msg_in.content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

