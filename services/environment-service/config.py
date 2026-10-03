from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BROKERS: str = "localhost:9092"
    REDIS_URL: str = "redis://localhost:6379/0"
    ENVIRONMENT_TOPIC: str = "environment.telemetry"
    ALERT_TOPIC: str = "environment.alert"
    CONSUMER_GROUP: str = "environment-service"
    PORT: int = 8003
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
