# Backend

API REST do Catálogo Pessoal de Filmes e Séries: autenticação, catálogo de obras, lista do usuário, avaliações e recomendações.

## Tecnologias

- Python 3.12+ com FastAPI
- SQLAlchemy 2 (ORM) e Alembic (migrações)
- PostgreSQL (psycopg 3)
- pwdlib com Argon2 (hash de senhas) e PyJWT (tokens de acesso)
- uv (gerenciamento de dependências)
- pytest e Ruff (testes, lint e formatação)

## Estrutura

```text
backend/
├── app/
│   ├── api/           # rotas HTTP, dependências e tratamento de erros
│   ├── core/          # configurações, segurança e erros de negócio
│   ├── db/            # conexão, sessão e seed do banco
│   ├── models/        # modelos ORM (tabelas)
│   ├── repositories/  # acesso a dados (padrão Repository)
│   ├── schemas/       # contratos de entrada e saída da API (Pydantic)
│   ├── services/      # regras de negócio
│   └── main.py        # criação da aplicação FastAPI
├── migrations/     # migrações do Alembic
└── tests/          # testes automatizados
```

## Modelo de dados

| Tabela | Conteúdo |
| --- | --- |
| `usuarios` | Usuários, com papel `admin` ou `usuario`. |
| `obras` | Filmes e séries: título, tipo, ano de lançamento, sinopse (opcional), classificação indicativa (opcional), duração em minutos (filmes) ou temporadas (séries). |
| `generos` | Gêneros das obras. |
| `obras_generos` | Associação N:N entre obras e gêneros. |
| `posters` | Imagem do pôster de cada obra (JPEG, PNG ou WebP, até 2 MB). |
| `itens_lista` | Lista pessoal do usuário, com status `quero_assistir`, `assistindo` ou `assistido`. |
| `avaliacoes` | Nota de 1 a 5 e comentário opcional; uma avaliação por usuário e obra. |

Regras garantidas pelo banco:

- Filmes exigem duração em minutos; séries exigem número de temporadas.
- Classificação indicativa: 0 (livre), 10, 12, 14, 16 ou 18; vazia quando a obra não é classificada.
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
| `JWT_SEGREDO` | Obrigatório. Segredo usado para assinar os tokens. Gere com `uv run python -c "import secrets; print(secrets.token_urlsafe(48))"`. |
| `JWT_EXPIRACAO_MINUTOS` | Validade do token de acesso (padrão: 60). |
| `SEED_DIRETORIO` | Opcional. Diretório com o `filmes.csv` e a pasta `posters/` (padrão: `database/seed` na raiz do repositório). |

## Banco de dados

A partir de `backend/`:

```bash
# Aplicar as migrações
uv run alembic upgrade head

# Popular com o administrador, os gêneros e os 100 filmes de exemplo (com pôsteres)
uv run python -m app.db.seed
```

Os filmes e os pôsteres vêm de [database/seed/](../database/README.md), onde também está descrito o formato do CSV. O seed pode ser executado mais de uma vez: registros já existentes são mantidos.

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

## Endpoints

Todas as rotas usam o prefixo `/api/v1`. A documentação completa, com exemplos, fica no Swagger (`/docs`).

| Método | Rota | Autenticação | Descrição |
| --- | --- | --- | --- |
| `GET` | `/saude` | — | Verifica se a API e o banco estão disponíveis. |
| `POST` | `/auth/cadastro` | — | Cadastra um usuário comum (nome, e-mail e senha com no mínimo 8 caracteres). |
| `POST` | `/auth/login` | — | Formulário OAuth2 (`username` = e-mail, `password`); retorna um token JWT válido por 60 minutos. |
| `GET` | `/usuarios/me` | Token | Dados do usuário autenticado. |
| `PATCH` | `/usuarios/me` | Token | Altera nome, e-mail ou senha. E-mail e senha exigem `senha_atual`. |
| `DELETE` | `/usuarios/me` | Token | Exclui a conta, a lista e as avaliações do usuário. Exige a senha. O único administrador não pode excluir a própria conta. |
| `GET` | `/usuarios/me/lista` | Token | Lista pessoal, paginada, com filtro opcional `status` (`quero_assistir`, `assistindo`, `assistido`). |
| `PUT` | `/usuarios/me/lista/{obra_id}` | Token | Adiciona a obra à lista (`201`) ou altera o status (`200`). Corpo: `{"status": "..."}`. |
| `DELETE` | `/usuarios/me/lista/{obra_id}` | Token | Remove a obra da lista. |
| `GET` | `/generos` | — | Lista os gêneros em ordem alfabética. |
| `POST` | `/generos` | Admin | Cadastra um gênero (nome único, sem diferenciar maiúsculas). |
| `PUT` | `/generos/{id}` | Admin | Renomeia um gênero. |
| `DELETE` | `/generos/{id}` | Admin | Exclui um gênero; retorna `409` se houver obras associadas. |
| `GET` | `/obras` | — | Busca paginada. Veja os parâmetros abaixo. |
| `GET` | `/obras/{id}` | — | Detalhes da obra, com gêneros, média de notas e URL do pôster. |
| `POST` | `/obras` | Admin | Cadastra uma obra (JSON). Filmes exigem `duracao_minutos`; séries, `temporadas`. |
| `PUT` | `/obras/{id}` | Admin | Substitui todos os dados da obra. |
| `DELETE` | `/obras/{id}` | Admin | Exclui a obra, com pôster, itens de lista e avaliações. |
| `GET` | `/obras/{id}/avaliacoes` | — | Avaliações da obra, paginadas, mais recentes primeiro, com o nome do autor. |
| `PUT` | `/obras/{id}/avaliacoes/me` | Token | Cria (`201`) ou edita (`200`) a avaliação do usuário: nota inteira de 1 a 5 e comentário opcional (até 2000 caracteres). |
| `DELETE` | `/obras/{id}/avaliacoes/me` | Token | Remove a avaliação do usuário. |
| `DELETE` | `/avaliacoes/{id}` | Admin | Remove qualquer avaliação (moderação). |
| `GET` | `/obras/{id}/poster` | — | Imagem do pôster. |
| `PUT` | `/obras/{id}/poster` | Admin | Envia ou substitui o pôster (`multipart/form-data`, campo `arquivo`; PNG, JPEG ou WebP até 2 MB). |
| `DELETE` | `/obras/{id}/poster` | Admin | Remove o pôster. |

### Parâmetros de `GET /obras`

| Parâmetro | Descrição |
| --- | --- |
| `texto` | Parte do título, sem diferenciar maiúsculas. |
| `tipo` | `filme` ou `serie`. |
| `generos` | Ids de gêneros; pode ser repetido (`?generos=1&generos=2`) e retorna obras com qualquer um deles. |
| `ano_de`, `ano_ate` | Faixa de ano de lançamento. |
| `nota_minima` | Média mínima de notas (1 a 5). |
| `classificacoes` | Classificações indicativas aceitas; pode ser repetido. |
| `ordenar_por` | `media` (padrão), `titulo` ou `ano_lancamento`. Obras sem avaliação ficam no fim. |
| `direcao` | `asc` ou `desc`. Padrão: crescente para título, decrescente para os demais. |
| `pagina`, `tamanho` | Paginação (padrão: página 1 com 20 itens; máximo de 100 por página). |

Com um token válido, `GET /obras` e `GET /obras/{id}` trazem em cada obra o campo `meu_status`, com o status dela na lista do usuário. Sem token, ou com token inválido, a rota continua pública e `meu_status` vem nulo.

A resposta tem o formato `{"itens": [...], "total": 100, "pagina": 1, "tamanho": 20}`.

Nas rotas autenticadas, envie o cabeçalho `Authorization: Bearer <token>`. No Swagger, use o botão **Authorize** e informe o e-mail e a senha.

Erros seguem o formato `{"detail": "mensagem"}`: `401` para token ou credenciais inválidos, `403` para senha incorreta ou falta de permissão, `404` para recurso inexistente, `409` para conflitos (como e-mail já cadastrado), `413`/`415` para pôster grande demais ou em formato não aceito e `422` para dados inválidos.

## Testes e qualidade

```bash
# Executar os testes (requer o banco de testes em execução)
uv run pytest

# Verificar o lint e a formatação
uv run ruff check .
uv run ruff format --check .
```

Os testes aplicam as migrações no banco definido em `TEST_DATABASE_URL` e desfazem as alterações de cada teste ao final.
