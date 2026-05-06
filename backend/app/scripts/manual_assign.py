from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor

def force_assign():
    db = SessionLocal()
    try:
        print("🔗 Force-Assigning Doctor to Patient...")
        
        # 1. Fetch Users
        pat_email = "meenakshig75@gmail.com"
        doc_email = "doctor@rpm.com"
        
        patient_user = db.query(User).filter(User.email == pat_email).first()
        doctor_user = db.query(User).filter(User.email == doc_email).first()
        
        if not patient_user:
            print(f"❌ Patient {pat_email} NOT FOUND.")
            return

        # Ensure Patient Profile
        p_profile = db.query(Patient).filter(Patient.user_id == patient_user.id).first()
        if not p_profile:
             print("   🛠️ Creating Patient Profile...")
             p_profile = Patient(user_id=patient_user.id, gender="Female", dob=None)
             db.add(p_profile)
             db.commit()
        else:
             print(f"   Patient Profile ID: {p_profile.id}")

        # Ensure Doctor Profile
        d_profile = db.query(Doctor).filter(Doctor.user_id == doctor_user.id).first()
        if not d_profile:
             print("   🛠️ Creating Doctor Profile...")
             d_profile = Doctor(user_id=doctor_user.id, specialization="General")
             db.add(d_profile)
             db.commit()
        else:
             print(f"   Doctor Profile ID: {d_profile.id}")

        # Perform Assignment using append
        # Need to query explicit relationship or use append on collection
        # p_profile.doctors is the collection
        
        # Check if d_profile is in p_profile.doctors
        # We need to refresh or re-query to be safe
        db.refresh(p_profile)
        
        assigned_ids = [d.id for d in p_profile.doctors]
        if d_profile.id in assigned_ids:
            print("   ⚠️ Already Assigned!")
        else:
            p_profile.doctors.append(d_profile)
            db.commit()
            print("   ✅ Assignment Created Successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    force_assign()
