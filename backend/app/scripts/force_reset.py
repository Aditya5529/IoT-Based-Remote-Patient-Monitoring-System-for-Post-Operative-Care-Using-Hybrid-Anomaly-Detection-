from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.vital import Vital
from app.core.security import get_password_hash
from app.db.base import Base
import logging
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_reset_users():
    logger.info("--- STARTING FORCE RESET OF USERS & MEDICAL DATA ---")
    
    # 1. Ensure Tables Exist (Drops and creates if you want a cleaner slate, 
    # but for now we just rely on create_all to add missing tables. 
    # Note: Alembic is better, but this is dev mode.)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    users_to_seed = [
        {"email": "admin@rpm.com", "password": "admin123", "role": UserRole.ADMIN, "name": "Admin User"},
        {"email": "doctor@rpm.com", "password": "doc123", "role": UserRole.DOCTOR, "name": "Dr. Smith"},
        {"email": "patient@rpm.com", "password": "pat123", "role": UserRole.PATIENT, "name": "John Patient"},
    ]

    seeded_users = {}

    for u_data in users_to_seed:
        user = db.query(User).filter(User.email == u_data["email"]).first()
        if not user:
            logger.info(f"Creating new user: {u_data['email']}")
            user = User(
                email=u_data["email"],
                hashed_password=get_password_hash(u_data["password"]),
                full_name=u_data["name"],
                role=u_data["role"],
                is_active=True
            )
            db.add(user)
            db.commit() # Commit to get ID
            db.refresh(user)
        else:
             logger.info(f"User exists: {u_data['email']}")
        
        seeded_users[u_data["email"]] = user

    # 2. Seed Medical Profiles
    
    # Doctor Profile
    doc_user = seeded_users["doctor@rpm.com"]
    doctor = db.query(Doctor).filter(Doctor.user_id == doc_user.id).first()
    if not doctor:
        doctor = Doctor(user_id=doc_user.id, specialization="Cardiology")
        db.add(doctor)
        logger.info("Seeded Doctor Profile")
    
    # Patient Profile
    pat_user = seeded_users["patient@rpm.com"]
    patient = db.query(Patient).filter(Patient.user_id == pat_user.id).first()
    if not patient:
        patient = Patient(user_id=pat_user.id, dob=datetime(1980, 1, 1).date(), gender="Male", medical_notes="Hypertension history")
        db.add(patient)
        logger.info("Seeded Patient Profile")

    db.commit()
    db.refresh(doctor)
    db.refresh(patient)

    # 3. Assign Patient to Doctor
    if patient not in doctor.patients:
        doctor.patients.append(patient)
        logger.info(f"Assigned {pat_user.full_name} to {doc_user.full_name}")
        db.commit()

    # 4. Seed Vitals (Last 24 hours)
    # Check if vitals already exist to avoid dupes on re-run
    existing_vitals = db.query(Vital).filter(Vital.patient_id == pat_user.id).count()
    if existing_vitals < 10:
        logger.info("Seeding dummy vitals...")
        base_time = datetime.utcnow() - timedelta(hours=24)
        vitals_data = []
        for i in range(50):
            ts = base_time + timedelta(minutes=30*i)
            # HR
            vitals_data.append(Vital(
                patient_id=pat_user.id,
                ts=ts,
                vital_type="heart_rate",
                value=random.normalvariate(80, 5), # Normal HR
                unit="bpm",
                source="simulator"
            ))
            # SpO2
            vitals_data.append(Vital(
                patient_id=pat_user.id,
                ts=ts,
                vital_type="spo2",
                value=random.uniform(95, 100),
                unit="%",
                source="simulator"
            ))
        
        db.add_all(vitals_data)
        db.commit()
        logger.info("Seeded 100 vital records.")

    db.close()

if __name__ == "__main__":
    force_reset_users()
