from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/credit_pm")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    bolagsverket_api_key: str = os.getenv("BOLAGSVERKET_API_KEY", "")
    require_auth: bool = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    
    # OpenRouter configuration
    openrouter_url: str = os.getenv("open_router_url", "https://openrouter.ai/api/v1/chat/completions")
    openrouter_authorization: str = os.getenv("Authorization", "")
    
    class Config:
        env_file = ".env"

settings = Settings()