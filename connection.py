import os
import sqlite3

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "data",
    "database"
)

DATABASE_FILE = os.path.join(
    DATABASE_DIR,
    "gcom_engine.db"
)

os.makedirs(
    DATABASE_DIR,
    exist_ok=True
)


def conectar():
    conexao = sqlite3.connect(
        DATABASE_FILE,
        timeout=30
    )

    conexao.row_factory = sqlite3.Row

    conexao.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conexao


def obter_caminho_banco():
    return DATABASE_FILE
