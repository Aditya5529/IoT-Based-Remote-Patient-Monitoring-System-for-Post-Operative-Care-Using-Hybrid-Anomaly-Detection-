from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import verify_password
import sys

def check_auth():
    print("--- AUTH DIAGNOSTIC ---")
    db = SessionLocal()
    email = 'patient@rpm.com'
    password = 'pat123'
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"FAIL: User {email} NOT FOUND in DB")
        return
    
    print(f"User Found: {user.email}")
    print(f"Role: {user.role}")
    print(f"Stored Hash (first 20 chars): {user.hashed_password[:20]}")
    
    is_valid = verify_password(password, user.hashed_password)
    print(f"Password '{password}' Valid? : {is_valid}")
    
    if is_valid:
        print("SUCCESS: Credentials verification passed locally.")
    else:
        print("FAIL: Password verification failed.")

if __name__ == "__main__":
    check_auth()
