"""Punto de entrada de la API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import espacios, eventos, usuarios

app = FastAPI(
    title="Sistema de Reservaciones API",
    description="API RESTful para la gestión de espacios y reservas.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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