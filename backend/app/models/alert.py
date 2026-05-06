from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from sqlalchemy.sql import func
from app.db.session import Base

class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertStatus(str, enum.Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True) # Assigned doctor at time of alert
    ts = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    vital_type = Column(String, nullable=False)
    measured_value = Column(Float, nullable=False)
    severity = Column(PgEnum(AlertSeverity), default=AlertSeverity.INFO)
    reason = Column(String, nullable=False)
    status = Column(PgEnum(AlertStatus), default=AlertStatus.NEW, index=True)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    # ML Fields
    alert_type = Column(String, default="RULE", nullable=False) # RULE, ML_ANOMALY
    anomaly_score = Column(Float, nullable=True) # 0.0 to 1.0 (or -1 to 1 depending on algo)
    risk_score = Column(Float, nullable=True)
    source = Column(String, default="system")

    patient = relationship("User", foreign_keys=[patient_id], backref="alerts")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_alerts")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])
