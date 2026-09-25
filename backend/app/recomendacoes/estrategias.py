"""Estratégias concretas de recomendação (padrão Strategy)."""

from collections import defaultdict

from app.recomendacoes.base import (
    ContextoRecomendacao,
    EstrategiaRecomendacao,
    NomeEstrategia,
    Recomendacao,
)

NOTA_NEUTRA = 3
PESO_ASSISTIDA_SEM_NOTA = 1.0
NOTA_MINIMA_REFERENCIA = 4
MAXIMO_OBRAS_REFERENCIA = 5
MAXIMO_GENEROS_NO_MOTIVO = 2


class RecomendacaoPorGeneros(EstrategiaRecomendacao):
    """Recomenda obras dos gêneros de que o usuário mais gosta.

    Cada avaliação soma `nota - 3` aos gêneros da obra (notas baixas afastam o gênero)
    e cada obra assistida ou em andamento, ainda sem nota, soma 1.
    """

    nome = NomeEstrategia.GENEROS

    def recomendar(self, contexto: ContextoRecomendacao) -> list[Recomendacao]:
        pesos = self._pesos_dos_generos(contexto.usuario_id)
        positivos = {genero: peso for genero, peso in pesos.items() if peso > 0}
        if not positivos:
            return []

        candidatos = self.repositorio.afinidade_por_generos(
            positivos, set(contexto.obras_excluidas), contexto.limite
        )
        generos_das_obras = self.repositorio.generos_das_obras(o for o, _ in candidatos)
        nomes = self.repositorio.nomes_dos_generos(positivos)
        total = sum(positivos.values())

        return [
            Recomendacao(
                obra_id=obra_id,
                pontuacao=round(afinidade / total, 2),
                motivo=self._motivo(generos_das_obras.get(obra_id, set()), positivos, nomes),
            )
            for obra_id, afinidade in candidatos
        ]

    def _pesos_dos_generos(self, usuario_id: int) -> dict[int, float]:
        notas = self.repositorio.notas_do_usuario(usuario_id)
        assistidas_sem_nota = self.repositorio.obras_assistidas(usuario_id) - notas.keys()
        pesos_das_obras = {obra: float(nota - NOTA_NEUTRA) for obra, nota in notas.items()}
        pesos_das_obras |= {obra: PESO_ASSISTIDA_SEM_NOTA for obra in assistidas_sem_nota}

        pesos: dict[int, float] = defaultdict(float)
        generos = self.repositorio.generos_das_obras(pesos_das_obras)
        for obra_id, peso in pesos_das_obras.items():
            for genero_id in generos.get(obra_id, ()):
                pesos[genero_id] += peso
        return pesos

    @staticmethod
    def _motivo(generos_da_obra: set[int], pesos: dict[int, float], nomes: dict[int, str]) -> str:
        preferidos = sorted(
            (g for g in generos_da_obra if g in pesos), key=lambda g: (-pesos[g], nomes[g])
        )[:MAXIMO_GENEROS_NO_MOTIVO]
        return "Porque você gosta de " + " e ".join(nomes[g] for g in preferidos)


class RecomendacaoPorSimilaridade(EstrategiaRecomendacao):
    """Recomenda obras parecidas com as que o usuário avaliou com nota 4 ou 5.

    A semelhança entre duas obras é a proporção de gêneros em comum (índice de Jaccard),
    somada sobre as obras de referência do usuário.
    """

    nome = NomeEstrategia.SIMILARES

    def recomendar(self, contexto: ContextoRecomendacao) -> list[Recomendacao]:
        notas = self.repositorio.notas_do_usuario(contexto.usuario_id)
        referencias = sorted(
            (obra for obra, nota in notas.items() if nota >= NOTA_MINIMA_REFERENCIA),
            key=lambda obra: -notas[obra],
        )[:MAXIMO_OBRAS_REFERENCIA]
        if not referencias:
            return []

        generos = self.repositorio.generos_das_obras()
        pontuacoes: dict[int, float] = {}
        mais_parecida: dict[int, tuple[float, int]] = {}
        for obra_id, generos_da_obra in generos.items():
            if obra_id in contexto.obras_excluidas:
                continue
            for referencia in referencias:
                semelhanca = self._jaccard(generos_da_obra, generos.get(referencia, set()))
                if semelhanca == 0:
                    continue
                pontuacoes[obra_id] = pontuacoes.get(obra_id, 0.0) + semelhanca
                if semelhanca > mais_parecida.get(obra_id, (0.0, 0))[0]:
                    mais_parecida[obra_id] = (semelhanca, referencia)

        medias = self.repositorio.medias(pontuacoes)
        melhores = sorted(pontuacoes, key=lambda o: (-pontuacoes[o], -medias.get(o, 0.0), o))[
            : contexto.limite
        ]
        titulos = self.repositorio.titulos(mais_parecida[o][1] for o in melhores)
        return [
            Recomendacao(
                obra_id=obra_id,
                pontuacao=round(pontuacoes[obra_id] / len(referencias), 2),
                motivo=f"Parecido com {titulos[mais_parecida[obra_id][1]]}",
            )
            for obra_id in melhores
        ]

    @staticmethod
    def _jaccard(a: set[int], b: set[int]) -> float:
        uniao = a | b
        return len(a & b) / len(uniao) if uniao else 0.0


class RecomendacaoPorPopularidade(EstrategiaRecomendacao):
    """Recomenda as obras mais bem avaliadas do catálogo. Não depende do histórico."""

    nome = NomeEstrategia.POPULARES

    def recomendar(self, contexto: ContextoRecomendacao) -> list[Recomendacao]:
        obras = self.repositorio.mais_bem_avaliadas(set(contexto.obras_excluidas), contexto.limite)
        return [
            Recomendacao(
                obra_id=obra_id,
                pontuacao=round(media / 5, 2) if media is not None else 0.0,
                motivo=(
                    f"Bem avaliado pela comunidade (média {media:.1f} em {total} avaliações)"
                    if media is not None
                    else "Destaque do catálogo"
                ),
            )
            for obra_id, media, total in obras
        ]


ESTRATEGIAS: dict[NomeEstrategia, type[EstrategiaRecomendacao]] = {
    estrategia.nome: estrategia
    for estrategia in (
        RecomendacaoPorGeneros,
        RecomendacaoPorSimilaridade,
        RecomendacaoPorPopularidade,
    )
}
