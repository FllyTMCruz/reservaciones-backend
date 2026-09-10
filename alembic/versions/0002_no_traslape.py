"""Agrega la restricción de no-traslape de horarios por espacio.
dos eventos del mismo id_espacio no pueden tener rangos
fecha_inicio/fecha_fin que se encimen, mientras el evento no esté
Cancelado. Se implementa a nivel de base de datos con una EXCLUSION
CONSTRAINT de PostgreSQL (requiere la extensión btree_gist para poder
combinar una columna de igualdad (id_espacio) con un rango de tiempo).

Revision ID: 0002_no_traslape
Revises: 0001_initial
Create Date: 2026-09-09 00:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_no_traslape"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    # La exclusion constraint necesita esta extensión para poder usar
    # gist sobre una columna normal (id_espacio) combinada con un rango.
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    op.execute(
        """
        ALTER TABLE evento_reservacion
        ADD CONSTRAINT no_traslape_por_espacio
        EXCLUDE USING gist (
            id_espacio WITH =,
            tsrange(fecha_inicio, fecha_fin) WITH &&
        )
        WHERE (estado_evento != 'Cancelado'::estado_evento_enum);
        """
    )


def downgrade():
    op.execute(
        "ALTER TABLE evento_reservacion DROP CONSTRAINT no_traslape_por_espacio;"
    )
    # No se elimina la extensión btree_gist por si algo más de la BD la usa.