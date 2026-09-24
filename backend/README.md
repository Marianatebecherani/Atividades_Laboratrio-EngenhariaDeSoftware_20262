# Backend

API REST do Catálogo Pessoal de Filmes e Séries: autenticação, catálogo de obras, lista do usuário, avaliações e recomendações.

## Tecnologias

- Python 3.12+ com FastAPI
- SQLAlchemy 2 (ORM) e Alembic (migrações)
- PostgreSQL (psycopg 3)
- uv (gerenciamento de dependências)
- pytest e Ruff (testes, lint e formatação)

## Estrutura

```text
backend/
├── app/
│   ├── api/        # rotas HTTP
│   ├── core/       # configurações
│   ├── db/         # conexão e sessão do banco
│   └── main.py     # criação da aplicação FastAPI
└── tests/          # testes automatizados
```

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) instalado. O uv baixa o Python 3.12 automaticamente, se necessário.
- Banco PostgreSQL em execução. Veja [infra/](../infra/README.md) para subir o banco com Docker Compose.

## Configuração

Copie o arquivo de exemplo e ajuste as variáveis, se necessário:

```bash
cd backend
cp .env.example .env
```

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | URL de conexão com o banco da aplicação. |
| `TEST_DATABASE_URL` | URL de conexão com o banco usado pelos testes. |
| `CORS_ORIGENS` | Lista de origens autorizadas a chamar a API. |

## Execução

A partir de `backend/`:

```bash
# Instalar as dependências
uv sync

# Iniciar a API em modo de desenvolvimento (recarrega ao salvar)
uv run fastapi dev app/main.py
```

A API fica disponível em `http://localhost:8000`:

- Documentação interativa (Swagger): `http://localhost:8000/docs`
- Verificação de saúde: `GET /api/v1/saude`

## Testes e qualidade

```bash
# Executar os testes (requer o banco de testes em execução)
uv run pytest

# Verificar o lint e a formatação
uv run ruff check .
uv run ruff format --check .
```
