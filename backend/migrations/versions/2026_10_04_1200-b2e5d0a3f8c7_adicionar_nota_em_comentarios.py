"""adicionar nota opcional em comentários

Revision ID: b2e5d0a3f8c7
Revises: a1f4c9d2e7b6
Create Date: 2026-10-04 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b2e5d0a3f8c7"
down_revision: str | Sequence[str] | None = "a1f4c9d2e7b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("comentarios", sa.Column("nota", sa.SmallInteger(), nullable=True))
    op.create_check_constraint(
        "ck_comentarios_nota_valida",
        "comentarios",
        "nota IS NULL OR nota BETWEEN 1 AND 5",
    )


def downgrade() -> None:
    op.drop_constraint("ck_comentarios_nota_valida", "comentarios", type_="check")
    op.drop_column("comentarios", "nota")
