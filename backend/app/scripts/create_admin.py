from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_admin_user():
    db: Session = SessionLocal()
    try:
        email = "admin@rpm.com"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("Admin user already exists.")
            return

        admin_user = User(
            email=email,
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        print(f"✅ Created Admin User: {email} / admin123")
    except Exception as e:
        print(f"❌ Failed to create admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
