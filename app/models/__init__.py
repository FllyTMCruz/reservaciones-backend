"""Registro central de modelos ORM.
 
Importar los tres modelos aquí garantiza que SQLAlchemy los conozca a
todos antes de resolver relaciones declaradas como texto (por ejemplo,
relationship("EventoReservacion", ...) dentro de Usuario). Sin este
import, cualquier módulo que solo necesite un modelo (como
app/routers/espacios.py, que solo usa Espacio) dejaría a los demás sin
cargar y SQLAlchemy fallaría al mapear las relaciones.
"""
 
from app.models.espacio import Espacio
from app.models.evento_reservacion import EventoReservacion
from app.models.usuario import Usuario
 
__all__ = ["Usuario", "Espacio", "EventoReservacion"]