from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.core.security import get_password_hash

def seed_users():
    db: Session = SessionLocal()
    try:
        print("🌱 Seeding Users & Profiles...")
        
        # 1. Admin (handled by create_admin but safe to repeat)
        if not db.query(User).filter(User.email == "admin@rpm.com").first():
            db.add(User(
                email="admin@rpm.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Admin",
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True
            ))

        # 2. Doctor: doctor@rpm.com
        doc_user = db.query(User).filter(User.email == "doctor@rpm.com").first()
        if not doc_user:
            doc_user = User(
                email="doctor@rpm.com",
                hashed_password=get_password_hash("doc123"),
                full_name="Dr. Smith",
                role=UserRole.DOCTOR,
                is_active=True
            )
            db.add(doc_user)
            db.commit() # Commit to get ID
            db.refresh(doc_user)
            
            # Create Profile
            if not doc_user.doctor_profile:
                db.add(Doctor(user_id=doc_user.id, specialization="Cardiology"))
                
        # 4. Universal Fix: Check ALL users and create missing profiles
        print("🔧 Checking all users for missing profiles...")
        all_users = db.query(User).all()
        for u in all_users:
            if u.role == UserRole.DOCTOR and not u.doctor_profile:
                print(f"   -> Creating Doctor profile for {u.email}")
                db.add(Doctor(user_id=u.id, specialization="General"))
            elif u.role == UserRole.PATIENT and not u.patient_profile:
                print(f"   -> Creating Patient profile for {u.email}")
                db.add(Patient(user_id=u.id, gender="Unknown", dob=None))
                
        db.commit()
        print("✅ Seeding Complete. Profiles Ready.")
        
    except Exception as e:
        print(f"❌ Seeding Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
