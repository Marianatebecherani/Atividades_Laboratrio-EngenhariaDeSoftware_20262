from pwdlib import PasswordHash

_hash_de_senha = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash da senha com Argon2."""
    return _hash_de_senha.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return _hash_de_senha.verify(senha, senha_hash)
