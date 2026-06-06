import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "finsights"
    jwt_secret_key: str = "supersecretkey_change_me_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440 # 24 hours
    
    # Mock AA settings
    mock_aa_base_url: str = "https://mock-aa-api.local"

    # Gemini Settings
    gemini_api_key: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
