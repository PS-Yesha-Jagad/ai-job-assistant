from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ADZUNA_APP_ID: str
    ADZUNA_APP_KEY: str
    OLLAMA_MODEL: str = "mistral"
    OLLAMA_HOST: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

settings = Settings()