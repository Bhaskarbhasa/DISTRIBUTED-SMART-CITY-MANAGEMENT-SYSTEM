import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BROKERS: str = os.getenv('KAFKA_BROKERS', 'localhost:9092')
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/emergency')
    TRAFFIC_SERVICE_URL: str = os.getenv('TRAFFIC_SERVICE_URL', 'http://localhost:8002')
    PORT: int = int(os.getenv('PORT', '8004'))

settings = Settings()
