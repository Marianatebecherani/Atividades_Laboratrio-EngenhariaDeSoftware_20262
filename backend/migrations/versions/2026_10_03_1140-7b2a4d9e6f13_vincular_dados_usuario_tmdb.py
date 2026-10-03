"""vincular dados do usuário a filmes TMDb sem copiar metadados

Revision ID: 7b2a4d9e6f13
Revises: 50d19cef9de0
Create Date: 2026-10-03 11:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7b2a4d9e6f13"
down_revision: str | Sequence[str] | None = "50d19cef9de0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("itens_lista", "obra_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("itens_lista", sa.Column("tmdb_id", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_itens_lista_um_alvo",
        "itens_lista",
        "(obra_id IS NOT NULL AND tmdb_id IS NULL) OR (obra_id IS NULL AND tmdb_id IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_itens_lista_tmdb_id_positivo",
        "itens_lista",
        "tmdb_id IS NULL OR tmdb_id > 0",
    )
    op.create_unique_constraint(
        "uq_itens_lista_usuario_tmdb", "itens_lista", ["usuario_id", "tmdb_id"]
    )
    op.create_index("ix_itens_lista_tmdb_id", "itens_lista", ["tmdb_id"])

    op.alter_column("avaliacoes", "obra_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("avaliacoes", sa.Column("tmdb_id", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_avaliacoes_um_alvo",
        "avaliacoes",
        "(obra_id IS NOT NULL AND tmdb_id IS NULL) OR (obra_id IS NULL AND tmdb_id IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_avaliacoes_tmdb_id_positivo",
        "avaliacoes",
        "tmdb_id IS NULL OR tmdb_id > 0",
    )
    op.create_unique_constraint(
        "uq_avaliacoes_usuario_tmdb", "avaliacoes", ["usuario_id", "tmdb_id"]
    )
    op.create_index("ix_avaliacoes_tmdb_id", "avaliacoes", ["tmdb_id"])

    op.create_table(
        "favoritos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("tmdb_id", sa.Integer(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("tmdb_id > 0", name="ck_favoritos_tmdb_id_positivo"),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            name="fk_favoritos_usuario_id_usuarios",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_favoritos"),
        sa.UniqueConstraint("usuario_id", "tmdb_id", name="uq_favoritos_usuario_tmdb"),
    )
    op.create_index("ix_favoritos_tmdb_id", "favoritos", ["tmdb_id"])


def downgrade() -> None:
    conexao = op.get_bind()
    possui_dados_tmdb = conexao.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM favoritos) "
            "OR EXISTS (SELECT 1 FROM itens_lista WHERE tmdb_id IS NOT NULL) "
            "OR EXISTS (SELECT 1 FROM avaliacoes WHERE tmdb_id IS NOT NULL)"
        )
    ).scalar_one()
    if possui_dados_tmdb:
        raise RuntimeError(
            "Downgrade bloqueado: remova os favoritos, listas e avaliações TMDb antes."
        )

    op.drop_index("ix_favoritos_tmdb_id", table_name="favoritos")
    op.drop_table("favoritos")

    op.drop_index("ix_avaliacoes_tmdb_id", table_name="avaliacoes")
    op.drop_constraint("uq_avaliacoes_usuario_tmdb", "avaliacoes", type_="unique")
    op.drop_constraint("ck_avaliacoes_tmdb_id_positivo", "avaliacoes", type_="check")
    op.drop_constraint("ck_avaliacoes_um_alvo", "avaliacoes", type_="check")
    op.drop_column("avaliacoes", "tmdb_id")
    op.alter_column("avaliacoes", "obra_id", existing_type=sa.Integer(), nullable=False)

    op.drop_index("ix_itens_lista_tmdb_id", table_name="itens_lista")
    op.drop_constraint("uq_itens_lista_usuario_tmdb", "itens_lista", type_="unique")
    op.drop_constraint("ck_itens_lista_tmdb_id_positivo", "itens_lista", type_="check")
    op.drop_constraint("ck_itens_lista_um_alvo", "itens_lista", type_="check")
    op.drop_column("itens_lista", "tmdb_id")
    op.alter_column("itens_lista", "obra_id", existing_type=sa.Integer(), nullable=False)
