from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/smartcity"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_devices: str = "device.status"
    
    class Config:
        env_file = ".env"

settings = Settings()
