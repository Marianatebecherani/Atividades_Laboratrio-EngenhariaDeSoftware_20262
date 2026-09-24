from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    """Configurações da aplicação, lidas de variáveis de ambiente ou do arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    nome_app: str = "Catálogo de Filmes e Séries"
    database_url: str = "postgresql+psycopg://catalogo:catalogo@localhost:5432/catalogo"
    test_database_url: str = "postgresql+psycopg://catalogo:catalogo@localhost:5432/catalogo_test"
    cors_origens: list[str] = ["http://localhost:5173"]


@lru_cache
def obter_configuracoes() -> Configuracoes:
    return Configuracoes()
