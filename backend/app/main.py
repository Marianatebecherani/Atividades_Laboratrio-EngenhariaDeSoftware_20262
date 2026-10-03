from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.erros import registrar_tratadores
from app.api.rotas import api_router
from app.core.config import obter_configuracoes

configuracoes = obter_configuracoes()

app = FastAPI(title=configuracoes.nome_app, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.cors_origens,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_tratadores(app)
app.include_router(api_router)
