from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/broodjes"
    admin_password: str = "admin2026"

    class Config:
        env_file = ".env"


settings = Settings()
