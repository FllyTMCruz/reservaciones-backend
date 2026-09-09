"""Initial migration: create espacio and evento_reservacion tables; create usuario via raw SQL

Revision ID: 0001_initial
Revises: 
Create Date: 2026-09-09 16:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create espacio table
    op.create_table(
        'espacio',
        sa.Column('id_espacio', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('nombre_espacio', sa.Text(), nullable=False),
        sa.Column('capacidad_maxima', sa.Integer(), nullable=False),
    )

    # Create enums used by evento_reservacion
    estado_enum = postgresql.ENUM('Pendiente', 'Confirmado', 'Cancelado', name='estado_evento_enum')
    estado_enum.create(op.get_bind(), checkfirst=True)

    # Create evento_reservacion table
    op.create_table(
        'evento_reservacion',
        sa.Column('id_evento', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_usuario', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('id_espacio', sa.Integer(), nullable=False),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
        sa.Column('fecha_fin', sa.DateTime(), nullable=False),
        sa.Column('tipo_evento', sa.String(length=100), nullable=False),
        sa.Column('invitados_estimados', sa.Integer(), nullable=False),
        sa.Column('estado_evento', sa.Enum(name='estado_evento_enum'), nullable=False),
        sa.ForeignKeyConstraint(['id_espacio'], ['espacio.id_espacio'], ondelete='CASCADE')
    )

    # Create usuario table via raw SQL to reference auth.users(id)
    op.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            rol TEXT NOT NULL
        );
    ''')


def downgrade():
    # Drop usuario table created via raw SQL
    op.execute('DROP TABLE IF EXISTS usuario;')

    # Drop evento_reservacion and estado enum
    op.drop_table('evento_reservacion')
    estado_enum = postgresql.ENUM('Pendiente', 'Confirmado', 'Cancelado', name='estado_evento_enum')
    estado_enum.drop(op.get_bind(), checkfirst=True)

    # Drop espacio table
    op.drop_table('espacio')
