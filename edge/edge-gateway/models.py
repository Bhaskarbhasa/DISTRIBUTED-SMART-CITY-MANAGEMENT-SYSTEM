from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class BaseEvent(BaseModel):
    sensor_id: str
    zone_id: str
    timestamp: str
    processing_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class TrafficEvent(BaseEvent):
    vehicle_count: int
    average_speed: float
    lane_count: int
    lane_occupancy: List[float]
    
    congestion_level: Optional[str] = None
    density: Optional[float] = None
    anomaly_score: Optional[float] = None

class EnvironmentEvent(BaseEvent):
    temperature: float
    humidity: float
    aqi: float
    pm25: float
    pm10: float
    co2: float
    no2: float
    wind_speed: float
    wind_direction: float
    
    air_quality_category: Optional[str] = None
    temperature_alert: Optional[bool] = None

class EmergencyEvent(BaseEvent):
    emergency_type: str
    severity: str
    location: dict
    
    priority: Optional[int] = None

class CameraEvent(BaseEvent):
    camera_id: str
    vehicle_count: int
    pedestrian_count: int
    incident_detected: bool
    incident_type: Optional[str] = None
    confidence: float
