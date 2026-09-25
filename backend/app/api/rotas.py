from fastapi import APIRouter

from app.api import (
    autenticacao,
    avaliacoes,
    generos,
    lista,
    obras,
    recomendacoes,
    saude,
    usuarios,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(saude.router)
api_router.include_router(autenticacao.router)
api_router.include_router(usuarios.router)
api_router.include_router(lista.router)
api_router.include_router(recomendacoes.router)
api_router.include_router(generos.router)
api_router.include_router(obras.router)
api_router.include_router(avaliacoes.router)
