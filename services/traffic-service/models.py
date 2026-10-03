from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class TrafficTelemetry(Base):
    __tablename__ = 'traffic_telemetry'
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, index=True)
    zone_id = Column(String, index=True)
    vehicle_count = Column(Integer)
    avg_speed = Column(Float)
    congestion_level = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class TrafficDecision(Base):
    __tablename__ = 'traffic_decision'
    decision_id = Column(String, primary_key=True, index=True)
    zone_id = Column(String, index=True)
    signal_state = Column(String)
    green_duration = Column(Integer)
    yellow_duration = Column(Integer)
    red_duration = Column(Integer)
    leader_id = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class TrafficSignalState(Base):
    __tablename__ = 'traffic_signal_state'
    zone_id = Column(String, primary_key=True, index=True)
    current_signal = Column(String)
    duration_remaining = Column(Integer)
    last_decision_id = Column(String)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
