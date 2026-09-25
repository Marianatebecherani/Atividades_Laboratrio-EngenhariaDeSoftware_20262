from app.models import StatusLista
from app.repositories.obra_repository import ObraComResumo
from app.schemas.genero import GeneroResposta
from app.schemas.obra import ObraResposta


def obra_para_resposta(
    resultado: ObraComResumo, meu_status: StatusLista | None = None
) -> ObraResposta:
    obra = resultado.obra
    url_poster = None
    if obra.poster is not None:
        # O parâmetro de versão muda quando o pôster é trocado, invalidando o cache do navegador.
        versao = int(obra.poster.atualizado_em.timestamp())
        url_poster = f"/api/v1/obras/{obra.id}/poster?v={versao}"
    return ObraResposta(
        id=obra.id,
        titulo=obra.titulo,
        tipo=obra.tipo,
        ano_lancamento=obra.ano_lancamento,
        sinopse=obra.sinopse,
        classificacao_indicativa=obra.classificacao_indicativa,
        duracao_minutos=obra.duracao_minutos,
        temporadas=obra.temporadas,
        generos=[GeneroResposta.model_validate(genero) for genero in obra.generos],
        media_notas=resultado.media_notas,
        total_avaliacoes=resultado.total_avaliacoes,
        url_poster=url_poster,
        meu_status=meu_status,
    )
