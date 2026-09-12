"""Configuración centralizada de variables de entorno."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Sistema de Reservaciones API"
    debug: bool = False
    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_key: str = Field(alias="SUPABASE_KEY")
    supabase_jwt_secret: str = Field(alias="SUPABASE_JWT_SECRET")
    database_url: str = Field(alias="DATABASE_URL")
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")

    # Orígenes del frontend permitidos por CORS, separados por coma, ej:
    # "https://reservaciones.vercel.app,http://localhost:4200"
    # Antes main.py usaba allow_origins=["*"] junto con allow_credentials=True,
    # una combinación que el propio spec de CORS desaconseja y que además
    # dejaba la API abierta a cualquier dominio en producción.
    cors_origins: str = Field(default="http://localhost:4200", alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]


settings = Settings()
