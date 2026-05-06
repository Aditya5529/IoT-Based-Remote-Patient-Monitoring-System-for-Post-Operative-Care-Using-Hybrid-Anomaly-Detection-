import os
import sys

# Add backend directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor

def view_all_users(output_file=None):
    import sys
    original_stdout = sys.stdout
    if output_file:
        sys.stdout = open(output_file, 'w', encoding='utf-8')
    try:
        print("Fetching all users from database...")
        print("-" * 60)
        db = SessionLocal()
        try:
            users = db.query(User).all()
            if not users:
                print("No users found in database.")
                return

            print(f"Total Users: {len(users)}\n")
            
            # Display each user details
            for u in users:
                print(f"ID: {u.id}")
                print(f"Email: {u.email}")
                print(f"Role: {u.role}")
                print(f"Hashed Password: {u.hashed_password}")
                print(f"Is Active: {u.is_active}")
                
                # Show associated profiles if present
                if u.role == "patient" and hasattr(u, 'patient_profile'):
                    prof = u.patient_profile[0] if isinstance(u.patient_profile, list) and u.patient_profile else u.patient_profile
                    if prof and not isinstance(prof, list):
                        print(f"↳ Patient Profile ID: {prof.id}")
                    
                if u.role == "doctor" and hasattr(u, 'doctor_profile'):
                    prof = u.doctor_profile[0] if isinstance(u.doctor_profile, list) and u.doctor_profile else u.doctor_profile
                    if prof and not isinstance(prof, list):
                        print(f"↳ Doctor Profile ID: {prof.id}")
                        print(f"  Assigned Patients: {[p.id for p in prof.patients]}")
                
                print("-" * 40)
                
        finally:
            db.close()
    finally:
        if output_file:
            sys.stdout.close()
            sys.stdout = original_stdout

if __name__ == "__main__":
    view_all_users()
