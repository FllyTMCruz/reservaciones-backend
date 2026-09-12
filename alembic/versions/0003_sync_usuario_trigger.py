"""Trigger para sincronizar auth.users con la tabla usuario.

Cuando alguien se registra vía Supabase Auth, se crea un registro en
auth.users pero NO en la tabla `usuario` de la aplicación. Este trigger
crea automáticamente esa fila justo después del registro, tomando
`nombre` y `rol` de los metadatos que mande el frontend al hacer signUp,
con valores por defecto si no los manda.

Revision ID: 0003_sync_usuario_trigger
Revises: 0002_no_traslape
Create Date: 2026-09-10 00:00:00.000000
"""

from alembic import op

revision = "0003_sync_usuario_trigger"
down_revision = "0002_no_traslape"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS trigger AS $$
        BEGIN
            INSERT INTO public.usuario (id_usuario, nombre, correo, rol)
            VALUES (
                NEW.id,
                COALESCE(NEW.raw_user_meta_data->>'nombre', split_part(NEW.email, '@', 1)),
                NEW.email,
                COALESCE(
                    (NEW.raw_user_meta_data->>'rol')::rol_usuario_enum,
                    'Cliente'::rol_usuario_enum
                )
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;
        """
    )

    op.execute(
        """
        CREATE TRIGGER on_auth_user_created
        AFTER INSERT ON auth.users
        FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
        """
    )


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;")
    op.execute("DROP FUNCTION IF EXISTS public.handle_new_user();")
