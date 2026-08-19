from services.browser_service import BrowserService
from services.logger_service import (
    erro,
    registrar_status_sessao
)


class GcomAuth:

    def __init__(self):
        self.browser = BrowserService()

    def realizar_login(
        self,
        timeout_segundos=300
    ):
        try:
            pagina = (
                self.browser
                .abrir_login()
            )

            pagina.wait_for_url(
                "**?Page=Home*",
                timeout=timeout_segundos * 1000
            )

            if not self.browser.salvar_sessao():
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Login realizado, mas não foi "
                        "possível salvar a sessão."
                    )
                }

            registrar_status_sessao(
                "CONNECTED"
            )

            return {
                "sucesso": True,
                "mensagem": "Portal GCOM conectado."
            }

        except Exception as exception:
            erro(
                f"Erro durante login: {exception}"
            )

            return {
                "sucesso": False,
                "mensagem": str(exception)
            }

    def fechar(self):
        self.browser.fechar()
