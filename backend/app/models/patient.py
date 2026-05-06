from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
import uuid
from app.db.session import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    dob = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    medical_notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", backref=backref("patient_profile", uselist=False))
