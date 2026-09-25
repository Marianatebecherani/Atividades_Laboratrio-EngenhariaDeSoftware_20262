from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DIRETORIO_RAIZ = Path(__file__).resolve().parents[3]


class Configuracoes(BaseSettings):
    """Configurações da aplicação, lidas de variáveis de ambiente ou do arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    nome_app: str = "Catálogo de Filmes e Séries"
    database_url: str = "postgresql+psycopg://catalogo:catalogo@localhost:5432/catalogo"
    test_database_url: str = "postgresql+psycopg://catalogo:catalogo@localhost:5432/catalogo_test"
    cors_origens: list[str] = ["http://localhost:5173"]

    # Administrador criado pelo seed. Sem e-mail e senha definidos, o seed não cria o admin.
    admin_nome: str = "Administrador"
    admin_email: str | None = None
    admin_senha: str | None = None

    # Diretório com o filmes.csv e a pasta posters/ usados pelo seed.
    seed_diretorio: Path = DIRETORIO_RAIZ / "database" / "seed"


@lru_cache
def obter_configuracoes() -> Configuracoes:
    return Configuracoes()
