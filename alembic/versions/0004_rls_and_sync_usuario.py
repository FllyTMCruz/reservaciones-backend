"""Habilita RLS en tablas públicas y sincroniza cambios de usuario hacia auth.users.

Revision ID: 0004_rls_and_sync_usuario
Revises: 0003_sync_usuario_trigger
Create Date: 2026-11-07 16:58:00.000000
"""

from alembic import op

revision = "0004_rls_and_sync_usuario"
down_revision = "0003_sync_usuario_trigger"
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE "public"."alembic_version" ENABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE "public"."usuario" ENABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE "public"."espacio" ENABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE "public"."evento_reservacion" ENABLE ROW LEVEL SECURITY;')

    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.sync_usuario_to_auth_users()
        RETURNS trigger AS $$
        BEGIN
            IF NEW.rol IS DISTINCT FROM OLD.rol OR NEW.nombre IS DISTINCT FROM OLD.nombre THEN
                UPDATE auth.users
                SET raw_user_meta_data = COALESCE(raw_user_meta_data, '{}'::jsonb)
                    || jsonb_build_object('rol', NEW.rol::text, 'nombre', NEW.nombre)
                WHERE id = NEW.id_usuario;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER on_public_usuario_updated
        AFTER UPDATE OF rol, nombre ON public.usuario
        FOR EACH ROW EXECUTE FUNCTION public.sync_usuario_to_auth_users();
        """
    )

    op.execute(
        "REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;"
    )
    op.execute(
        "REVOKE EXECUTE ON FUNCTION public.sync_usuario_to_auth_users() FROM PUBLIC, anon, authenticated;"
    )


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS on_public_usuario_updated ON public.usuario;")
    op.execute("DROP FUNCTION IF EXISTS public.sync_usuario_to_auth_users();")
    op.execute('ALTER TABLE "public"."evento_reservacion" DISABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE "public"."espacio" DISABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE "public"."usuario" DISABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE "public"."alembic_version" DISABLE ROW LEVEL SECURITY;')
