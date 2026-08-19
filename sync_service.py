import threading
import time

from config.config import (
    obter_configuracao,
    obter_env
)
from services.sheets_service import (
    ler_registros
)
from services.google_auth_service import (
    obter_credenciais
)
from totens.google_sheets import (
    validar_colunas,
    processar_dados
)
from database.totem_repository import (
    substituir_totens
)


class SyncService:

    def __init__(self):
        self._executando = False
        self._thread = None
        self._lock = threading.Lock()

        self.intervalo_totens = obter_configuracao(
            "sincronizacao",
            "totens_segundos",
            600
        )

        self.ultima_sync_totens = 0

        self.on_totens_atualizados = None
        self.on_erro = None
        self.on_status = None

    def iniciar(self):
        if self._executando:
            return

        self._executando = True

        self._thread = threading.Thread(
            target=self._loop,
            daemon=True
        )

        self._thread.start()

    def parar(self):
        self._executando = False

    def _loop(self):
        while self._executando:
            agora = time.time()

            credenciais = obter_credenciais(
                solicitar_login=False
            )

            if (
                credenciais
                and agora - self.ultima_sync_totens
                >= self.intervalo_totens
            ):
                self.sincronizar_totens()

            time.sleep(1)

    def sincronizar_totens(
        self,
        solicitar_login=False
    ):
        if not self._lock.acquire(
            blocking=False
        ):
            return

        try:
            self._status(
                "Atualizando Totens GCOM..."
            )

            aba = obter_env(
                "GOOGLE_SHEET_TOTENS_ABA",
                ""
            )

            linhas = ler_registros(
                aba or None,
                solicitar_login=solicitar_login
            )

            valido, faltando = validar_colunas(
                linhas
            )

            if not valido:
                raise ValueError(
                    "Colunas não encontradas: "
                    + ", ".join(
                        faltando
                    )
                )

            dados = processar_dados(
                linhas,
                aba or ""
            )

            substituir_totens(
                dados
            )

            self.ultima_sync_totens = (
                time.time()
            )

            self._status(
                f"Totens GCOM atualizados: "
                f"{len(dados)}"
            )

            if self.on_totens_atualizados:
                self.on_totens_atualizados(
                    len(dados)
                )

        except Exception as exception:
            self.ultima_sync_totens = (
                time.time()
            )

            self._erro(
                f"Erro ao sincronizar Totens: "
                f"{exception}"
            )

        finally:
            self._lock.release()

    def _status(
        self,
        mensagem
    ):
        print(
            f"[SYNC] {mensagem}"
        )

        if self.on_status:
            self.on_status(
                mensagem
            )

    def _erro(
        self,
        mensagem
    ):
        print(
            f"[ERRO] {mensagem}"
        )

        if self.on_erro:
            self.on_erro(
                mensagem
            )
