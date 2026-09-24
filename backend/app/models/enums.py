from enum import StrEnum


class PapelUsuario(StrEnum):
    ADMIN = "admin"
    USUARIO = "usuario"


class TipoObra(StrEnum):
    FILME = "filme"
    SERIE = "serie"


class StatusLista(StrEnum):
    QUERO_ASSISTIR = "quero_assistir"
    ASSISTINDO = "assistindo"
    ASSISTIDO = "assistido"
