from database.totem_repository import (
    pesquisar_totens
)
from totens.modelos import (
    Totem
)


def buscar_totens(termo):
    return [
        Totem.de_dict(
            item
        )
        for item in pesquisar_totens(
            termo
        )
    ]
