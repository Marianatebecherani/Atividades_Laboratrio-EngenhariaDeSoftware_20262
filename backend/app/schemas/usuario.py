from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models import PapelUsuario

SENHA_MINIMA = 8
SENHA_MAXIMA = 128

Nome = Annotated[str, Field(min_length=1, max_length=100), AfterValidator(str.strip)]
Email = Annotated[EmailStr, Field(max_length=255), AfterValidator(str.lower)]
Senha = Annotated[str, Field(min_length=SENHA_MINIMA, max_length=SENHA_MAXIMA)]


class UsuarioCadastro(BaseModel):
    nome: Nome
    email: Email
    senha: Senha


class UsuarioAtualizacao(BaseModel):
    """Campos opcionais. Trocar e-mail ou senha exige a senha atual."""

    nome: Nome | None = None
    email: Email | None = None
    senha_nova: Senha | None = None
    senha_atual: str | None = None

    @model_validator(mode="after")
    def exigir_senha_atual(self) -> "UsuarioAtualizacao":
        if (self.email or self.senha_nova) and not self.senha_atual:
            raise ValueError("Informe a senha atual para alterar o e-mail ou a senha")
        return self


class UsuarioExclusao(BaseModel):
    senha: str


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    papel: PapelUsuario
    criado_em: datetime


class TokenResposta(BaseModel):
    """Formato definido pelo padrão OAuth2 (nomes em inglês por exigência do protocolo)."""

    access_token: str
    token_type: str = "bearer"
    expira_em_minutos: int
