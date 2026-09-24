from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.sessao import obter_sessao

router = APIRouter(tags=["Saúde"])


@router.get("/saude", summary="Verifica se a API e o banco estão disponíveis")
def verificar_saude(sessao: Annotated[Session, Depends(obter_sessao)]) -> dict[str, str]:
    try:
        sessao.execute(text("SELECT 1"))
    except SQLAlchemyError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados indisponível",
        ) from erro
    return {"status": "ok"}
