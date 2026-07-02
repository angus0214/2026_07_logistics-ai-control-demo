from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Logistics AI Control Tower"
    DATABASE_URL: str = "sqlite:///./logistics.db"
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
