"""Punto de entrada de la API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import espacios, eventos, usuarios

app = FastAPI(
    title="Sistema de Reservaciones API",
    description="API RESTful para la gestión de espacios y reservas.",
    version="0.1.0",
)

# Permitimos orígenes locales, dominios de Vercel (*.vercel.app) y wildcard '*',
# ya que la autenticación es mediante Authorization Bearer (sin cookies).
origenes = list(settings.cors_origins_list)
if "*" not in origenes:
    origenes.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(espacios.router)
app.include_router(eventos.router)
app.include_router(usuarios.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Confirma que la API está disponible."""
    return {"status": "ok"}
