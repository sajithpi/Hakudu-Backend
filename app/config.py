from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = False
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 60
    cors_origins: List[str] = ["http://localhost:3000"]
    trusted_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    class Config:
        env_file = ".env"


settings = Settings()
