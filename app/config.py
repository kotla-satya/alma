from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://alma:alma@localhost:5432/alma"
    secret_key: str = "changeme"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    resend_api_key: str = ""
    attorney_email: str = "attorney@example.com"
    from_email: str = "noreply@alma.com"

    admin_email: str = "admin@alma.com"
    admin_password: str = "changeme"
    admin_name: str = "Admin Attorney"


settings = Settings()
