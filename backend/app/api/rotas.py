from fastapi import APIRouter

from app.api import (
    autenticacao,
    avaliacoes,
    filmes,
    saude,
    usuarios,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(saude.router)
api_router.include_router(autenticacao.router)
api_router.include_router(usuarios.router)
api_router.include_router(filmes.router)
api_router.include_router(avaliacoes.router)
