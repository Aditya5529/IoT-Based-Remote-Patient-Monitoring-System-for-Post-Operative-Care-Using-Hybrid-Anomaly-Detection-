from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
import uuid
from app.db.session import Base

# Association Table for Doctor-Patient Many-to-Many
doctor_patient_map = Table(
    "doctor_patient_map",
    Base.metadata,
    Column("doctor_id", UUID(as_uuid=True), ForeignKey("doctors.id"), primary_key=True),
    Column("patient_id", UUID(as_uuid=True), ForeignKey("patients.id"), primary_key=True)
)

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String, nullable=True)

    # Relationships
    user = relationship("User", backref=backref("doctor_profile", uselist=False))
    patients = relationship("Patient", secondary=doctor_patient_map, backref="doctors")
