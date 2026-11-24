# Backend

API REST do Filmstar. Os filmes, séries, gêneros, imagens e demais metadados são consultados no TMDb; o PostgreSQL guarda apenas contas e estado pessoal associado a IDs TMDb.

## Tecnologias

- Python 3.12+ com FastAPI
- SQLAlchemy 2 e Alembic
- PostgreSQL com psycopg 3
- HTTPX para integração assíncrona com o TMDb
- pwdlib com Argon2 e PyJWT
- uv, pytest e Ruff

## Configuração

Pré-requisitos: `uv` e PostgreSQL em execução. Para iniciar o banco local, consulte [infra/](../infra/README.md).

Na pasta `backend/`, copie `.env.example` para `.env` e configure:

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | Banco da aplicação. |
| `TEST_DATABASE_URL` | Banco isolado dos testes. |
| `CORS_ORIGENS` | Origens autorizadas do frontend. |
| `JWT_SEGREDO` | Segredo obrigatório para assinar tokens. |
| `JWT_EXPIRACAO_MINUTOS` | Validade do token (padrão: 60). |
| `TMDB_API_TOKEN` | Token de leitura do TMDb, necessário para buscas e detalhes. |
| `ADMIN_NOME`, `ADMIN_EMAIL`, `ADMIN_SENHA` | Dados opcionais do administrador inicial. |

Obtenha `TMDB_API_TOKEN` em [Configurações da API TMDb](https://www.themoviedb.org/settings/api). Mantenha-o apenas no backend; ele não é enviado ao frontend. O arquivo `.env` é ignorado pelo Git.

Gere `JWT_SEGREDO` com:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Banco de dados

Aplique as migrações a partir de `backend/`:

```bash
uv run alembic upgrade head
```

Opcionalmente, crie o administrador inicial após configurar `ADMIN_EMAIL` e `ADMIN_SENHA`:

```bash
uv run python -m app.db.seed
```

Esse comando cria somente o administrador; não carrega filmes nem metadados locais.

A migration `9d3c7a1b5e20` remove o catálogo local, gêneros e pôsteres. Ela também remove registros antigos de lista e avaliação que não possuíam `tmdb_id`; usuários, favoritos e registros pessoais TMDb são preservados. A reversão restaura tabelas locais vazias, pois os dados removidos não podem ser recuperados.

## Execução

```bash
uv sync
uv run fastapi dev app/main.py
```

A API fica em `http://localhost:8000`. Swagger: `http://localhost:8000/docs`.

## Endpoints

Todas as rotas usam o prefixo `/api/v1`.

| Método | Rota | Autenticação | Descrição |
| --- | --- | --- | --- |
| `GET` | `/saude` | — | Estado da API e do banco. |
| `POST` | `/auth/cadastro` | — | Cria uma conta comum. |
| `POST` | `/auth/login` | — | Autentica (`username` é o e-mail) e retorna JWT. |
| `GET`, `PATCH`, `DELETE` | `/usuarios/me` | Token | Consulta, altera ou remove a própria conta. |
| `GET` | `/filmes/buscar?query=Batman&page=1` | — | Pesquisa filmes no TMDb. |
| `GET` | `/filmes/populares?page=1` | — | Filmes populares. |
| `GET` | `/filmes/top-rated?page=1` | — | Filmes mais bem avaliados. |
| `GET` | `/filmes/now-playing?page=1` | — | Filmes em cartaz. |
| `GET` | `/filmes/upcoming?page=1` | — | Próximos lançamentos. |
| `GET` | `/filmes/discover` | — | Descoberta com filtros TMDb. |
| `GET` | `/filmes/generos` | — | Gêneros de filmes do TMDb. |
| `GET` | `/filmes/{tmdb_id}` | — | Detalhes, créditos e imagens de um filme. |
| `GET` | `/usuarios/me/filmes?status=assistido&pagina=1&tamanho=20` | Token | Estado pessoal agregado, paginado. O filtro `status` (opcional) aceita `quero_assistir`, `assistindo` ou `assistido` e é aplicado antes da paginação. |
| `GET` | `/usuarios/me/filmes/{tmdb_id}` | Token | Status, avaliação e favorito para um filme. |
| `PUT`, `DELETE` | `/usuarios/me/filmes/{tmdb_id}/lista` | Token | Define ou remove status pessoal. |
| `PUT`, `DELETE` | `/usuarios/me/filmes/{tmdb_id}/avaliacao` | Token | Salva ou remove nota pessoal e comentário. |
| `GET` | `/usuarios/me/favoritos` | Token | Lista IDs TMDb favoritados. |
| `GET` | `/usuarios/me/recomendacoes?estrategia=perfil&limite=10` | Token | Recomenda filmes com a estratégia escolhida (`perfil`, `similares` ou `populares`). |
| `POST`, `DELETE` | `/filmes/{tmdb_id}/favoritar` | Token | Adiciona ou remove favorito. |
| `DELETE` | `/avaliacoes/{id}` | Admin | Modera uma avaliação pessoal. |
| `GET` | `/filmes/{tmdb_id}/comentarios?pagina=1&tamanho=20` | — | Lista comentários públicos de um filme, mais recentes primeiro. |
| `GET` | `/filmes/{tmdb_id}/comentarios/meu` | Token | Obtém o comentário público próprio (se existir) nesse filme. |
| `POST` | `/filmes/{tmdb_id}/comentarios` | Token | Cria um comentário público no filme (1 a 2000 caracteres, nota opcional de 1 a 5). |
| `PATCH` | `/comentarios/{id}` | Token (autor) | Edita o conteúdo/nota de um comentário próprio. |
| `DELETE` | `/comentarios/{id}` | Token (autor) | Remove (exclusão lógica) um comentário próprio. |

Nas rotas autenticadas, envie `Authorization: Bearer <token>`. O endpoint `/filmes/discover` aceita gêneros, ano, intervalo de lançamento, nota, idioma, ordenação e página. Os resultados e imagens são obtidos do TMDb em tempo real; o token do provedor nunca é retornado pela API.

A lista, as avaliações e os favoritos guardam apenas o `tmdb_id` e os dados pessoais do usuário. A nota pessoal (1 a 5) é independente da nota pública do TMDb.

Filtros do RF4 (buscar e filtrar por gênero, ano e status): gênero e ano em `/filmes/discover` (tela de Busca) e status em `/usuarios/me/filmes?status=` (abas da Minha Lista).

Este produto usa a API TMDb, mas não é endossado nem certificado pelo TMDb.

## Recomendações (padrão Strategy)

O motor de recomendações fica em [app/recomendacoes/](app/recomendacoes/). Cada estratégia implementa a interface `EstrategiaRecomendacao` ([base.py](app/recomendacoes/base.py)). O `RecomendacaoService` ([recomendacao_service.py](app/services/recomendacao_service.py)) monta o contexto do usuário (notas e filmes a excluir) e escolhe a estratégia pelo parâmetro `estrategia`.

| Estratégia | Critério | Exemplo de motivo |
| --- | --- | --- |
| `perfil` (padrão) | Gêneros e países com maior afinidade nas avaliações do usuário. Cada avaliação vale `nota − 3`, e a nota do comentário público mais recente prevalece sobre a avaliação privada. | "Porque você gosta de Ação e Drama" |
| `similares` | Recomendações do TMDb para os 3 filmes mais bem avaliados (nota 4 ou 5). Filmes indicados por mais de uma base sobem na lista. | "Parecido com Interestelar" |
| `populares` | Filmes populares do TMDb. Não depende do histórico do usuário. | "Em alta no TMDb" |

Regras comuns:

- Filmes avaliados ou marcados como assistidos não são recomendados.
- Quando a estratégia escolhida não encontra filmes (por exemplo, para um usuário sem avaliações), a API usa `populares`. O campo `estrategia` da resposta informa a estratégia efetivamente usada.
- Cada item traz os dados do filme e o `motivo` da recomendação.
- O campo `tempo_ms` informa quanto tempo o cálculo levou.

Exemplo de resposta, com os campos do filme resumidos:

```json
{
  "estrategia": "similares",
  "itens": [
    {
      "tmdb_id": 75612,
      "titulo": "Oblivion",
      "nota_tmdb": 6.7,
      "motivo": "Parecido com Interestelar"
    }
  ],
  "total": 1,
  "tempo_ms": 145
}
```

Para criar uma estratégia, adicione o nome em `NomeEstrategia` ([enums.py](app/models/enums.py)), crie uma classe que herde de `EstrategiaRecomendacao` e registre-a no `RecomendacaoService`.

### Desempenho (RNF3: menos de 800 ms)

As recomendações dependem do TMDb, então o tempo de resposta vem principalmente das consultas externas. Para ficar abaixo de 800 ms:

- **Conexão reaproveitada:** a API cria um único cliente HTTP para o TMDb ao iniciar (`ciclo_de_vida` em [main.py](app/main.py)). As conexões HTTPS continuam abertas por até 60 s sem uso, em vez de uma conexão nova a cada consulta.
- **Consultas em paralelo:** a estratégia `perfil` busca ao mesmo tempo os detalhes de todos os filmes avaliados e, depois, as páginas de candidatos. O resultado é o mesmo da versão sequencial, inclusive na ordem.
- **Cache em memória** ([cache_tmdb.py](app/services/cache_tmdb.py)): detalhes de filmes ficam guardados por 24 horas, e listas e buscas por 30 minutos. Do elenco, o cache guarda só o que a API exibe, o que dá cerca de 25 KB por filme, até 1.000 respostas. Ele contém apenas dados públicos do catálogo e é perdido quando a API reinicia.

A tela inicial mostra o valor de `tempo_ms` abaixo das recomendações.

Medições com o TMDb real, para um usuário com 10 filmes avaliados:

| Estratégia | Antes | Primeira consulta | Consulta repetida (cache) |
| --- | --- | --- | --- |
| `perfil` | 4,5 a 6,6 s | 0,7 a 0,8 s (API recém-iniciada) | cerca de 5 ms |
| `similares` | 0,9 a 1,6 s | cerca de 150 ms | cerca de 5 ms |
| `populares` | 0,6 a 0,8 s | cerca de 150 ms | cerca de 5 ms |

A consulta mais lenta é a primeira depois que a API inicia, porque é quando as conexões com o TMDb são abertas. O teste `test_recomendacoes_levam_menos_de_800_ms_com_a_latencia_do_tmdb` simula 150 ms por consulta ao TMDb, que é a latência medida com a conexão já aberta, e verifica as três estratégias.

Em desenvolvimento, o React (StrictMode) faz cada requisição duas vezes. Por isso, a tela pode mostrar o tempo da segunda, que já encontra o cache preenchido.

## Testes e qualidade

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
