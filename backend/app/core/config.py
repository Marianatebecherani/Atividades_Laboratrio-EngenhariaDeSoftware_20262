from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    """Configurações da aplicação, lidas de variáveis de ambiente ou do arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    nome_app: str = "Catálogo de Filmes e Séries"
    database_url: str = "postgresql+psycopg://catalogo:catalogo@localhost:5432/catalogo"
    test_database_url: str = "postgresql+psycopg://catalogo:catalogo@localhost:5432/catalogo_test"
    cors_origens: list[str] = ["http://localhost:5173"]
    tmdb_api_token: SecretStr | None = None

    # Autenticação: o segredo é obrigatório e deve vir do ambiente (.env).
    jwt_segredo: str
    jwt_algoritmo: str = "HS256"
    jwt_expiracao_minutos: int = 60

    # Administrador criado pelo seed. Sem e-mail e senha definidos, o seed não cria o admin.
    admin_nome: str = "Administrador"
    admin_email: str | None = None
    admin_senha: str | None = None


@lru_cache
def obter_configuracoes() -> Configuracoes:
    return Configuracoes()
