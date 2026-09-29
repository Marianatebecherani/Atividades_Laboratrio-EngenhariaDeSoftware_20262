"""ordenar titulos e generos em portugues

Revision ID: 50d19cef9de0
Revises: 2aa15acb8eb7
Create Date: 2026-09-25 16:31:22.383723

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "50d19cef9de0"
down_revision: str | Sequence[str] | None = "2aa15acb8eb7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Collation ICU do Postgres: ordena em português, com acentos junto das letras.
# O Alembic não detecta mudanças de collation, por isso esta migração foi escrita à mão.
COLUNAS = (("obras", "titulo", 200), ("generos", "nome", 50))


def upgrade() -> None:
    """Upgrade schema."""
    for tabela, coluna, tamanho in COLUNAS:
        op.alter_column(
            tabela,
            coluna,
            existing_type=sa.String(tamanho),
            type_=sa.String(tamanho, collation="pt-BR-x-icu"),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    for tabela, coluna, tamanho in COLUNAS:
        op.alter_column(
            tabela,
            coluna,
            existing_type=sa.String(tamanho, collation="pt-BR-x-icu"),
            type_=sa.String(tamanho, collation="default"),
            existing_nullable=False,
        )
