"""Initial migration: create espacio and evento_reservacion tables; create usuario via raw SQL

Revision ID: 0001_initial
Revises: 
Create Date: 2026-09-09 16:35:00.000000
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
    # Create enum for rol_usuario since usuario table is created via raw SQL and needs it.
    rol_enum = postgresql.ENUM('Cliente', 'Coordinador', 'Administración', name='rol_usuario_enum')
    rol_enum.create(op.get_bind(), checkfirst=True)

    # 1) Create usuario table first via raw SQL (references Supabase auth.users).
    op.execute('''
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    rol rol_usuario_enum NOT NULL
);
''')

    # 2) Create espacio table.
    op.create_table(
        'espacio',
        sa.Column('id_espacio', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('nombre_espacio', sa.Text(), nullable=False),
        sa.Column('capacidad_maxima', sa.Integer(), nullable=False),
    )

    # 3) Create evento_reservacion table last (depends on usuario and espacio).
    op.create_table(
        'evento_reservacion',
        sa.Column('id_evento', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_usuario', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('id_espacio', sa.Integer(), nullable=False),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
        sa.Column('fecha_fin', sa.DateTime(), nullable=False),
        sa.Column('tipo_evento', sa.String(length=100), nullable=False),
        sa.Column('invitados_estimados', sa.Integer(), nullable=False),
        sa.Column(
            'estado_evento',
            sa.Enum('Pendiente', 'Confirmado', 'Cancelado', name='estado_evento_enum'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['id_espacio'], ['espacio.id_espacio'], ondelete='RESTRICT'),
    )


def downgrade():
    # Drop dependent table first.
    op.drop_table('evento_reservacion')

    # Drop principal tables after dependents.
    op.execute('DROP TABLE IF EXISTS usuario;')
    op.drop_table('espacio')

    # Drop enums after all tables that use them are gone.
    estado_enum = postgresql.ENUM('Pendiente', 'Confirmado', 'Cancelado', name='estado_evento_enum')
    estado_enum.drop(op.get_bind(), checkfirst=True)

    rol_enum = postgresql.ENUM('Cliente', 'Coordinador', 'Administración', name='rol_usuario_enum')
    rol_enum.drop(op.get_bind(), checkfirst=True)
