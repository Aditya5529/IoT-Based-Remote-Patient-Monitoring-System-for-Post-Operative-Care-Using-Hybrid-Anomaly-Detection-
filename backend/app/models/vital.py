from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base

class Vital(Base):
    __tablename__ = "vitals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    ts = Column(DateTime(timezone=True), nullable=False, index=True)
    vital_type = Column(String, nullable=False, index=True) # HR, SPO2, TEMP, etc.
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    source = Column(String, default="manual") # sensor, manual, dataset
    activity_label = Column(String, nullable=True) # walking, running, sitting (from HAR)
    raw_meta = Column(JSON, nullable=True)

    patient = relationship("User", backref="vitals")
