from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    
    device_id = Column(String, primary_key=True, index=True)
    device_type = Column(String, index=True) # e.g., traffic_light, sensor, camera
    location_zone = Column(String, index=True)
    status = Column(String, default="active") # active, offline, maintenance
    credentials = Column(String) # Hashed token or similar
    metadata_json = Column(JSON, default={})
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    
# Pydantic Schemas for API
class DeviceRegister(BaseModel):
    device_id: str
    device_type: str
    location_zone: str
    credentials: str
    metadata_json: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DeviceStatusUpdate(BaseModel):
    status: str
    metadata_update: Optional[Dict[str, Any]] = None

class DeviceResponse(BaseModel):
    device_id: str
    device_type: str
    location_zone: str
    status: str
    metadata_json: Dict[str, Any]
    registered_at: datetime.datetime
    last_seen: datetime.datetime

    class Config:
        from_attributes = True
