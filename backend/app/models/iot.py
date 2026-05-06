from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base

class IoTDevice(Base):
    __tablename__ = "iot_devices"

    device_id = Column(String, primary_key=True, index=True) # like esp32-rpm-001
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    device_name = Column(String, nullable=True)
    status = Column(String, default="active")
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("User", backref="iot_devices")


class IoTVital(Base):
    __tablename__ = "iot_vitals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    source = Column(String, default="esp32")
    heart_rate = Column(Float, nullable=True)
    avg_bpm = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    ir_value = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    accel_x = Column(Float, nullable=True)
    gyro_x = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    patient = relationship("User", backref="iot_vitals_history")
