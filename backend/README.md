# Backend

API REST do Catálogo Pessoal de Filmes e Séries: autenticação, catálogo de obras, lista do usuário, avaliações e recomendações.

## Tecnologias

- Python 3.12+ com FastAPI
- SQLAlchemy 2 (ORM) e Alembic (migrações)
- PostgreSQL (psycopg 3)
- pwdlib com Argon2 (hash de senhas)
- uv (gerenciamento de dependências)
- pytest e Ruff (testes, lint e formatação)

## Estrutura

```text
backend/
├── app/
│   ├── api/        # rotas HTTP
│   ├── core/       # configurações e segurança
│   ├── db/         # conexão, sessão e seed do banco
│   ├── models/     # modelos ORM (tabelas)
│   └── main.py     # criação da aplicação FastAPI
├── migrations/     # migrações do Alembic
└── tests/          # testes automatizados
```

## Modelo de dados

| Tabela | Conteúdo |
| --- | --- |
| `usuarios` | Usuários, com papel `admin` ou `usuario`. |
| `obras` | Filmes e séries: título, tipo, ano de lançamento, sinopse (opcional), classificação indicativa, duração em minutos (filmes) ou temporadas (séries). |
| `generos` | Gêneros das obras. |
| `obras_generos` | Associação N:N entre obras e gêneros. |
| `posters` | Imagem do pôster de cada obra (JPEG, PNG ou WebP, até 2 MB). |
| `itens_lista` | Lista pessoal do usuário, com status `quero_assistir`, `assistindo` ou `assistido`. |
| `avaliacoes` | Nota de 1 a 5 e comentário opcional; uma avaliação por usuário e obra. |

Regras garantidas pelo banco:

- Filmes exigem duração em minutos; séries exigem número de temporadas.
- Classificação indicativa: 0 (livre), 10, 12, 14, 16 ou 18.
- Excluir uma obra remove o pôster, os gêneros associados, os itens de lista e as avaliações dela.
- Não é possível excluir um gênero associado a alguma obra.

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
| `ADMIN_NOME`, `ADMIN_EMAIL`, `ADMIN_SENHA` | Dados do administrador criado pelo seed. Sem e-mail e senha, o admin não é criado. |

## Banco de dados

A partir de `backend/`:

```bash
# Aplicar as migrações
uv run alembic upgrade head

# Popular com o administrador, os gêneros e as obras de exemplo
uv run python -m app.db.seed
```

O seed pode ser executado mais de uma vez: registros já existentes são mantidos.

Ao alterar os modelos, gere uma nova migração e revise o arquivo criado em `migrations/versions/` antes de aplicá-lo:

```bash
uv run alembic revision --autogenerate -m "descrição da mudança"
```

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

Os testes aplicam as migrações no banco definido em `TEST_DATABASE_URL` e desfazem as alterações de cada teste ao final.
