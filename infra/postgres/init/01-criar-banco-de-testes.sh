#!/bin/sh
# Cria o banco usado pelos testes automatizados do backend.
# Executado apenas na primeira inicialização do volume.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
	CREATE DATABASE ${POSTGRES_DB}_test OWNER "$POSTGRES_USER";
SQL
