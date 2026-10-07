from fastapi import APIRouter

from app.api import autenticacao, saude, usuarios

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(saude.router)
api_router.include_router(autenticacao.router)
api_router.include_router(usuarios.router)
