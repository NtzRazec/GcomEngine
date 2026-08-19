import threading

import customtkinter as ctk

from app.theme import (
    CARD,
    INPUT,
    PRIMARY,
    PRIMARY_HOVER,
    TEXT,
    TEXT_SECONDARY,
    BORDER,
    SUCCESS,
    DANGER,
    CORNER_RADIUS
)
from totens.pesquisa import (
    buscar_totens
)
from totens.detalhes import (
    DetalhesTotem
)
from services.google_auth_service import (
    conectar_google,
    desconectar_google,
    status_google
)
from services.sheets_service import (
    ler_registros
)
from config.config import obter_env
from totens.google_sheets import (
    validar_colunas,
    processar_dados
)
from database.totem_repository import (
    substituir_totens
)


class TelaTotens(ctk.CTkFrame):

    def __init__(
        self,
        parent
    ):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        self._conectando_google = False
        self._sincronizando = False

        self.grid_columnconfigure(
            0,
            weight=1
        )
        self.grid_rowconfigure(
            3,
            weight=1
        )

        self._criar_barra_google()
        self._criar_pesquisa()

        self.after(
            300,
            self.atualizar_status_google
        )

    def _criar_barra_google(self):
        self.google_card = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=BORDER
        )
        self.google_card.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 15)
        )
        self.google_card.grid_columnconfigure(
            1,
            weight=1
        )

        self.google_indicador = ctk.CTkLabel(
            self.google_card,
            text="●",
            text_color=TEXT_SECONDARY,
            font=("Segoe UI", 22, "bold")
        )
        self.google_indicador.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(20, 12),
            pady=16
        )

        self.google_titulo = ctk.CTkLabel(
            self.google_card,
            text="Google Sheets",
            text_color=TEXT,
            font=("Segoe UI", 14, "bold")
        )
        self.google_titulo.grid(
            row=0,
            column=1,
            sticky="sw",
            pady=(12, 0)
        )

        self.google_status = ctk.CTkLabel(
            self.google_card,
            text="Verificando conta Google...",
            text_color=TEXT_SECONDARY,
            font=("Segoe UI", 11)
        )
        self.google_status.grid(
            row=1,
            column=1,
            sticky="nw",
            pady=(2, 12)
        )

        self.btn_google = ctk.CTkButton(
            self.google_card,
            text="Conectar Google",
            width=140,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=self.conectar_google
        )
        self.btn_google.grid(
            row=0,
            column=2,
            rowspan=2,
            padx=(10, 10),
            pady=16
        )

        self.btn_sync = ctk.CTkButton(
            self.google_card,
            text="Atualizar Totens",
            width=130,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=self.sincronizar_totens
        )
        self.btn_sync.grid(
            row=0,
            column=3,
            rowspan=2,
            padx=(0, 20),
            pady=16
        )

    def _criar_pesquisa(self):
        pesquisa = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=CORNER_RADIUS
        )
        pesquisa.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 15)
        )
        pesquisa.grid_columnconfigure(
            0,
            weight=1
        )

        self.campo = ctk.CTkEntry(
            pesquisa,
            placeholder_text=(
                "Pesquisar por ETB, CNPJ, empresa, "
                "unidade, data, tipo ou marca..."
            ),
            height=45,
            fg_color=INPUT,
            border_color=BORDER
        )
        self.campo.grid(
            row=0,
            column=0,
            padx=(20, 10),
            pady=20,
            sticky="ew"
        )
        self.campo.bind(
            "<Return>",
            lambda event: self.pesquisar()
        )

        ctk.CTkButton(
            pesquisa,
            text="Pesquisar",
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=self.pesquisar
        ).grid(
            row=0,
            column=1,
            padx=(0, 20),
            pady=20
        )

        self.status = ctk.CTkLabel(
            self,
            text="Digite um termo para pesquisar.",
            text_color=TEXT_SECONDARY
        )
        self.status.grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 10)
        )

        self.resultados = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.resultados.grid(
            row=3,
            column=0,
            sticky="nsew"
        )
        self.resultados.grid_columnconfigure(
            0,
            weight=1
        )

    def atualizar_status_google(self):
        estado = status_google()

        if estado["conectado"]:
            self.google_indicador.configure(
                text_color=SUCCESS
            )
            self.google_status.configure(
                text="Conta Google conectada."
            )
            self.btn_google.configure(
                text="Desconectar",
                command=self.desconectar_google
            )
        else:
            self.google_indicador.configure(
                text_color=DANGER
            )
            self.google_status.configure(
                text=estado["mensagem"]
            )
            self.btn_google.configure(
                text="Conectar Google",
                command=self.conectar_google
            )

    def conectar_google(self):
        if self._conectando_google:
            return

        self._conectando_google = True
        self.btn_google.configure(
            state="disabled",
            text="Aguardando login..."
        )
        self.google_status.configure(
            text=(
                "Faça login no navegador "
                "com a conta que possui acesso à planilha."
            )
        )

        threading.Thread(
            target=self._conectar_thread,
            daemon=True
        ).start()

    def _conectar_thread(self):
        try:
            conectar_google()
            resultado = {
                "sucesso": True,
                "mensagem": "Conta Google conectada."
            }
        except Exception as exception:
            resultado = {
                "sucesso": False,
                "mensagem": str(exception)
            }

        self.after(
            0,
            lambda: self._finalizar_conexao(
                resultado
            )
        )

    def _finalizar_conexao(
        self,
        resultado
    ):
        self._conectando_google = False

        if resultado["sucesso"]:
            self.google_status.configure(
                text="Conta Google conectada."
            )
            self.atualizar_status_google()
            self.sincronizar_totens()
        else:
            self.btn_google.configure(
                state="normal",
                text="Conectar Google"
            )
            self.google_status.configure(
                text=(
                    "Falha no login: "
                    + resultado["mensagem"]
                )
            )

    def desconectar_google(self):
        desconectar_google()
        self.atualizar_status_google()

    def sincronizar_totens(self):
        if self._sincronizando:
            return

        estado = status_google()

        if not estado["conectado"]:
            self.google_status.configure(
                text=(
                    "Conecte sua conta Google antes "
                    "de atualizar os Totens."
                )
            )
            return

        self._sincronizando = True

        self.btn_sync.configure(
            state="disabled",
            text="Atualizando..."
        )
        self.status.configure(
            text="Atualizando Totens GCOM..."
        )

        threading.Thread(
            target=self._sincronizar_thread,
            daemon=True
        ).start()

    def _sincronizar_thread(self):
        try:
            aba = obter_env(
                "GOOGLE_SHEET_TOTENS_ABA",
                ""
            )

            linhas = ler_registros(
                aba or None,
                solicitar_login=False
            )

            valido, faltando = validar_colunas(
                linhas
            )

            if not valido:
                raise ValueError(
                    "Colunas não encontradas: "
                    + ", ".join(faltando)
                )

            dados = processar_dados(
                linhas,
                aba or ""
            )

            substituir_totens(
                dados
            )

            resultado = {
                "sucesso": True,
                "quantidade": len(dados)
            }

        except Exception as exception:
            resultado = {
                "sucesso": False,
                "mensagem": str(exception)
            }

        self.after(
            0,
            lambda: self._finalizar_sync(
                resultado
            )
        )

    def _finalizar_sync(
        self,
        resultado
    ):
        self._sincronizando = False

        self.btn_sync.configure(
            state="normal",
            text="Atualizar Totens"
        )

        if resultado["sucesso"]:
            self.status.configure(
                text=(
                    f"Totens atualizados: "
                    f"{resultado['quantidade']}"
                )
            )
        else:
            self.status.configure(
                text=(
                    "Erro ao atualizar Totens: "
                    + resultado["mensagem"]
                )
            )

    def pesquisar(self):
        for widget in (
            self.resultados
            .winfo_children()
        ):
            widget.destroy()

        dados = buscar_totens(
            self.campo.get()
        )

        self.status.configure(
            text=f"{len(dados)} resultado(s)."
        )

        for indice, totem in enumerate(
            dados
        ):
            card = ctk.CTkFrame(
                self.resultados,
                fg_color=CARD,
                border_width=1,
                border_color=BORDER,
                corner_radius=CORNER_RADIUS,
                cursor="hand2"
            )
            card.grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=5
            )
            card.grid_columnconfigure(
                0,
                weight=1
            )

            titulo = ctk.CTkLabel(
                card,
                text=totem.titulo,
                text_color=TEXT,
                font=("Segoe UI", 16, "bold"),
                cursor="hand2"
            )
            titulo.grid(
                row=0,
                column=0,
                padx=20,
                pady=(15, 5),
                sticky="w"
            )

            info = ctk.CTkLabel(
                card,
                text=(
                    f"ETB: {totem.etb or '-'}   "
                    f"CNPJ: {totem.cnpj_formatado or '-'}   "
                    f"Empresa: {totem.empresa_gcom or '-'}"
                ),
                text_color=TEXT_SECONDARY,
                cursor="hand2"
            )
            info.grid(
                row=1,
                column=0,
                padx=20,
                pady=(0, 15),
                sticky="w"
            )

            ctk.CTkButton(
                card,
                text="Ver detalhes",
                width=110,
                command=lambda valor=totem: (
                    DetalhesTotem(
                        self,
                        valor
                    )
                )
            ).grid(
                row=0,
                column=1,
                rowspan=2,
                padx=20
            )

            for widget in (
                card,
                titulo,
                info
            ):
                widget.bind(
                    "<Button-1>",
                    lambda event, valor=totem: (
                        DetalhesTotem(
                            self,
                            valor
                        )
                    )
                )
