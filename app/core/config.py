from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Urban Copilot AI"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ucai"
    
    # IBM Services
    CLOUDANT_URL: str = ""
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = ""
    IBM_AUTH_URL: str = "https://iam.cloud.ibm.com/identity/token"
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_EXPIRE_MINS: int = 60
    
    # Message Queue
    KAFKA_BROKER: str = "localhost:9092"
    KAFKA_TOPICS: dict = {
        "events": "traffic-events",
        "predictions": "predictions",
        "recommendations": "recommendations"
    }
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
