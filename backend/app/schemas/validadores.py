def texto_vazio_como_nulo(valor: object) -> object:
    """Remove espaços das pontas e converte texto vazio em nulo."""
    if isinstance(valor, str):
        return valor.strip() or None
    return valor
