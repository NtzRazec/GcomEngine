import logging
import os
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "gcom_engine.log")

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("GCOM_ENGINE")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    arquivo_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    arquivo_handler.setFormatter(formatter)
    logger.addHandler(arquivo_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def info(mensagem):
    logger.info(mensagem)


def aviso(mensagem):
    logger.warning(mensagem)


def erro(mensagem):
    logger.error(mensagem)


def registrar_inicio():
    info("GCOM Engine iniciado.")


def registrar_encerramento():
    info("GCOM Engine encerrado.")


def registrar_status_sessao(status):
    info(f"Status da sessão Portal GCOM: {status}")


def registrar_robo(mensagem):
    info(f"Robô Agendamento | {mensagem}")


def registrar_erro_robo(mensagem):
    erro(f"Robô Agendamento | {mensagem}")
