"""Erros de regra de negócio, independentes de HTTP.

Os serviços lançam estes erros e a camada de API os converte em respostas HTTP
(ver `registrar_tratadores` em app/api/erros.py).
"""


class ErroDeNegocio(Exception):
    """Base dos erros de negócio. `mensagem` é exibida ao cliente."""

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class RecursoNaoEncontrado(ErroDeNegocio):
    pass


class ConflitoDeDados(ErroDeNegocio):
    pass


class CredenciaisInvalidas(ErroDeNegocio):
    pass


class OperacaoNaoPermitida(ErroDeNegocio):
    pass


class DadosInvalidos(ErroDeNegocio):
    pass


class ArquivoMuitoGrande(ErroDeNegocio):
    pass


class TipoDeArquivoNaoSuportado(ErroDeNegocio):
    pass
