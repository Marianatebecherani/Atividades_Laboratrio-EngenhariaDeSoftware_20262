"""remover catálogo local e manter dados TMDb

Revision ID: 9d3c7a1b5e20
Revises: 7b2a4d9e6f13
Create Date: 2026-10-03 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9d3c7a1b5e20"
down_revision: str | Sequence[str] | None = "7b2a4d9e6f13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

COLLATION_PT_BR = "pt-BR-x-icu"


def upgrade() -> None:
    op.execute(sa.text("DELETE FROM itens_lista WHERE tmdb_id IS NULL"))
    op.execute(sa.text("DELETE FROM avaliacoes WHERE tmdb_id IS NULL"))

    op.drop_constraint("ck_itens_lista_um_alvo", "itens_lista", type_="check")
    op.drop_constraint("uq_itens_lista_usuario_obra", "itens_lista", type_="unique")
    op.drop_constraint("fk_itens_lista_obra_id_obras", "itens_lista", type_="foreignkey")
    op.drop_index("ix_itens_lista_obra_id", table_name="itens_lista")
    op.drop_column("itens_lista", "obra_id")
    op.alter_column("itens_lista", "tmdb_id", existing_type=sa.Integer(), nullable=False)

    op.drop_constraint("ck_avaliacoes_um_alvo", "avaliacoes", type_="check")
    op.drop_constraint("uq_avaliacoes_usuario_obra", "avaliacoes", type_="unique")
    op.drop_constraint("fk_avaliacoes_obra_id_obras", "avaliacoes", type_="foreignkey")
    op.drop_index("ix_avaliacoes_obra_id", table_name="avaliacoes")
    op.drop_column("avaliacoes", "obra_id")
    op.alter_column("avaliacoes", "tmdb_id", existing_type=sa.Integer(), nullable=False)

    op.drop_table("posters")
    op.drop_index("ix_obras_generos_genero_id", table_name="obras_generos")
    op.drop_table("obras_generos")
    op.drop_index("ix_obras_titulo", table_name="obras")
    op.drop_index("ix_obras_tipo", table_name="obras")
    op.drop_index("ix_obras_ano_lancamento", table_name="obras")
    op.drop_table("obras")
    op.drop_table("generos")


def downgrade() -> None:
    op.create_table(
        "generos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=50, collation=COLLATION_PT_BR), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_generos")),
        sa.UniqueConstraint("nome", name=op.f("uq_generos_nome")),
    )
    op.create_table(
        "obras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=200, collation=COLLATION_PT_BR), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("filme", "serie", name="tipo_obra", native_enum=False, create_constraint=True),
            nullable=False,
        ),
        sa.Column("ano_lancamento", sa.SmallInteger(), nullable=False),
        sa.Column("sinopse", sa.Text(), nullable=True),
        sa.Column("classificacao_indicativa", sa.SmallInteger(), nullable=True),
        sa.Column("duracao_minutos", sa.SmallInteger(), nullable=True),
        sa.Column("temporadas", sa.SmallInteger(), nullable=True),
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(tipo = 'filme' AND duracao_minutos IS NOT NULL AND temporadas IS NULL) "
            "OR (tipo = 'serie' AND temporadas IS NOT NULL AND duracao_minutos IS NULL)",
            name=op.f("ck_obras_duracao_conforme_tipo"),
        ),
        sa.CheckConstraint("ano_lancamento >= 1888", name=op.f("ck_obras_ano_lancamento_valido")),
        sa.CheckConstraint(
            "classificacao_indicativa IN (0, 10, 12, 14, 16, 18)",
            name=op.f("ck_obras_classificacao_indicativa_valida"),
        ),
        sa.CheckConstraint("duracao_minutos > 0", name=op.f("ck_obras_duracao_minutos_positiva")),
        sa.CheckConstraint("temporadas > 0", name=op.f("ck_obras_temporadas_positiva")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_obras")),
    )
    op.create_index(op.f("ix_obras_ano_lancamento"), "obras", ["ano_lancamento"])
    op.create_index(op.f("ix_obras_tipo"), "obras", ["tipo"])
    op.create_index(op.f("ix_obras_titulo"), "obras", ["titulo"])
    op.create_table(
        "obras_generos",
        sa.Column("obra_id", sa.Integer(), nullable=False),
        sa.Column("genero_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["genero_id"],
            ["generos.id"],
            name=op.f("fk_obras_generos_genero_id_generos"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["obra_id"],
            ["obras.id"],
            name=op.f("fk_obras_generos_obra_id_obras"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("obra_id", "genero_id", name=op.f("pk_obras_generos")),
    )
    op.create_index("ix_obras_generos_genero_id", "obras_generos", ["genero_id"])
    op.create_table(
        "posters",
        sa.Column("obra_id", sa.Integer(), nullable=False),
        sa.Column("conteudo", sa.LargeBinary(), nullable=False),
        sa.Column("tipo_mime", sa.String(length=20), nullable=False),
        sa.Column("tamanho_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "tipo_mime IN ('image/jpeg', 'image/png', 'image/webp')",
            name=op.f("ck_posters_tipo_mime_permitido"),
        ),
        sa.CheckConstraint(
            "tamanho_bytes > 0 AND tamanho_bytes <= 2097152",
            name=op.f("ck_posters_tamanho_permitido"),
        ),
        sa.ForeignKeyConstraint(
            ["obra_id"], ["obras.id"], name=op.f("fk_posters_obra_id_obras"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("obra_id", name=op.f("pk_posters")),
    )

    op.alter_column("itens_lista", "tmdb_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("itens_lista", sa.Column("obra_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_itens_lista_obra_id_obras",
        "itens_lista",
        "obras",
        ["obra_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_itens_lista_usuario_obra", "itens_lista", ["usuario_id", "obra_id"]
    )
    op.create_index("ix_itens_lista_obra_id", "itens_lista", ["obra_id"])
    op.create_check_constraint(
        "ck_itens_lista_um_alvo",
        "itens_lista",
        "(obra_id IS NOT NULL AND tmdb_id IS NULL) OR (obra_id IS NULL AND tmdb_id IS NOT NULL)",
    )

    op.alter_column("avaliacoes", "tmdb_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("avaliacoes", sa.Column("obra_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_avaliacoes_obra_id_obras",
        "avaliacoes",
        "obras",
        ["obra_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_avaliacoes_usuario_obra", "avaliacoes", ["usuario_id", "obra_id"]
    )
    op.create_index("ix_avaliacoes_obra_id", "avaliacoes", ["obra_id"])
    op.create_check_constraint(
        "ck_avaliacoes_um_alvo",
        "avaliacoes",
        "(obra_id IS NOT NULL AND tmdb_id IS NULL) OR (obra_id IS NULL AND tmdb_id IS NOT NULL)",
    )
