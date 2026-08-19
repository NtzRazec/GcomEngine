from datetime import datetime

from config.config import obter_regra


def agendamento_ocupa_vaga(status):
    return not str(
        status or ""
    ).strip().upper().startswith(
        "CANCELADO"
    )


def calcular_duracao_minutos(
    inicio,
    fim
):
    formatos = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S"
    ]

    data_inicio = None
    data_fim = None

    for formato in formatos:
        try:
            data_inicio = datetime.strptime(
                str(inicio).strip(),
                formato
            )
            break
        except Exception:
            pass

    for formato in formatos:
        try:
            data_fim = datetime.strptime(
                str(fim).strip(),
                formato
            )
            break
        except Exception:
            pass

    if not data_inicio or not data_fim:
        return 0

    return max(
        int(
            (
                data_fim - data_inicio
            ).total_seconds()
            / 60
        ),
        0
    )


def capacidade_por_duracao(
    duracao
):
    if duracao > 30:
        return obter_regra(
            "capacidade",
            "acima_30_minutos",
            3
        )

    return obter_regra(
        "capacidade",
        "ate_30_minutos",
        4
    )


def analisar_agendamento_existente(
    dados
):
    duracao = calcular_duracao_minutos(
        dados.get(
            "data_inicio",
            ""
        ),
        dados.get(
            "data_fim_previsto",
            ""
        )
    )

    return {
        **dados,
        "duracao_minutos": duracao,
        "ocupa_vaga": agendamento_ocupa_vaga(
            dados.get(
                "status",
                ""
            )
        ),
        "capacidade": capacidade_por_duracao(
            duracao
        )
    }
