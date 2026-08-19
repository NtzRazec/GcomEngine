import os

from google.auth.transport.requests import Request

from google.oauth2.credentials import Credentials

from google_auth_oauthlib.flow import InstalledAppFlow

from config.config import BASE_DIR

# ==========================================================
# SCOPES
# ==========================================================

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


# ==========================================================
# CAMINHOS
# ==========================================================

OAUTH_CLIENT_FILE = os.path.join(BASE_DIR, "credentials", "google_oauth_client.json")


TOKEN_DIR = os.path.join(BASE_DIR, "data", "sessions")


TOKEN_FILE = os.path.join(TOKEN_DIR, "google_token.json")


os.makedirs(TOKEN_DIR, exist_ok=True)


# ==========================================================
# CLIENTE OAUTH EXISTE?
# ==========================================================


def oauth_client_existe():

    return os.path.isfile(OAUTH_CLIENT_FILE)


# ==========================================================
# TOKEN EXISTE?
# ==========================================================


def token_existe():

    return os.path.isfile(TOKEN_FILE)


# ==========================================================
# SALVAR TOKEN
# ==========================================================


def salvar_token(credenciais):

    os.makedirs(TOKEN_DIR, exist_ok=True)

    with open(TOKEN_FILE, "w", encoding="utf-8") as arquivo:

        arquivo.write(credenciais.to_json())


# ==========================================================
# CARREGAR CREDENCIAIS
# ==========================================================


def carregar_credenciais():

    credenciais = None

    if os.path.exists(TOKEN_FILE):

        try:

            credenciais = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        except Exception:

            credenciais = None

    if credenciais and credenciais.expired and credenciais.refresh_token:

        try:

            credenciais.refresh(Request())

            salvar_token(credenciais)

        except Exception:

            credenciais = None

    if credenciais and credenciais.valid:

        return credenciais

    return None


# ==========================================================
# CONECTAR GOOGLE
# ==========================================================


def conectar_google():

    if not oauth_client_existe():

        raise FileNotFoundError(
            "Arquivo OAuth não encontrado:\n" f"{OAUTH_CLIENT_FILE}"
        )

    credenciais = carregar_credenciais()

    if credenciais:

        return credenciais

    fluxo = InstalledAppFlow.from_client_secrets_file(OAUTH_CLIENT_FILE, SCOPES)

    credenciais = fluxo.run_local_server(
        port=0,
        open_browser=True,
        authorization_prompt_message=(
            "Abrindo navegador para " "conectar sua conta Google..."
        ),
        success_message=(
            "Conta Google conectada com sucesso. " "Você pode fechar esta página."
        ),
    )

    salvar_token(credenciais)

    return credenciais


# ==========================================================
# OBTER CREDENCIAIS
# ==========================================================


def obter_credenciais(solicitar_login=False):

    credenciais = carregar_credenciais()

    if credenciais:

        return credenciais

    if solicitar_login:

        return conectar_google()

    return None


# ==========================================================
# DESCONECTAR
# ==========================================================


def desconectar_google():

    if os.path.exists(TOKEN_FILE):

        os.remove(TOKEN_FILE)

        return True

    return False


# ==========================================================
# STATUS
# ==========================================================


def status_google():

    if not oauth_client_existe():

        return {
            "conectado": False,
            "codigo": "SEM_CLIENTE_OAUTH",
            "mensagem": ("Arquivo google_oauth_client.json " "não encontrado."),
        }

    credenciais = carregar_credenciais()

    if credenciais:

        return {
            "conectado": True,
            "codigo": "CONECTADO",
            "mensagem": ("Conta Google conectada."),
        }

    return {
        "conectado": False,
        "codigo": "DESCONECTADO",
        "mensagem": ("Conta Google não conectada."),
    }
