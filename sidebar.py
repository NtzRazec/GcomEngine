import os

import customtkinter as ctk
from PIL import Image

from app.theme import (
    SIDEBAR,
    PRIMARY,
    PRIMARY_HOVER,
    TEXT,
    TEXT_SECONDARY,
    SUCCESS
)

from app.icon import obter_caminho_logo


class Sidebar(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        on_agendamento,
        on_totens
    ):
        super().__init__(
            parent,
            width=220,
            fg_color=SIDEBAR,
            corner_radius=0
        )

        self.grid_propagate(False)
        self.grid_rowconfigure(4, weight=1)

        caminho_logo = obter_caminho_logo()

        if os.path.exists(caminho_logo):
            imagem = Image.open(caminho_logo)

            self.logo_image = ctk.CTkImage(
                light_image=imagem,
                dark_image=imagem,
                size=(82, 82)
            )

            self.logo = ctk.CTkLabel(
                self,
                text="",
                image=self.logo_image
            )
        else:
            self.logo = ctk.CTkLabel(
                self,
                text="GCOM",
                text_color=TEXT,
                font=("Segoe UI", 22, "bold")
            )

        self.logo.grid(
            row=0,
            column=0,
            padx=20,
            pady=(22, 28)
        )

        self.btn_agendamento = ctk.CTkButton(
            self,
            text="Agendamento",
            anchor="w",
            fg_color="transparent",
            hover_color=PRIMARY_HOVER,
            command=on_agendamento
        )
        self.btn_agendamento.grid(
            row=1,
            column=0,
            padx=12,
            pady=6,
            sticky="ew"
        )

        self.btn_totens = ctk.CTkButton(
            self,
            text="Totens GCOM",
            anchor="w",
            fg_color="transparent",
            hover_color=PRIMARY_HOVER,
            command=on_totens
        )
        self.btn_totens.grid(
            row=2,
            column=0,
            padx=12,
            pady=6,
            sticky="ew"
        )

        self.status_portal = ctk.CTkLabel(
            self,
            text="Portal GCOM • Desconectado",
            text_color=TEXT_SECONDARY,
            font=("Segoe UI", 11)
        )
        self.status_portal.grid(
            row=5,
            column=0,
            padx=20,
            pady=20,
            sticky="w"
        )

    def selecionar_menu(self, menu):
        self.btn_agendamento.configure(
            fg_color=PRIMARY
            if menu == "agendamento"
            else "transparent"
        )

        self.btn_totens.configure(
            fg_color=PRIMARY
            if menu == "totens"
            else "transparent"
        )

    def atualizar_status_portal(self, conectado):
        if conectado:
            self.status_portal.configure(
                text="Portal GCOM • Conectado",
                text_color=SUCCESS
            )
        else:
            self.status_portal.configure(
                text="Portal GCOM • Desconectado",
                text_color=TEXT_SECONDARY
            )
