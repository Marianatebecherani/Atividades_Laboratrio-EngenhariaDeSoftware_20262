"""criar tabela de comentários públicos de filmes

Revision ID: a1f4c9d2e7b6
Revises: 9d3c7a1b5e20
Create Date: 2026-10-04 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1f4c9d2e7b6"
down_revision: str | Sequence[str] | None = "9d3c7a1b5e20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comentarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("tmdb_id", sa.Integer(), nullable=False),
        sa.Column("conteudo", sa.String(length=2000), nullable=False),
        sa.Column("removido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("tmdb_id > 0", name="ck_comentarios_tmdb_id_positivo"),
        sa.CheckConstraint("length(trim(conteudo)) > 0", name="ck_comentarios_conteudo_nao_vazio"),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            name="fk_comentarios_usuario_id_usuarios",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_comentarios"),
    )
    op.create_index("ix_comentarios_tmdb_criado", "comentarios", ["tmdb_id", "criado_em"])


def downgrade() -> None:
    op.drop_index("ix_comentarios_tmdb_criado", table_name="comentarios")
    op.drop_table("comentarios")
