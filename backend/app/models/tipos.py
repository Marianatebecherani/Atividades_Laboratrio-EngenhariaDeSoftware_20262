from enum import StrEnum

from sqlalchemy import Enum


def enum_como_texto(enum: type[StrEnum], nome: str) -> Enum:
    """Armazena o enum como VARCHAR com CHECK, evitando tipos ENUM nativos do Postgres."""
    return Enum(
        enum,
        name=nome,
        native_enum=False,
        create_constraint=True,
        length=max(len(item.value) for item in enum),
        values_callable=lambda itens: [item.value for item in itens],
    )
