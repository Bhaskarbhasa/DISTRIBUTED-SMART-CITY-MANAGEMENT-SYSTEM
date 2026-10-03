from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

class EnvironmentTelemetry(BaseModel):
    sensor_id: str
    zone_id: str
    temperature: float
    humidity: float
    aqi: float
    pm25: float
    pm10: float
    co2: float
    no2: float
    wind_speed: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnvironmentAlert(BaseModel):
    alert_id: str
    zone_id: str
    alert_type: str
    severity: str
    value: float
    threshold: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
