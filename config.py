import json
import os
import sys

from dotenv import load_dotenv

# ==========================================================
# DIRETÓRIO DO PROGRAMA
# ==========================================================


def obter_diretorio_programa():

    # Quando estiver rodando como .exe
    if getattr(sys, "frozen", False):

        return os.path.dirname(sys.executable)

    # Quando estiver rodando pelo Python
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ==========================================================
# DIRETÓRIO DE RECURSOS EMPACOTADOS
# ==========================================================


def obter_diretorio_recursos():

    if getattr(sys, "frozen", False):

        return getattr(sys, "_MEIPASS", obter_diretorio_programa())

    return obter_diretorio_programa()


# ==========================================================
# CAMINHOS
# ==========================================================

BASE_DIR = obter_diretorio_programa()

RESOURCE_DIR = obter_diretorio_recursos()


ENV_FILE = os.path.join(BASE_DIR, ".env")


SETTINGS_FILE = os.path.join(RESOURCE_DIR, "config", "settings.json")


REGRAS_FILE = os.path.join(RESOURCE_DIR, "config", "regras.json")


# ==========================================================
# CARREGAR .ENV
# ==========================================================

load_dotenv(ENV_FILE, override=True)


# ==========================================================
# JSON
# ==========================================================


def carregar_json(caminho):

    if not os.path.exists(caminho):

        return {}

    try:

        with open(caminho, "r", encoding="utf-8") as arquivo:

            return json.load(arquivo)

    except (json.JSONDecodeError, OSError):

        return {}


# ==========================================================
# ENV
# ==========================================================


def obter_env(chave, padrao=None):

    return os.getenv(chave, padrao)


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================


def obter_configuracao(secao, chave, padrao=None):

    dados = carregar_json(SETTINGS_FILE)

    return dados.get(secao, {}).get(chave, padrao)


# ==========================================================
# REGRAS
# ==========================================================


def obter_regra(secao, chave=None, padrao=None):

    dados = carregar_json(REGRAS_FILE).get(secao, padrao)

    if chave is None:
        return dados

    if not isinstance(dados, dict):
        return padrao

    return dados.get(chave, padrao)
