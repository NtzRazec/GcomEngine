from datetime import datetime, timedelta


SERVICOS = {
    "INSTALACAO_VPN_TOTEM": {
        "nome": "Instalação VPN Totem",
        "duracao": 20,
        "peso": "LEVE"
    },
    "INSTALACAO_NOVO_SAT": {
        "nome": "Instalação novo S@T",
        "duracao": 30,
        "peso": "NORMAL"
    },
    "INSTALACAO_SMARTPOS": {
        "nome": "Instalação SmartPOS",
        "duracao": 30,
        "peso": "NORMAL"
    },
    "INSTALACAO_APP_GARCOM": {
        "nome": "Instalação App Garçom",
        "duracao": 30,
        "peso": "NORMAL"
    },
    "GCOMCLIENT_CAIXA": {
        "nome": "Instalação GcomClient - Caixa",
        "duracao": 20,
        "peso": "LEVE"
    },
    "GCOMCLIENT_TERMINAL": {
        "nome": (
            "Instalação GcomClient - "
            "Terminal/Chama Senha/Make"
        ),
        "duracao": 10,
        "peso": "LEVE"
    },
    "INSTALACAO_TEF": {
        "nome": "Instalação TEF - PDV",
        "duracao": 30,
        "peso": "NORMAL"
    },
    "REINSTALACAO_SERVIDOR": {
        "nome": "Reinstalação servidor",
        "duracao": 60,
        "peso": "PESADO"
    },
    "INSTALACAO_SERVIDOR": {
        "nome": "Instalação servidor",
        "duracao": 60,
        "peso": "PESADO"
    },
    "DESCIDA_BASE": {
        "nome": "Descida de base nova",
        "duracao": 30,
        "peso": "NORMAL"
    },
    "TROCA_CNPJ": {
        "nome": "Troca de CNPJ",
        "duracao": 30,
        "peso": "NORMAL"
    },
    "MAPA_MESA": {
        "nome": (
            "Habilitar o Mapa de Mesa - "
            "Parametros"
        ),
        "duracao": 30,
        "peso": "NORMAL"
    },
    "BACKUP_BANCO": {
        "nome": (
            "Realização do BKP do banco de dados"
        ),
        "duracao": 30,
        "peso": "NORMAL"
    },
    "REINSTALACAO_TEF": {
        "nome": "Reinstalação TEF - PDV",
        "duracao": 15,
        "peso": "LEVE"
    },
    "TROCA_ADQUIRENTE_TEF": {
        "nome": "Troca de adquirente TEF",
        "duracao": 10,
        "peso": "LEVE"
    },
    "LIMPEZA_BASE": {
        "nome": "Limpeza de base",
        "duracao": 30,
        "peso": "NORMAL"
    },
    "BASE_TREINAMENTO": {
        "nome": "Instalação base de treinamento",
        "duracao": 30,
        "peso": "NORMAL"
    }
}


def normalizar_texto(texto):
    return str(
        texto or ""
    ).strip().upper()


def identificar_servico(titulo):
    titulo_normalizado = normalizar_texto(
        titulo
    )

    verificacoes = [
        (
            "REINSTALACAO_SERVIDOR",
            [
                "REINSTALAÇÃO SERVIDOR",
                "REINSTALACAO SERVIDOR"
            ]
        ),
        (
            "INSTALACAO_SERVIDOR",
            [
                "INSTALAÇÃO SERVIDOR",
                "INSTALACAO SERVIDOR"
            ]
        ),
        (
            "REINSTALACAO_TEF",
            [
                "REINSTALAÇÃO TEF",
                "REINSTALACAO TEF"
            ]
        ),
        (
            "TROCA_ADQUIRENTE_TEF",
            [
                "TROCA DE ADQUIRENTE TEF"
            ]
        ),
        (
            "INSTALACAO_TEF",
            [
                "INSTALAÇÃO TEF",
                "INSTALACAO TEF"
            ]
        ),
        (
            "INSTALACAO_VPN_TOTEM",
            [
                "INSTALAÇÃO VPN TOTEM",
                "INSTALACAO VPN TOTEM"
            ]
        ),
        (
            "GCOMCLIENT_TERMINAL",
            [
                "GCOMCLIENT - TERMINAL",
                "CHAMA SENHA",
                "MAKE"
            ]
        ),
        (
            "GCOMCLIENT_CAIXA",
            [
                "GCOMCLIENT - CAIXA"
            ]
        ),
        (
            "TROCA_CNPJ",
            [
                "TROCA DE CNPJ"
            ]
        ),
        (
            "INSTALACAO_SMARTPOS",
            [
                "SMARTPOS"
            ]
        ),
        (
            "INSTALACAO_NOVO_SAT",
            [
                "NOVO S@T",
                "NOVO SAT"
            ]
        ),
        (
            "INSTALACAO_APP_GARCOM",
            [
                "APP GARÇOM",
                "APP GARCOM"
            ]
        ),
        (
            "DESCIDA_BASE",
            [
                "DESCIDA DE BASE"
            ]
        ),
        (
            "MAPA_MESA",
            [
                "MAPA DE MESA"
            ]
        ),
        (
            "BACKUP_BANCO",
            [
                "BKP DO BANCO",
                "BACKUP DO BANCO"
            ]
        ),
        (
            "LIMPEZA_BASE",
            [
                "LIMPEZA DE BASE"
            ]
        ),
        (
            "BASE_TREINAMENTO",
            [
                "BASE DE TREINAMENTO"
            ]
        )
    ]

    for codigo, palavras in verificacoes:
        for palavra in palavras:
            if palavra in titulo_normalizado:
                dados = SERVICOS[
                    codigo
                ].copy()

                dados[
                    "codigo"
                ] = codigo

                return dados

    return {
        "codigo": "OUTRO",
        "nome": "Outro serviço",
        "duracao": 30,
        "peso": "NORMAL"
    }


def esta_cancelado(status):
    return normalizar_texto(
        status
    ).startswith(
        "CANCELADO"
    )


def converter_datetime(valor):
    if not valor:
        return None

    for formato in (
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S"
    ):
        try:
            return datetime.strptime(
                str(valor).strip(),
                formato
            )
        except ValueError:
            pass

    return None


def existe_sobreposicao(
    inicio_evento,
    fim_evento,
    inicio_faixa,
    fim_faixa
):
    return (
        inicio_evento < fim_faixa
        and fim_evento > inicio_faixa
    )


def eventos_da_faixa(
    registros,
    data,
    horario
):
    inicio_faixa = datetime.combine(
        data,
        horario
    )

    fim_faixa = inicio_faixa + timedelta(
        hours=1
    )

    encontrados = []

    for registro in registros:
        if esta_cancelado(
            registro.get(
                "status",
                ""
            )
        ):
            continue

        inicio = converter_datetime(
            registro.get(
                "data_inicio"
            )
        )

        fim = converter_datetime(
            registro.get(
                "data_fim_previsto"
            )
        )

        if not inicio:
            continue

        if not fim:
            duracao = int(
                registro.get(
                    "duracao_minutos",
                    30
                ) or 30
            )

            fim = inicio + timedelta(
                minutes=duracao
            )

        if existe_sobreposicao(
            inicio,
            fim,
            inicio_faixa,
            fim_faixa
        ):
            encontrados.append(
                registro
            )

    return encontrados


def analisar_composicao(registros):
    servidores = 0
    tefs = 0
    leves = 0
    normais = 0
    pesados = 0
    possui_longo = False

    for registro in registros:
        servico = identificar_servico(
            registro.get(
                "titulo",
                ""
            )
        )

        codigo = servico[
            "codigo"
        ]

        duracao = int(
            registro.get(
                "duracao_minutos",
                servico["duracao"]
            ) or servico["duracao"]
        )

        if "SERVIDOR" in codigo:
            servidores += 1

        if "TEF" in codigo:
            tefs += 1

        if servico["peso"] == "LEVE":
            leves += 1
        elif servico["peso"] == "NORMAL":
            normais += 1
        elif servico["peso"] == "PESADO":
            pesados += 1

        if duracao > 30:
            possui_longo = True

    return {
        "quantidade": len(registros),
        "servidores": servidores,
        "tefs": tefs,
        "leves": leves,
        "normais": normais,
        "pesados": pesados,
        "possui_servico_longo": possui_longo
    }


def calcular_capacidade(
    registros,
    novo_servico=None
):
    analise = analisar_composicao(
        registros
    )

    servidores = analise[
        "servidores"
    ]

    tefs = analise[
        "tefs"
    ]

    possui_longo = analise[
        "possui_servico_longo"
    ]

    if novo_servico:
        codigo = novo_servico.get(
            "codigo",
            ""
        )

        if "SERVIDOR" in codigo:
            servidores += 1

        if "TEF" in codigo:
            tefs += 1

        if (
            novo_servico.get(
                "duracao",
                30
            )
            > 30
        ):
            possui_longo = True

    if servidores >= 2:
        return 3

    if (
        servidores == 1
        and tefs <= 2
    ):
        return 4

    if possui_longo:
        return 3

    return 4


def classificar_status(
    ocupados,
    capacidade
):
    vagas = capacidade - ocupados

    if vagas <= 0:
        return {
            "codigo": "LOTADO",
            "texto": "Lotado",
            "icone": "🔴"
        }

    if vagas == 1:
        return {
            "codigo": "POUCAS_VAGAS",
            "texto": "Poucas vagas",
            "icone": "🟡"
        }

    return {
        "codigo": "DISPONIVEL",
        "texto": "Disponível",
        "icone": "🟢"
    }


def analisar_horario(
    registros,
    data,
    horario,
    novo_servico=None
):
    eventos = eventos_da_faixa(
        registros,
        data,
        horario
    )

    capacidade = calcular_capacidade(
        eventos,
        novo_servico
    )

    ocupados = len(
        eventos
    )

    vagas = max(
        capacidade - ocupados,
        0
    )

    status = classificar_status(
        ocupados,
        capacidade
    )

    composicao = analisar_composicao(
        eventos
    )

    return {
        "data": data,
        "horario": horario,
        "ocupados": ocupados,
        "capacidade": capacidade,
        "vagas": vagas,
        "disponivel": vagas > 0,
        "status": status["codigo"],
        "status_texto": status["texto"],
        "icone": status["icone"],
        "servidores": composicao["servidores"],
        "tefs": composicao["tefs"],
        "leves": composicao["leves"],
        "normais": composicao["normais"],
        "pesados": composicao["pesados"],
        "eventos": eventos
    }
