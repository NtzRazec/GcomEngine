from enum import Enum

from services.browser_service import BrowserService


class StatusSessao(Enum):
    CONECTADO = "CONNECTED"
    EXPIRADA = "EXPIRED"
    NAO_ENCONTRADA = "NOT_FOUND"
    ERRO = "ERROR"


class SessionValidator:

    def validar(self):
        browser = BrowserService()

        try:
            if not browser.sessao_existe():
                return StatusSessao.NAO_ENCONTRADA

            pagina = browser.abrir_com_sessao()

            if pagina is None:
                return StatusSessao.ERRO

            if browser.acessar_pagina_protegida(
                pagina
            ):
                return StatusSessao.CONECTADO

            return StatusSessao.EXPIRADA

        except Exception:
            return StatusSessao.ERRO

        finally:
            browser.fechar()


def descricao_status(status):
    return {
        StatusSessao.CONECTADO:
            "Portal GCOM conectado.",

        StatusSessao.EXPIRADA:
            "Sessão do Portal GCOM expirada.",

        StatusSessao.NAO_ENCONTRADA:
            "Nenhuma sessão encontrada.",

        StatusSessao.ERRO:
            "Erro ao validar sessão."
    }.get(
        status,
        "Status desconhecido."
    )
