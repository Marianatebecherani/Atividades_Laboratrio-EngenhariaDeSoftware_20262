# Catálogo Pessoal de Filmes e Séries

Projeto do Grupo 1 da disciplina Laboratório de Engenharia de Software (2026/2).

Aplicação para registrar filmes e séries assistidos, manter uma lista "Quero Assistir", avaliar obras com notas e comentários e receber recomendações personalizadas.

## Integrantes

- Igor Mateus de Andrade
- Mariana Rebelo Tebecherani
- Taylor Henrique Marinho Silva

## Stack

| Camada | Tecnologia |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy 2, Alembic, uv |
| Banco de dados | PostgreSQL |
| Frontend | React (Vite) |

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

Em construção. As instruções de instalação e execução serão adicionadas conforme os componentes forem implementados.
