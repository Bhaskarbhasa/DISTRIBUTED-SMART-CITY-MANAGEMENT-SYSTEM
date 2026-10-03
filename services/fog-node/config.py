from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    FOG_NODE_ID: str = "fog-node-1"
    FOG_PEERS: str = "" # Comma-separated
    FOG_PORT: int = 8020
    RAFT_PORT: int = 8021
    ELECTION_TIMEOUT_MIN_MS: int = 150
    ELECTION_TIMEOUT_MAX_MS: int = 300
    HEARTBEAT_INTERVAL_MS: int = 50
    KAFKA_BROKERS: str = "kafka:9092"
    REDIS_URL: str = "redis://redis:6379"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def peer_list(self) -> List[str]:
        if not self.FOG_PEERS:
            return []
        return [p.strip() for p in self.FOG_PEERS.split(",") if p.strip()]

settings = Settings()
