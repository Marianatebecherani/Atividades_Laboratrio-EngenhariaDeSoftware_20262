# Catálogo Pessoal de Filmes e Séries

Projeto do Grupo 1 da disciplina Laboratório de Engenharia de Software (2026/2).

Aplicação para registrar filmes e séries assistidos, manter uma lista "Quero Assistir", avaliar obras com notas e comentários e receber recomendações personalizadas.

## 👥 <span id="authors">Autores</span>

<div align="center">
  <table>
    <tr>
      <th>Membro</th>
      <th>Github</th>
      <th>Linkedin</th>
    </tr>
    <tr>
      <td>Igor Mateus de Andrade</td>
      <td><a href="https://github.com/IgorAndrade2024/"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="www.linkedin.com/in/igor-andrade-b3b434327"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Mariana Tebecherani</td>
      <td><a href="https://github.com/Marianatebecherani/"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/mariana-tebecherani/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Taylor Henrique Marinho Silva</td>
      <td><a href="https://github.com/TaylorSilva2"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/taylor-silva-859300330/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
  </table>
</div>

### 📈 Backlog

| Rank | User Story | Prioridade | Sprint |
|---:|---|---|---|
| 1 | Como usuário, quero uma função de busca com filtros para selecionar mais facilmente os filmes. | Alta | Sprint 1 |
| 2 | Como usuário, quero uma página com filmes que já avaliei para consulta. | Alta |  Sprint 1 |
| 3 | Como usuário, quero poder avaliar filmes para informar outros usuários. | Média |  Sprint 1 |
| 4 | Como usuário, quero uma página do filme para saber mais informações. | Média | Sprint 1 |
| 5 | Como usuário, quero ver comentários de outros usuários para ter uma noção da qualidade do filme. | Média | Sprint 1 |
| 6 | Como usuário, quero uma lista de filmes a assistir para facilitar a organização. | Baixa | Sprint 1 |
| 7 | Como usuário, quero uma lista de filmes recomendados de acordo com meu gosto para facilitar conhecer novas obras. | Baixa | Sprint 2 |
| 8 | Como usuário, quero recomendações de filmes por gênero para conhecer novas obras. | Baixa | Sprint 2 |

## Stack

| Camada | Tecnologia |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy 2, Alembic, uv |
| Banco de dados | PostgreSQL |
| Frontend | React (Vite) |

<p align="center">
  <img
    src="./docs/Arquitetura%20star%20film.png"
    alt="Arquitetura do projeto Star Film"
    width="900"
  />
</p>

## Requisitos

### Funcionais

- RF1: registrar obras assistidas e lista de desejos ("Quero Assistir").
- RF2: atribuir notas (1 a 5 estrelas) e comentários às obras.
- RF3: gerar recomendações de filmes e séries com base no catálogo e nas preferências do usuário.
- RF4: buscar e filtrar obras por gênero, ano e status.

### Não funcionais

- RNF1: tabelas normalizadas em PostgreSQL, com chaves primárias e estrangeiras.
- RNF2: padrão Strategy no motor de recomendações e Repository no acesso a dados.
- RNF3: recomendações calculadas em menos de 800 ms.
- RNF4: interface React com componentes de avaliação e sugestões interativas.

## Estrutura

| Local | Responsabilidade |
| --- | --- |
| [backend/](backend/README.md) | API REST, regras de negócio e acesso a dados. |
| [frontend/](frontend/README.md) | Interface web em React. |



## Execução
# 🎬 Catálogo de Filmes — Manual de Instalação

Este documento apresenta o passo a passo para configurar e executar o projeto **Catálogo de Filmes** localmente.

A aplicação é composta por:

* **Frontend:** React + Vite
* **Backend:** FastAPI + Python
* **Banco de dados:** PostgreSQL 17
* **Banco de dados executado através de:** Docker
* **ORM:** SQLAlchemy
* **Migrações:** Alembic
* **API externa:** TMDb
* **Gerenciamento de dependências Python:** uv

---

# 1. Pré-requisitos

Antes de iniciar, certifique-se de que os seguintes programas estão instalados.

## 1.1 Git

Verifique:

```bash
git --version
```

Caso não esteja instalado no Ubuntu:

```bash
sudo apt update
sudo apt install git
```

---

## 1.2 Docker

Verifique:

```bash
docker --version
```

E:

```bash
docker compose version
```

O projeto utiliza Docker Compose para executar o PostgreSQL.

Caso o Docker não esteja instalado:

```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin
```

Depois, habilite o serviço:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Para permitir executar Docker sem `sudo`:

```bash
sudo usermod -aG docker $USER
```

Depois disso, encerre a sessão e entre novamente no sistema.

Teste:

```bash
docker ps
```

---

## 1.3 Node.js e npm

Verifique:

```bash
node --version
```

```bash
npm --version
```

O frontend utiliza Node.js e npm para instalar as dependências e executar o servidor de desenvolvimento.

---

## 1.4 Python

Verifique:

```bash
python3 --version
```

O backend utiliza Python.

> O projeto utiliza `uv` para gerenciar o ambiente virtual e as dependências Python.

---

## 1.5 uv

Verifique:

```bash
uv --version
```

Caso não esteja instalado:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Depois, reinicie o terminal ou carregue novamente as configurações do shell.

Teste:

```bash
uv --version
```

---

# 2. Clonar o projeto

Clone o repositório:

```bash
git clone https://github.com/Marianatebecherani/Atividades_Laboratrio-EngenhariaDeSoftware_20262.git
```

Entre no projeto:

```bash
cd Atividades_Laboratrio-EngenhariaDeSoftware_20262
```

Confira a estrutura:

```bash
ls
```

A estrutura principal deve ser semelhante a:

```text
Atividades_Laboratrio-EngenhariaDeSoftware_20262/
├── backend/
├── frontend/
├── infra/
├── README.md
└── ...
```

---

# 3. Configuração do PostgreSQL com Docker

O PostgreSQL utilizado pela aplicação é executado através do Docker.

Entre na raiz do projeto:

```bash
cd Atividades_Laboratrio-EngenhariaDeSoftware_20262
```

Inicie o banco:

```bash
docker compose -f infra/docker-compose.yml up -d --wait
```

Verifique o status:

```bash
docker compose -f infra/docker-compose.yml ps
```

O resultado esperado é semelhante a:

```text
NAME                IMAGE                COMMAND                  SERVICE
catalogo-postgres   postgres:17-alpine   "docker-entrypoint.s…"   postgres
```

O status deve aparecer como:

```text
Up ... (healthy)
```

E a porta deve aparecer como:

```text
0.0.0.0:5432->5432/tcp
```

Isso significa que o PostgreSQL está disponível em:

```text
localhost:5432
```

---

# 4. Atenção: PostgreSQL instalado diretamente no Ubuntu

O projeto utiliza o PostgreSQL através do Docker.

Caso exista uma instalação nativa do PostgreSQL no computador, ela pode estar utilizando a porta `5432`.

Verifique:

```bash
sudo lsof -i :5432
```

Se aparecer um processo `postgres` fora do Docker, pare o PostgreSQL nativo:

```bash
sudo systemctl stop postgresql
```

Depois inicie novamente o PostgreSQL do projeto:

```bash
docker compose -f infra/docker-compose.yml up -d --wait
```

Verifique:

```bash
docker compose -f infra/docker-compose.yml ps
```

A porta deve aparecer:

```text
0.0.0.0:5432->5432/tcp
```

---

# 5. Configuração do Backend

Entre no diretório do backend:

```bash
cd backend
```

## 5.1 Criar o arquivo `.env`

Crie:

```bash
touch .env
```

O arquivo deve conter as variáveis necessárias para o funcionamento da aplicação.

Exemplo:

```env
DATABASE_URL=postgresql+psycopg://catalogo:catalogo@localhost:5432/catalogo

CORS_ORIGENS=["http://localhost:5173"]

TEST_DATABASE_URL=postgresql+psycopg://catalogo:catalogo@localhost:5432/catalogo_test

ADMIN_NOME=Administrador
ADMIN_EMAIL=admin@catalogo.com
ADMIN_SENHA=troque-esta-senha

JWT_SEGREDO=troque-por-um-valor-aleatorio
JWT_EXPIRACAO_MINUTOS=60

TMDB_API_TOKEN=seu_token_de_leitura
```

### Importante

O arquivo `.env` contém informações sensíveis.

**Não envie o `.env` para o GitHub.**

Verifique se ele está no `.gitignore`.

---

# 6. Configuração do TMDb

A aplicação utiliza a API do **The Movie Database (TMDb)** para obter informações sobre filmes.

É necessário possuir um token da API do TMDb.

Depois de obter o token, configure:

```env
TMDB_API_TOKEN=SEU_TOKEN_AQUI
```

Não coloque o token diretamente no código-fonte.

Também não publique o token no GitHub.

Depois de alterar o `.env`, reinicie o backend.

---

# 7. Instalar as dependências do Backend

Dentro de:

```text
backend/
```

execute:

```bash
uv sync
```

O `uv` criará/atualizará o ambiente virtual e instalará as dependências necessárias.

---

# 8. Configurar o Banco de Dados

Com o PostgreSQL executando pelo Docker, ainda é necessário aplicar as migrações.

Dentro do diretório:

```text
backend/
```

execute:

```bash
uv run alembic upgrade head
```

Esse comando cria/atualiza as tabelas do banco de dados de acordo com as migrations existentes.

Sempre que novas migrations forem adicionadas ao projeto, execute novamente:

```bash
uv run alembic upgrade head
```

---

# 9. Executar o Backend

Ainda dentro de:

```text
backend/
```

execute:

```bash
uv run fastapi dev app/main.py
```

O backend ficará disponível em:

```text
http://localhost:8000
```

A documentação interativa do FastAPI pode ser acessada em:

```text
http://localhost:8000/docs
```

Também é possível acessar:

```text
http://127.0.0.1:8000/docs
```

Mantenha esse terminal aberto enquanto estiver utilizando a aplicação.

---

# 10. Configuração do Frontend

Abra **outro terminal**.

Entre no diretório do frontend:

```bash
cd ~/Área\ de\ trabalho/Atividades_Laboratrio-EngenhariaDeSoftware_20262/frontend
```

Ou, caso esteja na raiz do projeto:

```bash
cd frontend
```

Instale as dependências:

```bash
npm install
```

---

# 11. Executar o Frontend

Depois de instalar as dependências:

```bash
npm run dev
```

O Vite exibirá o endereço da aplicação, normalmente:

```text
http://localhost:5173
```

Abra esse endereço no navegador.

---

# 12. Executando o projeto completo

Para executar o sistema completo, serão necessários pelo menos **três processos**.

## Terminal 1 — PostgreSQL

Na raiz do projeto:

```bash
docker compose -f infra/docker-compose.yml up -d --wait
```

Verifique:

```bash
docker compose -f infra/docker-compose.yml ps
```

---

## Terminal 2 — Backend

```bash
cd backend
```

Execute as migrations:

```bash
uv run alembic upgrade head
```

Inicie o FastAPI:

```bash
uv run fastapi dev app/main.py
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## Terminal 3 — Frontend

```bash
cd frontend
```

Execute:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 13. Estrutura da aplicação

A estrutura geral do projeto é semelhante a:

```text
Atividades_Laboratrio-EngenhariaDeSoftware_20262/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── migrations/
│   │   └── versions/
│   │
│   ├── tests/
│   │
│   ├── .env
│   ├── pyproject.toml
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── infra/
│   ├── docker-compose.yml
│   └── postgres/
│       └── init/
│
└── README.md
```

---

# 14. Fluxo da aplicação

A arquitetura local funciona da seguinte forma:

```text
                  ┌──────────────────┐
                  │    Navegador     │
                  │  localhost:5173  │
                  └────────┬─────────┘
                           │
                           │ HTTP
                           ▼
                  ┌──────────────────┐
                  │    Frontend      │
                  │   React + Vite   │
                  └────────┬─────────┘
                           │
                           │ API
                           ▼
                  ┌──────────────────┐
                  │     FastAPI      │
                  │  localhost:8000  │
                  └────────┬─────────┘
                           │
                           │ SQL
                           ▼
              ┌─────────────────────────┐
              │       PostgreSQL        │
              │         Docker          │
              │      localhost:5432     │
              └─────────────────────────┘

                           │
                           │ HTTPS
                           ▼
                  ┌──────────────────┐
                  │       TMDb       │
                  │    API externa   │
                  └──────────────────┘
```

---

# 15. Comandos úteis do Docker

## Ver containers

```bash
docker ps
```

## Ver containers do projeto

```bash
docker compose -f infra/docker-compose.yml ps
```

## Iniciar o banco

```bash
docker compose -f infra/docker-compose.yml up -d
```

## Iniciar e aguardar o banco ficar saudável

```bash
docker compose -f infra/docker-compose.yml up -d --wait
```

## Parar o banco

```bash
docker compose -f infra/docker-compose.yml down
```

### Atenção

Evite utilizar:

```bash
docker compose down -v
```

Esse comando remove também o volume do PostgreSQL e pode apagar os dados armazenados localmente.

Utilize `down -v` somente quando realmente for necessário recriar o banco do zero.

---

# 16. Verificar se o PostgreSQL está funcionando

Verifique o container:

```bash
docker compose -f infra/docker-compose.yml ps
```

O status deve ser:

```text
healthy
```

Também é possível verificar diretamente:

```bash
docker exec catalogo-postgres pg_isready -U catalogo -d catalogo
```

O resultado esperado é semelhante a:

```text
/var/run/postgresql:5432 - accepting connections
```

---

# 17. Atualizar o projeto após alterações no GitHub

Caso outro integrante da equipe tenha enviado alterações para a branch utilizada:

```bash
git pull
```

Ou:

```bash
git pull origin nome-da-branch
```

Depois, caso tenham sido alteradas dependências do Python:

```bash
cd backend
uv sync
```

Caso tenham sido adicionadas novas migrations:

```bash
uv run alembic upgrade head
```

Caso tenham sido alteradas dependências do frontend:

```bash
cd ../frontend
npm install
```

Depois reinicie os servidores.

---

# 18. Problemas comuns

## Erro: `connection refused` em `localhost:5432`

Significa que o backend não conseguiu acessar o PostgreSQL.

Verifique:

```bash
docker compose -f infra/docker-compose.yml ps
```

O PostgreSQL deve estar:

```text
healthy
```

E deve possuir:

```text
0.0.0.0:5432->5432/tcp
```

Se necessário:

```bash
docker compose -f infra/docker-compose.yml up -d --wait
```

---

## Erro: `password authentication failed for user "catalogo"`

Pode existir um volume PostgreSQL criado anteriormente com outra senha.

Primeiro confirme se as credenciais do `.env` correspondem ao Docker Compose.

Se for uma instalação local de desenvolvimento e os dados puderem ser apagados, é possível recriar o banco:

```bash
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d --wait
```

Depois execute novamente:

```bash
cd backend
uv run alembic upgrade head
```

> **Atenção:** `down -v` remove os dados do banco armazenados no volume Docker.

---

## Erro: porta `5432` já está em uso

Verifique:

```bash
sudo lsof -i :5432
```

Se for uma instalação nativa do PostgreSQL:

```bash
sudo systemctl stop postgresql
```

Depois:

```bash
docker compose -f infra/docker-compose.yml up -d --wait
```

---

## Erro ao executar Alembic

Verifique primeiro se o PostgreSQL está funcionando:

```bash
docker compose -f infra/docker-compose.yml ps
```

Depois:

```bash
docker exec catalogo-postgres pg_isready -U catalogo -d catalogo
```

Se estiver funcionando, dentro do backend execute:

```bash
uv run alembic upgrade head
```

---

## TMDb informa erro de autenticação

Verifique se o token foi configurado corretamente no:

```text
backend/.env
```

Exemplo:

```env
TMDB_API_TOKEN=SEU_TOKEN_AQUI
```

Depois reinicie o FastAPI.

Não compartilhe o token publicamente.

---

## Frontend não consegue acessar o backend

Verifique se o backend está executando:

```text
http://localhost:8000
```

Teste o Swagger:

```text
http://localhost:8000/docs
```

Também verifique se o frontend está executando na porta:

```text
5173
```

O backend deve possuir a origem do frontend configurada no `.env`:

```env
CORS_ORIGENS=["http://localhost:5173"]
```

---

# 19. Testes do Backend

Os testes podem ser executados através do ambiente gerenciado pelo `uv`.

Dentro de:

```text
backend/
```

execute:

```bash
uv run pytest
```

Para obter mais detalhes:

```bash
uv run pytest -v
```

---

# 20. Qualidade do código

O projeto utiliza ferramentas de análise e formatação do código Python.

Para executar o Ruff:

```bash
uv run ruff check .
```

Para verificar problemas de formatação:

```bash
uv run ruff format --check .
```

---

# 21. Resumo — instalação rápida

Para quem já possui todos os pré-requisitos instalados:

### 1. Clonar

```bash
git clone https://github.com/Marianatebecherani/Atividades_Laboratrio-EngenhariaDeSoftware_20262.git
cd Atividades_Laboratrio-EngenhariaDeSoftware_20262
```

### 2. Banco

```bash
docker compose -f infra/docker-compose.yml up -d --wait
```

### 3. Backend

```bash
cd backend
uv sync
```

Configure o `.env` e depois:

```bash
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

### 4. Frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

### 5. Acessar

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 22. Ordem correta para iniciar o projeto

Sempre que for iniciar o projeto novamente:

```text
1. Docker/PostgreSQL
        ↓
2. Alembic
        ↓
3. FastAPI
        ↓
4. Frontend
```

Comandos:

```bash
# Terminal 1
docker compose -f infra/docker-compose.yml up -d --wait
```

```bash
# Terminal 2
cd backend
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

```bash
# Terminal 3
cd frontend
npm run dev
```

Com isso, o ambiente completo estará disponível localmente.

