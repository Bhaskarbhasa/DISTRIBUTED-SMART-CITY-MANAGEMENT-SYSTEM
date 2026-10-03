from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret_key: str = "super_secret_jwt_key_for_dev_only_change_in_prod"
    jwt_algorithm: str = "HS256"
    
    # Service URLs
    auth_service_url: str = "http://localhost:8001"
    traffic_service_url: str = "http://localhost:8002"
    emergency_service_url: str = "http://localhost:8003"
    environment_service_url: str = "http://localhost:8004"
    analytics_service_url: str = "http://localhost:8005"
    ingestion_service_url: str = "http://localhost:8006"
    fog_node_service_url: str = "http://localhost:8007"
    
    # Proxy Timeout
    proxy_timeout: float = 30.0
    
    class Config:
        env_file = ".env"

settings = Settings()
