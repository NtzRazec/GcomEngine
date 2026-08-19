import customtkinter as ctk

from app.theme import (
    CARD,
    TEXT,
    TEXT_SECONDARY,
    BORDER,
    SUCCESS
)
from app.toplevel import (
    GcomToplevel
)
from services.clipboard_service import (
    copiar_anydesk
)


class DetalhesTotem(GcomToplevel):

    def __init__(
        self,
        parent,
        totem
    ):
        super().__init__(
            parent
        )

        self.totem = totem

        self.title(
            "Detalhes da Loja"
        )
        self.geometry(
            "850x700"
        )

        self.transient(
            parent.winfo_toplevel()
        )
        self.grab_set()

        self.grid_columnconfigure(
            0,
            weight=1
        )
        self.grid_rowconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            self,
            text=self.totem.titulo,
            text_color=TEXT,
            font=("Segoe UI", 24, "bold")
        ).grid(
            row=0,
            column=0,
            padx=25,
            pady=20,
            sticky="w"
        )

        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        scroll.grid(
            row=1,
            column=0,
            padx=25,
            pady=(0, 25),
            sticky="nsew"
        )
        scroll.grid_columnconfigure(
            0,
            weight=1
        )

        linha = 0

        campos = {
            "Marca": self.totem.marca,
            "Tipo": self.totem.tipo,
            "Data": self.totem.data,
            "Empresa GCOM": self.totem.empresa_gcom,
            "CNPJ": self.totem.cnpj_formatado,
            "ETB": self.totem.etb,
            "Unidade": self.totem.unidade,
            "Status": self.totem.status,
            "Responsável": self.totem.responsavel,
            "Impressora": self.totem.impressora
        }

        for titulo, valor in campos.items():
            if not str(
                valor
            ).strip():
                continue

            card = ctk.CTkFrame(
                scroll,
                fg_color=CARD,
                border_width=1,
                border_color=BORDER
            )
            card.grid(
                row=linha,
                column=0,
                sticky="ew",
                pady=3
            )

            ctk.CTkLabel(
                card,
                text=f"{titulo}: {valor}",
                text_color=TEXT,
                anchor="w",
                justify="left"
            ).pack(
                fill="x",
                padx=15,
                pady=10
            )

            linha += 1

        for acesso in self.totem.acessos:
            card = ctk.CTkFrame(
                scroll,
                fg_color=CARD,
                border_width=1,
                border_color=BORDER
            )
            card.grid(
                row=linha,
                column=0,
                sticky="ew",
                pady=3
            )

            ctk.CTkLabel(
                card,
                text=(
                    f"{acesso.get('identificador', 'Totem')} | "
                    f"AnyDesk: {acesso.get('anydesk', '')} | "
                    f"Terminal: {acesso.get('terminal', '')}"
                ),
                text_color=SUCCESS
            ).pack(
                side="left",
                padx=15,
                pady=10
            )

            if acesso.get(
                "anydesk"
            ):
                ctk.CTkButton(
                    card,
                    text="Copiar AnyDesk",
                    width=110,
                    command=lambda valor=acesso.get(
                        "anydesk"
                    ): copiar_anydesk(
                        valor
                    )
                ).pack(
                    side="right",
                    padx=15,
                    pady=8
                )

            linha += 1
