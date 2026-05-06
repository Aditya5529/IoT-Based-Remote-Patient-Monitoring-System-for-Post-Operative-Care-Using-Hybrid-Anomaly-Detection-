import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.core import security
from app.db.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # 1. Create Tables
    Base.metadata.create_all(bind=engine)
    
    # 2. Check and Seed Admin
    admin = db.query(User).filter(User.email == "admin@rpm.com").first()
    if not admin:
        logger.info("Seeding Admin User")
        admin_in = User(
            email="admin@rpm.com",
            hashed_password=security.get_password_hash("admin123"),
            role=UserRole.ADMIN,
            full_name="System Admin",
            is_superuser=True
        )
        db.add(admin_in)
    
    # 3. Seed Doctor
    doctor = db.query(User).filter(User.email == "doctor@rpm.com").first()
    if not doctor:
        logger.info("Seeding Doctor User")
        doc_in = User(
            email="doctor@rpm.com",
            hashed_password=security.get_password_hash("doc123"),
            role=UserRole.DOCTOR,
            full_name="Dr. Strange",
        )
        db.add(doc_in)
        db.flush()
        doc_profile = Doctor(user_id=doc_in.id, specialization="General")
        db.add(doc_profile)

    # 4. Seed Patient
    patient = db.query(User).filter(User.email == "patient@rpm.com").first()
    if not patient:
        logger.info("Seeding Patient User")
        pat_in = User(
            email="patient@rpm.com",
            hashed_password=security.get_password_hash("pat123"),
            role=UserRole.PATIENT,
            full_name="Tony Stark",
        )
        db.add(pat_in)
        db.flush()
        pat_profile = Patient(user_id=pat_in.id, gender="Unknown", dob=None)
        db.add(pat_profile)
    
    db.commit()

if __name__ == "__main__":
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    logger.info("Initial data created")
