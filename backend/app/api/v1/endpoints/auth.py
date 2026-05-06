from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import Token, UserResponse, UserCreate
from pydantic import BaseModel, EmailStr
import random
import string

# In-memory dictionary for password resets: { "email@example.com": "123456" }
reset_tokens = {}

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    token: str
    new_password: str

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/test-token", response_model=UserResponse)
def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user

@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Register a new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    obj_in = jsonable_encoder(user_in)
    hashed_password = security.get_password_hash(user_in.password)
    if 'password' in obj_in:
        del obj_in['password']
    
    db_obj = User(**obj_in, hashed_password=hashed_password)
    db.add(db_obj)
    
    # Flush to get ID, but don't commit yet (Transaction ongoing)
    db.flush() 
    
    # Auto-create profile based on role
    from app.models.patient import Patient
    from app.models.doctor import Doctor
    
    try:
        if db_obj.role == "patient":
            profile = Patient(user_id=db_obj.id, gender="Unknown", dob=None)
            db.add(profile)
        elif db_obj.role == "doctor":
            profile = Doctor(user_id=db_obj.id, specialization="General")
            db.add(profile)
        
        db.commit() # Single commit for both
        db.refresh(db_obj)
        
        # Auto-update db_users.txt
        from app.scripts.view_all_users import view_all_users
        import os
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../db_users.txt"))
        background_tasks.add_task(view_all_users, output_path)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
        
    return db_obj

@router.post("/request-password-reset")
def request_password_reset(
    req: PasswordResetRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Request a password reset code. Returns the code for demo purposes.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email address not found")
        
    # Generate 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    
    # Store in memory
    reset_tokens[req.email] = code
    
    return {"detail": "Reset code generated", "demo_code": code}

@router.post("/reset-password")
def reset_password(
    req: PasswordResetConfirm,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Any:
    """
    Verify reset token and update database password.
    """
    stored_code = reset_tokens.get(req.email)
    if not stored_code or stored_code != req.token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
        
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email address not found")
        
    # Hash new password
    user.hashed_password = security.get_password_hash(req.new_password)
    db.commit()
    
    # Clear token
    del reset_tokens[req.email]
    
    # Auto-update db_users.txt
    from app.scripts.view_all_users import view_all_users
    import os
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../db_users.txt"))
    background_tasks.add_task(view_all_users, output_path)
    
    return {"detail": "Password successfully reset"}
