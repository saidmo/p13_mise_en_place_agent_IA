from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration centralisée, alimentée par les variables d'environnement."""

    app_name: str = "Agent IA Ouvertures Échecs - API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()