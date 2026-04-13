from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "FinLex AI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-this-to-a-random-secret-key-min-32-chars"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://finlex:finlex_password@localhost:5432/finlex_db"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    google_api_key: str = ""
    google_model: str = "models/gemini-2.5-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    llm_provider: str = "gemini"

    # Embeddings
    embedding_model: str = "models/gemini-embedding-001"

    # Vector DB
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "finlex_knowledge"

    # Auth (Clerk)
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    clerk_webhook_secret: str = ""
    clerk_jwt_issuer: str = ""
    clerk_jwks_url: str = ""

    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    # File Storage
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    # Rate Limiting
    rate_limit_per_minute: int = 30
    rate_limit_per_day: int = 500

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
