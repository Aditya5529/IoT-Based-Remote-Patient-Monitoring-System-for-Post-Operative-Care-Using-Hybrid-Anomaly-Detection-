from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base

class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True) # Null = Global Default
    vital_type = Column(String, nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    duration_seconds = Column(Integer, default=0) # Sustained duration required for alert
    enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    patient = relationship("User", backref="thresholds")
