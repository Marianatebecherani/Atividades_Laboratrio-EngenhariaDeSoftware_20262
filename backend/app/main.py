from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.erros import registrar_tratadores
from app.api.rotas import api_router
from app.core.config import obter_configuracoes
from app.services.tmdb_service import criar_cliente_tmdb

configuracoes = obter_configuracoes()


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
    # Um único cliente HTTP para o TMDb: as conexões HTTPS ficam abertas e são
    # reaproveitadas entre as requisições, em vez de abrir uma nova a cada consulta.
    async with criar_cliente_tmdb() as cliente_tmdb:
        app.state.cliente_tmdb = cliente_tmdb
        yield


app = FastAPI(title=configuracoes.nome_app, version="0.1.0", lifespan=ciclo_de_vida)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.cors_origens,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_tratadores(app)
app.include_router(api_router)
