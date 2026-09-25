# Database

Dados de exemplo usados para popular o banco da aplicação.

- O banco é o PostgreSQL, provisionado em [infra/](../infra/README.md).
- O esquema e as migrações (Alembic) ficam no [backend](../backend/README.md), em `backend/migrations/`.

## Seed

O diretório [seed/](seed/) contém os filmes carregados pelo seed do backend:

| Arquivo | Conteúdo |
| --- | --- |
| `seed/filmes.csv` | 100 filmes: título, ano, duração, classificação indicativa, gêneros e sinopse. |
| `seed/posters/` | Pôster de cada filme, nomeado pelo índice do CSV (`filme_001.png` a `filme_100.png`). |

### Formato do `filmes.csv`

Arquivo UTF-8, com colunas separadas por ponto e vírgula (`;`). Textos que contêm `;` devem ficar entre aspas.

| Coluna | Descrição |
| --- | --- |
| `indice` | Número do filme; define o nome do arquivo do pôster (`filme_<indice com 3 dígitos>`). |
| `titulo` | Título do filme (único). |
| `ano` | Ano de lançamento (a partir de 1888). |
| `duracao_min` | Duração em minutos. |
| `classificacao` | `Livre`, `10`, `12`, `14`, `16`, `18` ou `Not Rated` (sem classificação). |
| `genero` | Gêneros do filme separados por vírgula, por exemplo `Policial, Drama`. Os gêneros são criados a partir desta coluna; escreva cada nome sempre da mesma forma. |
| `sinopse` | Sinopse (opcional). |

Os pôsteres podem estar em PNG, JPEG (`.jpg`) ou WebP, com até 2 MB cada.

### Carregar os dados

A partir de `backend/`, com as migrações aplicadas:

```bash
uv run python -m app.db.seed
```

O seed pode ser executado mais de uma vez: filmes com título já cadastrado são mantidos sem alteração, inclusive seus gêneros. Para aplicar mudanças do CSV em filmes já cadastrados, recrie o banco do zero. **Isso apaga todos os dados do banco da aplicação e do banco de testes.** A partir da raiz do repositório:

```bash
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d --wait
cd backend
uv run alembic upgrade head
uv run python -m app.db.seed
```
