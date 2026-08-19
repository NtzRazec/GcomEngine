import json
import re
from datetime import datetime


COLUNAS_PRINCIPAIS = [
    "MARCA",
    "TIPO",
    "DATA",
    "EMPRESA GCOM",
    "CNPJ",
    "ETB",
    "UNIDADE"
]


def normalizar_texto(valor):
    return str(
        valor or ""
    ).strip()


def obter_valor(
    linha,
    nomes
):
    mapa = {
        str(chave)
        .strip()
        .upper(): chave
        for chave in linha.keys()
    }

    for nome in nomes:
        chave = mapa.get(
            nome.strip().upper()
        )

        if chave is not None:
            return normalizar_texto(
                linha.get(
                    chave,
                    ""
                )
            )

    return ""


def obter_detalhada(linha):
    for titulo, valor in linha.items():
        if (
            "DETALHADA"
            in str(titulo).upper()
        ):
            return normalizar_texto(
                valor
            )

    return ""


def extrair_acessos(
    detalhada
):
    acessos = []

    for linha in re.split(
        r"[\n\r]+",
        detalhada or ""
    ):
        if not linha.strip():
            continue

        id_match = re.search(
            r"\bVS\s*\d+\b",
            linha,
            flags=re.IGNORECASE
        )

        any_match = re.search(
            r"(?:ANYDESK|ANY)"
            r"\s*[:\-]?\s*"
            r"([\d\s]+)",
            linha,
            flags=re.IGNORECASE
        )

        terminal_match = re.search(
            r"(?:T|TERMINAL)"
            r"\s*[:\-]?\s*"
            r"(\d+)",
            linha,
            flags=re.IGNORECASE
        )

        acesso = {
            "identificador": (
                id_match.group(0)
                .replace(" ", "")
                .upper()
                if id_match
                else ""
            ),
            "anydesk": (
                "".join(
                    c
                    for c in any_match.group(1)
                    if c.isdigit()
                )
                if any_match
                else ""
            ),
            "terminal": (
                terminal_match.group(1)
                if terminal_match
                else ""
            )
        }

        if any(
            acesso.values()
        ):
            acessos.append(
                acesso
            )

    return acessos


def converter_linha(
    linha,
    nome_aba=""
):
    if not isinstance(
        linha,
        dict
    ):
        return None

    marca = obter_valor(
        linha,
        ["MARCA"]
    )
    tipo = obter_valor(
        linha,
        ["TIPO"]
    )
    data = obter_valor(
        linha,
        ["DATA"]
    )
    empresa_gcom = obter_valor(
        linha,
        ["EMPRESA GCOM"]
    )
    cnpj = "".join(
        c
        for c in obter_valor(
            linha,
            ["CNPJ"]
        )
        if c.isdigit()
    )
    etb = obter_valor(
        linha,
        ["ETB"]
    )
    unidade = obter_valor(
        linha,
        ["UNIDADE"]
    )
    status = obter_valor(
        linha,
        ["STATUS"]
    )
    responsavel = obter_valor(
        linha,
        [
            "RESPONSÁVEL",
            "RESPONSAVEL"
        ]
    )
    impressora = obter_valor(
        linha,
        ["IMPRESSORA"]
    )

    if not any(
        [
            marca,
            tipo,
            data,
            empresa_gcom,
            cnpj,
            etb,
            unidade
        ]
    ):
        return None

    dados_completos = {
        normalizar_texto(
            titulo
        ): normalizar_texto(
            valor
        )
        for titulo, valor
        in linha.items()
        if normalizar_texto(
            titulo
        )
    }

    acessos = extrair_acessos(
        obter_detalhada(
            linha
        )
    )

    return {
        "aba": nome_aba,
        "marca": marca,
        "tipo": tipo,
        "data": data,
        "empresa_gcom": empresa_gcom,
        "cnpj": cnpj,
        "etb": etb,
        "unidade": unidade,
        "status": status,
        "responsavel": responsavel,
        "quantidade": len(
            acessos
        ),
        "impressora": impressora,
        "dados_json": json.dumps(
            dados_completos,
            ensure_ascii=False
        ),
        "acessos": acessos,
        "atualizado_em": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )
    }


def processar_dados(
    linhas,
    nome_aba=""
):
    registros = []

    for linha in linhas:
        registro = converter_linha(
            linha,
            nome_aba
        )

        if registro:
            registros.append(
                registro
            )

    return registros


def validar_colunas(linhas):
    if not linhas:
        return (
            False,
            COLUNAS_PRINCIPAIS.copy()
        )

    titulos = {
        str(titulo)
        .strip()
        .upper()
        for titulo in linhas[0].keys()
    }

    faltando = [
        coluna
        for coluna in COLUNAS_PRINCIPAIS
        if coluna.upper()
        not in titulos
    ]

    return (
        len(faltando) == 0,
        faltando
    )
