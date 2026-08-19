import customtkinter as ctk

from app.icon import aplicar_icone


class GcomToplevel(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        *args,
        **kwargs
    ):
        super().__init__(
            parent,
            *args,
            **kwargs
        )

        aplicar_icone(self)
