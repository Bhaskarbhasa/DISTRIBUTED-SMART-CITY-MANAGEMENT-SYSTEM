from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BROKERS: str = "localhost:9092"
    CONSUMER_GROUP: str = "notification-service"
    PORT: int = 8005
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
