from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "proactive-onboarding-engine"

    # Database settings
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "onboarding_db"
    database_user: str = "onboarding_user"
    database_password: str = "securepassword"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.database_user}:"
            f"{self.database_password}@{self.database_host}:"
            f"{self.database_port}/{self.database_name}"
        )

    # Security settings
    secret_key: str = "your_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS settings
    cors_origins: list[str] | str = []

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins and isinstance(self.cors_origins, list):
            return self.cors_origins
        origins = list()
        if self.cors_origins and isinstance(self.cors_origins, str):
            for origin in self.cors_origins.split(","):
                if origin.strip():
                    origins.append(origin.strip())
        return origins

    # Logging settings
    log_level: str = "INFO"
    log_format: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s \n Traceback: %(exc_info)s"
    )

    # Envrionment
    environment: str = "development"  # Options: development, staging, production

    # External API keys
    openai_model_name: str = "gpt-4"
    youtube_api_key: str = "YOUR_YOUTUBE_API_KEY"
    openai_api_key: str = "YOUR_OPENAI_API_KEY"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
