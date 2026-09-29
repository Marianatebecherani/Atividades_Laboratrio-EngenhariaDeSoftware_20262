from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

NomeGenero = Annotated[str, AfterValidator(str.strip), Field(min_length=1, max_length=50)]


class GeneroEntrada(BaseModel):
    nome: NomeGenero


class GeneroResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
