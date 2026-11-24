from collections.abc import Hashable
from time import monotonic
from typing import Any


class CacheTmdb:
    """Guarda respostas do TMDb por um tempo, para não repetir consultas iguais.

    Só guarda dados públicos do catálogo, nunca dados de usuários. Fica na memória do
    processo da API: é perdido quando ela reinicia e não é compartilhado entre processos.
    Cada resposta ocupa cerca de 25 KB, então o limite padrão fica em torno de 25 MB.
    """

    def __init__(self, max_itens: int = 1000) -> None:
        self.max_itens = max_itens
        # Ordenado do item guardado há mais tempo para o mais recente.
        self._itens: dict[Hashable, tuple[float, dict[str, Any]]] = {}

    def __len__(self) -> int:
        return len(self._itens)

    def obter(self, chave: Hashable) -> dict[str, Any] | None:
        item = self._itens.get(chave)
        if item is None:
            return None

        expira_em, dados = item
        if monotonic() >= expira_em:
            del self._itens[chave]
            return None
        return dados

    def guardar(self, chave: Hashable, dados: dict[str, Any], validade_segundos: float) -> None:
        self._itens.pop(chave, None)
        self._itens[chave] = (monotonic() + validade_segundos, dados)

        if len(self._itens) > self.max_itens:
            self._liberar_espaco()

    def _liberar_espaco(self) -> None:
        agora = monotonic()
        for chave in [c for c, (expira_em, _) in self._itens.items() if expira_em <= agora]:
            del self._itens[chave]

        # Sem itens vencidos suficientes, descarta os guardados há mais tempo.
        while len(self._itens) > self.max_itens:
            del self._itens[next(iter(self._itens))]
