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

# Los orígenes permitidos salen de CORS_ORIGINS (ver app/core/config.py).
# No usamos allow_origins=["*"] porque, combinado con allow_credentials=True,
# es una configuración que el propio spec de CORS desaconseja y que además
# dejaría la API abierta a cualquier dominio en producción. La autenticación
# es por header Authorization (Bearer), no por cookies, así que no
# necesitamos allow_credentials=True.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
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