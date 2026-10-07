from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import obter_configuracoes

_hash_de_senha = PasswordHash.recommended()

# Hash usado quando o e-mail não existe, para que o tempo de resposta do login
# não revele quais e-mails estão cadastrados.
_HASH_FICTICIO = _hash_de_senha.hash("senha-ficticia-para-comparacao")


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash da senha com Argon2."""
    return _hash_de_senha.hash(senha)


def verificar_senha(senha: str, senha_hash: str | None) -> bool:
    if senha_hash is None:
        _hash_de_senha.verify(senha, _HASH_FICTICIO)
        return False
    return _hash_de_senha.verify(senha, senha_hash)


def criar_token_acesso(usuario_id: int) -> str:
    configuracoes = obter_configuracoes()
    agora = datetime.now(UTC)
    payload = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=configuracoes.jwt_expiracao_minutos),
    }
    return jwt.encode(payload, configuracoes.jwt_segredo, algorithm=configuracoes.jwt_algoritmo)


def ler_usuario_do_token(token: str) -> int | None:
    """Retorna o id do usuário do token, ou None se o token for inválido ou expirado."""
    configuracoes = obter_configuracoes()
    try:
        payload = jwt.decode(
            token,
            configuracoes.jwt_segredo,
            algorithms=[configuracoes.jwt_algoritmo],
            options={"require": ["sub", "exp"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
