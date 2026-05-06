from app.db.session import SessionLocal
from app.models.user import User
from app.models.doctor import Doctor
from app.models.patient import Patient

db = SessionLocal()
try:
    # Patch Doctor
    doc_user = db.query(User).filter(User.email == "doctor@rpm.com").first()
    if doc_user:
        has_profile = db.query(Doctor).filter(Doctor.user_id == doc_user.id).first()
        if not has_profile:
            db.add(Doctor(user_id=doc_user.id, specialization="General"))
            print("Doctor profile patched!")
            
    # Patch Patient
    pat_user = db.query(User).filter(User.email == "patient@rpm.com").first()
    if pat_user:
        has_profile = db.query(Patient).filter(Patient.user_id == pat_user.id).first()
        if not has_profile:
            db.add(Patient(user_id=pat_user.id, gender="Unknown"))
            print("Patient profile patched!")
            
    db.commit()
except Exception as e:
    print("Error:", e)
finally:
    db.close()
