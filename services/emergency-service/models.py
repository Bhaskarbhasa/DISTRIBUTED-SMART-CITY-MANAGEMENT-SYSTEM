from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class EmergencyAlert(Base):
    __tablename__ = 'emergency_alert'
    alert_id = Column(String, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    alert_type = Column(String)
    severity = Column(String)
    location_lat = Column(Float)
    location_lon = Column(Float)
    zone_id = Column(String, index=True)
    status = Column(String, default='ACTIVE')
    reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    resolution_notes = Column(String, nullable=True)

class AlertAuditLog(Base):
    __tablename__ = 'alert_audit_log'
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, index=True)
    action = Column(String)
    actor = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    details = Column(String, nullable=True)
