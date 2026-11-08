"""Configuración centralizada de variables de entorno."""

from pydantic import Field, field_validator
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

    # Orígenes del frontend permitidos por CORS, separados por coma.
    # Permitimos wildcard '*' ya que la autenticación es por header Bearer (sin cookies),
    # además de los dominios específicos de Vercel y desarrollo local.
    cors_origins: str = Field(
        default="*,http://localhost:4200,https://reservaciones-frontend-fly-tmc-ruz.vercel.app,https://reservaciones-frontend.vercel.app",
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def usar_driver_psycopg2(cls, v: str) -> str:
        """Asegura el uso del driver psycopg2 (definido en requirements.txt).

        En SQLAlchemy 2.1+, el esquema genérico 'postgresql://' intenta usar
        'psycopg' (v3) por defecto; normalizar a 'postgresql+psycopg2://'
        garantiza compatibilidad con psycopg2-binary en cualquier entorno.
        """
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg2://", 1)
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]


settings = Settings()
