import customtkinter as ctk

from app.theme import (
    BACKGROUND,
    TEXT,
    TEXT_SECONDARY,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)

from app.icon import aplicar_icone
from app.sidebar import Sidebar
from agendamento.tela import TelaAgendamento
from totens.tela import TelaTotens
from services.sync_service import SyncService
from services.logger_service import info


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")

        self.title("GCOM Engine")
        aplicar_icone(self)

        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )
        self.minsize(1050, 650)
        self.configure(fg_color=BACKGROUND)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.tela_atual = None
        self.sync_service = SyncService()

        self._criar_interface()
        self._configurar_sync()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.fechar_sistema
        )

        self.abrir_agendamento()
        self.sync_service.iniciar()

    def _criar_interface(self):
        self.sidebar = Sidebar(
            self,
            self.abrir_agendamento,
            self.abrir_totens
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND,
            corner_radius=0
        )
        self.content_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.content_frame.grid_rowconfigure(
            1,
            weight=1
        )
        self.content_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.header = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.header.grid(
            row=0,
            column=0,
            padx=30,
            pady=(20, 10),
            sticky="ew"
        )
        self.header.grid_columnconfigure(
            0,
            weight=1
        )

        self.titulo_tela = ctk.CTkLabel(
            self.header,
            text="GCOM Engine",
            text_color=TEXT,
            font=("Segoe UI", 26, "bold")
        )
        self.titulo_tela.grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.subtitulo_tela = ctk.CTkLabel(
            self.header,
            text="",
            text_color=TEXT_SECONDARY,
            font=("Segoe UI", 12)
        )
        self.subtitulo_tela.grid(
            row=1,
            column=0,
            sticky="w"
        )

        self.status_sync = ctk.CTkLabel(
            self.header,
            text="",
            text_color=TEXT_SECONDARY,
            font=("Segoe UI", 11)
        )
        self.status_sync.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="e"
        )

        self.page_container = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.page_container.grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 30),
            sticky="nsew"
        )
        self.page_container.grid_rowconfigure(
            0,
            weight=1
        )
        self.page_container.grid_columnconfigure(
            0,
            weight=1
        )

    def _configurar_sync(self):
        self.sync_service.on_status = (
            lambda msg: self.after(
                0,
                lambda: self.status_sync.configure(
                    text=msg
                )
            )
        )

        self.sync_service.on_totens_atualizados = (
            lambda quantidade: self.after(
                0,
                lambda: self.status_sync.configure(
                    text=f"Totens atualizados: {quantidade}"
                )
            )
        )

        self.sync_service.on_erro = (
            lambda msg: self.after(
                0,
                lambda: self.status_sync.configure(
                    text=f"Erro: {msg}"
                )
            )
        )

    def limpar_tela(self):
        if self.tela_atual is not None:
            self.tela_atual.destroy()
            self.tela_atual = None

    def abrir_agendamento(self):
        self.limpar_tela()

        self.sidebar.selecionar_menu(
            "agendamento"
        )

        self.titulo_tela.configure(
            text="Agendamento"
        )

        self.subtitulo_tela.configure(
            text="Consulte a agenda e os horários disponíveis."
        )

        self.tela_atual = TelaAgendamento(
            self.page_container,
            on_status_portal=self.sidebar.atualizar_status_portal
        )

        self.tela_atual.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    def abrir_totens(self):
        self.limpar_tela()

        self.sidebar.selecionar_menu(
            "totens"
        )

        self.titulo_tela.configure(
            text="Totens GCOM"
        )

        self.subtitulo_tela.configure(
            text="Consulte lojas, ETB, CNPJ e acessos."
        )

        self.tela_atual = TelaTotens(
            self.page_container
        )

        self.tela_atual.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    def fechar_sistema(self):
        try:
            self.sync_service.parar()
        except Exception:
            pass

        info("Encerrando GCOM Engine.")
        self.destroy()
