from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Firebase
    firebase_project_id: str = ""
    google_application_credentials: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # Admin
    admin_email: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
