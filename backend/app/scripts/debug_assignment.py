from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor

def debug_users():
    db = SessionLocal()
    try:
        print("🔍 Debugging User Data for Meenakshi...")
        
        # 1. Check Meenakshi
        email = "meenakshig75@gmail.com"
        # Try both case seinsitive and insensitive match just in case, but email is string
        meenakshi = db.query(User).filter(User.email == email).first()
        
        if meenakshi:
            print(f"✅ User Found: {meenakshi.email} (ID: {meenakshi.id})")
            if not meenakshi.patient_profile:
                print(f"   ❌ NO PATIENT PROFILE! Fix triggered...")
                # Fix: Check existing first to avoid duplicate key error if committed but object not refreshed?
                try:
                    db.add(Patient(user_id=meenakshi.id, gender="Unknown", dob=None))
                    db.commit()
                    print("   ✅ Fixed Profile created.")
                except Exception as ex:
                    print(f"   ⚠️ Fix error/rollback: {ex}")
                    db.rollback()
            else:
                 print("   ✅ Profile Already Exists.")
        else:
            print(f"❌ User {email} NOT FOUND in DB.")

        # 2. Check Doctor
        doc_email = "doctor@rpm.com"
        doctor = db.query(User).filter(User.email == doc_email).first()
        if doctor:
             if not doctor.doctor_profile:
                 print(f"   ❌ NO DOCTOR PROFILE for {doc_email}! Fix triggered...")
                 db.add(Doctor(user_id=doctor.id, specialization="General"))
                 db.commit()
                 print("   ✅ Doctor Profile Fixed.")
             else:
                 print("   ✅ Doctor Profile Exists.")
                 
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_users()
