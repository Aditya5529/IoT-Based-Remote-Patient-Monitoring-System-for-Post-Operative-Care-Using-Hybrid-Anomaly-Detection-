from app.db.session import engine
from app.db.base import Base

print("Creating new IoT tables if they don't exist...")
Base.metadata.create_all(bind=engine)
print("Tables verified/created successfully.")
