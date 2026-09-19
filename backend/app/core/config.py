from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration centralisée, alimentée par les variables d'environnement."""

    app_name: str = "Agent IA Ouvertures Échecs - API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    lichess_api_token: str = ""
    stockfish_path: str = "/usr/games/stockfish"
    ollama_base_url: str = "http://ollama-tunnel:11434"
    ollama_model: str = "qwen3-vl:30b-a3b-instruct-q8_0"
    embedding_model: str = "Qwen/Qwen3-Embedding-0.6B"
    milvus_uri: str = "http://milvus:19530"
    milvus_collection: str = "wikichess"
    embedding_dim: int = 1024
    youtube_api_key: str = ""
    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db: str = "chess_db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()