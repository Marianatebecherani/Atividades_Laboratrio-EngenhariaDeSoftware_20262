from fastapi import APIRouter

from app.api import autenticacao, generos, lista, obras, saude, usuarios

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(saude.router)
api_router.include_router(autenticacao.router)
api_router.include_router(usuarios.router)
api_router.include_router(lista.router)
api_router.include_router(generos.router)
api_router.include_router(obras.router)
