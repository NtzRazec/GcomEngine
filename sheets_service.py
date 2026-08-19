import gspread

from config.config import obter_env
from services.google_auth_service import (
    obter_credenciais
)
from totens.google_sheets import (
    validar_colunas
)


def criar_cliente(
    solicitar_login=False
):
    credenciais = obter_credenciais(
        solicitar_login=solicitar_login
    )

    if credenciais is None:
        raise PermissionError(
            "Conta Google não conectada."
        )

    return gspread.authorize(
        credenciais
    )


def abrir_planilha(
    solicitar_login=False
):
    sheet_id = obter_env(
        "GOOGLE_SHEET_ID"
    )

    if not sheet_id:
        raise ValueError(
            "GOOGLE_SHEET_ID não definido no .env"
        )

    return (
        criar_cliente(
            solicitar_login=solicitar_login
        )
        .open_by_key(
            sheet_id
        )
    )


def detectar_aba_totens(
    planilha
):
    for aba in planilha.worksheets():
        linhas = aba.get_all_records()

        valido, _ = validar_colunas(
            linhas
        )

        if valido:
            return aba

    raise ValueError(
        "Nenhuma aba compatível com os Totens foi encontrada."
    )


def obter_aba(
    nome_aba=None,
    solicitar_login=False
):
    planilha = abrir_planilha(
        solicitar_login=solicitar_login
    )

    nome_aba = (
        nome_aba
        or obter_env(
            "GOOGLE_SHEET_TOTENS_ABA",
            ""
        )
    ).strip()

    if nome_aba:
        return planilha.worksheet(
            nome_aba
        )

    return detectar_aba_totens(
        planilha
    )


def ler_registros(
    nome_aba=None,
    solicitar_login=False
):
    return obter_aba(
        nome_aba,
        solicitar_login=solicitar_login
    ).get_all_records()
