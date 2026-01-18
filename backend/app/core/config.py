from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "proactive-onboarding-engine"
    openai_model_name: str = "gpt-4"
    youtube_api_key: str = "YOUR_YOUTUBE_API_KEY"
    open_api_key: str = "YOUR_OPENAI_API_KEY"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
