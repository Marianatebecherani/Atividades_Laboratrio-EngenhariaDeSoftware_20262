# Infra

Configurações para executar os serviços da aplicação em ambiente local.

## Pré-requisitos

- Docker com Docker Compose v2.

## Serviços

| Serviço | Imagem | Porta padrão | Descrição |
| --- | --- | --- | --- |
| `postgres` | `postgres:17-alpine` | 5432 | Banco da aplicação (`catalogo`) e banco de testes (`catalogo_test`). |

O banco de testes é criado pelo script em [postgres/init/](postgres/init/), executado apenas na primeira inicialização do volume.

## Configuração

Os valores padrão (usuário, senha, banco e porta) estão no [docker-compose.yml](docker-compose.yml). Para alterá-los, copie o arquivo de exemplo e edite o `.env`, que não é versionado:

```bash
cp infra/.env.example infra/.env
```

Se a porta 5432 já estiver em uso na sua máquina, defina outra em `POSTGRES_PORT` e ajuste a URL de conexão do backend.

## Comandos

Execute a partir da raiz do repositório:

```bash
# Iniciar o banco e aguardar até ficar saudável
docker compose -f infra/docker-compose.yml up -d --wait

# Ver o estado e os logs
docker compose -f infra/docker-compose.yml ps
docker compose -f infra/docker-compose.yml logs -f postgres

# Parar o banco, preservando os dados
docker compose -f infra/docker-compose.yml down
```

Para apagar todos os dados e recriar os bancos do zero, remova também o volume. **Essa operação descarta os dados de forma irreversível.**

```bash
docker compose -f infra/docker-compose.yml down -v
```
