import json
from dataclasses import (
    dataclass,
    field
)


@dataclass
class Totem:
    id: int = 0
    aba: str = ""
    marca: str = ""
    tipo: str = ""
    data: str = ""
    empresa_gcom: str = ""
    cnpj: str = ""
    etb: str = ""
    unidade: str = ""
    status: str = ""
    responsavel: str = ""
    quantidade: int = 0
    impressora: str = ""
    atualizado_em: str = ""
    acessos: list = field(
        default_factory=list
    )
    dados_extras: dict = field(
        default_factory=dict
    )

    @classmethod
    def de_dict(
        cls,
        dados
    ):
        try:
            extras = json.loads(
                dados.get(
                    "dados_json",
                    "{}"
                ) or "{}"
            )
        except Exception:
            extras = {}

        return cls(
            id=dados.get("id", 0),
            aba=dados.get("aba", ""),
            marca=dados.get("marca", ""),
            tipo=dados.get("tipo", ""),
            data=dados.get("data", ""),
            empresa_gcom=dados.get("empresa_gcom", ""),
            cnpj=dados.get("cnpj", ""),
            etb=dados.get("etb", ""),
            unidade=dados.get("unidade", ""),
            status=dados.get("status", ""),
            responsavel=dados.get("responsavel", ""),
            quantidade=int(
                dados.get(
                    "quantidade",
                    0
                ) or 0
            ),
            impressora=dados.get("impressora", ""),
            atualizado_em=dados.get("atualizado_em", ""),
            acessos=dados.get("acessos", []),
            dados_extras=extras
        )

    @property
    def titulo(self):
        return (
            self.unidade
            or self.empresa_gcom
            or f"ETB {self.etb}"
        )

    @property
    def cnpj_formatado(self):
        numeros = "".join(
            c
            for c in self.cnpj
            if c.isdigit()
        )

        if len(numeros) != 14:
            return self.cnpj

        return (
            f"{numeros[0:2]}."
            f"{numeros[2:5]}."
            f"{numeros[5:8]}/"
            f"{numeros[8:12]}-"
            f"{numeros[12:14]}"
        )

    @property
    def primeiro_anydesk(self):
        for acesso in self.acessos:
            if acesso.get(
                "anydesk"
            ):
                return acesso[
                    "anydesk"
                ]

        return ""
