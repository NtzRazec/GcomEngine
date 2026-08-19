import os
import sys


def obter_base_dir():
    if getattr(sys, "frozen", False):
        return getattr(
            sys,
            "_MEIPASS",
            os.path.dirname(sys.executable)
        )

    return os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


def obter_caminho_icone():
    return os.path.join(
        obter_base_dir(),
        "assets",
        "gcom_engine.ico"
    )


def obter_caminho_logo():
    return os.path.join(
        obter_base_dir(),
        "assets",
        "gcom_engine.png"
    )


def aplicar_icone(janela):
    try:
        caminho = obter_caminho_icone()

        if os.path.exists(caminho):
            janela.iconbitmap(caminho)
    except Exception as erro:
        print(f"[ÍCONE] Erro ao aplicar ícone: {erro}")
