from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./restaurant.db"
    SYNC_DATABASE_URL: str = "sqlite:///./restaurant.db"
    REDIS_URL: str = "redis://localhost:6379/0"


settings = Settings()
