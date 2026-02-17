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

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # ChromaDB settings
    chroma_host: str = "localhost"
    chroma_port: int = 8100
    chroma_collection_name: str = "company_policies"

    # RAG settings
    rag_data_dir: str = "rag_data"
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 200

    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def chroma_url(self) -> str:
        return f"http://{self.chroma_host}:{self.chroma_port}"

    # Questionaire settings
    max_clarifying_questions: int = 5

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
