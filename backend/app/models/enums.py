from enum import StrEnum


class PapelUsuario(StrEnum):
    ADMIN = "admin"
    USUARIO = "usuario"


class StatusLista(StrEnum):
    QUERO_ASSISTIR = "quero_assistir"
    ASSISTINDO = "assistindo"
    ASSISTIDO = "assistido"
