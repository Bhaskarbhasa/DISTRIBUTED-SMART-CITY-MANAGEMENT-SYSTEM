import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MQTT_BROKER: str = os.getenv("MQTT_BROKER") or os.getenv("MQTT_BROKER_HOST") or "mosquitto"
    MQTT_PORT: int = int(os.getenv("MQTT_PORT") or os.getenv("MQTT_BROKER_PORT") or "1883")
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "admin")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "admin")
    
    KAFKA_BROKERS: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    
    DB_PATH: str = os.getenv("DB_PATH", "buffer.db")
    
    class Config:
        env_file = ".env"

settings = Settings()
