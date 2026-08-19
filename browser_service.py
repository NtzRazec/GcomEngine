# services/browser_service.py

import json
import os
import sys

# ==========================================================
# DIRETÓRIO DO PROGRAMA
# ==========================================================


def obter_diretorio_programa():
    """
    Em desenvolvimento:
        usa a raiz do projeto.

    No .exe:
        usa a pasta onde GCOM Engine.exe está instalado.
    """

    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = obter_diretorio_programa()


# ==========================================================
# PLAYWRIGHT / CHROMIUM
# ==========================================================

PLAYWRIGHT_BROWSERS_DIR = os.path.join(BASE_DIR, "pw-browsers")

# MUITO IMPORTANTE:
# precisa ser definido antes de importar playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = PLAYWRIGHT_BROWSERS_DIR


# ==========================================================
# AGORA IMPORTAMOS O PLAYWRIGHT
# ==========================================================

from playwright.sync_api import sync_playwright

# ==========================================================
# IMPORTS DO PROJETO
# ==========================================================

from config.config import obter_env

from services.logger_service import info, erro

# ==========================================================
# DIRETÓRIOS DE SESSÃO
# ==========================================================

DATA_DIR = os.path.join(BASE_DIR, "data")

SESSION_DIR = os.path.join(DATA_DIR, "sessions")

PROFILE_DIR = os.path.join(SESSION_DIR, "gcom_profile")

SESSION_MARKER = os.path.join(SESSION_DIR, "gcom_session.json")


os.makedirs(DATA_DIR, exist_ok=True)

os.makedirs(SESSION_DIR, exist_ok=True)

os.makedirs(PROFILE_DIR, exist_ok=True)


# ==========================================================
# BROWSER SERVICE
# ==========================================================


class BrowserService:

    def __init__(self):

        self.playwright = None
        self.context = None
        self.page = None

    # ======================================================
    # SESSÃO EXISTE?
    # ======================================================

    @staticmethod
    def sessao_existe():

        return os.path.isfile(SESSION_MARKER)

    # ======================================================
    # VERIFICAR CHROMIUM
    # ======================================================

    @staticmethod
    def navegador_existe():

        if not os.path.exists(PLAYWRIGHT_BROWSERS_DIR):
            return False

        try:

            itens = os.listdir(PLAYWRIGHT_BROWSERS_DIR)

            return any(item.lower().startswith("chromium") for item in itens)

        except Exception:

            return False

    # ======================================================
    # INICIAR NAVEGADOR
    # ======================================================

    def iniciar(self, headless=True, usar_sessao=True):

        if self.context:

            return self.page

        # ==================================================
        # VALIDAR CHROMIUM
        # ==================================================

        if not self.navegador_existe():

            raise FileNotFoundError(
                "Chromium do Playwright não encontrado.\n\n"
                f"Pasta esperada:\n"
                f"{PLAYWRIGHT_BROWSERS_DIR}\n\n"
                "Verifique se a pasta pw-browsers "
                "foi instalada junto com o GCOM Engine."
            )

        info("Iniciando navegador do Portal GCOM.")

        info(f"Playwright Browsers: " f"{PLAYWRIGHT_BROWSERS_DIR}")

        # ==================================================
        # PLAYWRIGHT
        # ==================================================

        self.playwright = sync_playwright().start()

        # ==================================================
        # CONTEXTO PERSISTENTE
        # ==================================================

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=headless,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )

        # ==================================================
        # RESTAURAR COOKIES
        # ==================================================

        if usar_sessao and os.path.isfile(SESSION_MARKER):

            try:

                with open(SESSION_MARKER, "r", encoding="utf-8") as arquivo:

                    estado = json.load(arquivo)

                cookies = estado.get("cookies", [])

                if cookies:

                    self.context.add_cookies(cookies)

                    nomes = [cookie.get("name", "") for cookie in cookies]

                    info("Cookies ativos no contexto: " f"{nomes}")

            except Exception as exception:

                erro("Erro ao restaurar sessão: " f"{exception}")

        # ==================================================
        # PÁGINA
        # ==================================================

        paginas = self.context.pages

        if paginas:

            self.page = paginas[0]

        else:

            self.page = self.context.new_page()

        return self.page

    # ======================================================
    # ABRIR COM SESSÃO
    # ======================================================

    def abrir_com_sessao(self):

        if not self.sessao_existe():

            return None

        return self.iniciar(headless=True, usar_sessao=True)

    # ======================================================
    # ABRIR LOGIN
    # ======================================================

    def abrir_login(self):

        url_login = obter_env("GCOM_LOGIN_URL")

        if not url_login:

            raise ValueError("GCOM_LOGIN_URL não definida no .env")

        pagina = self.iniciar(headless=False, usar_sessao=False)

        pagina.goto(url_login, wait_until="domcontentloaded", timeout=30000)

        return pagina

    # ======================================================
    # SALVAR SESSÃO
    # ======================================================

    def salvar_sessao(self):

        if not self.context:

            return False

        try:

            estado = self.context.storage_state()

            with open(SESSION_MARKER, "w", encoding="utf-8") as arquivo:

                json.dump(estado, arquivo, ensure_ascii=False, indent=2)

            info("Sessão do Portal GCOM salva.")

            return True

        except Exception as exception:

            erro("Erro ao salvar sessão: " f"{exception}")

            return False

    # ======================================================
    # TESTAR PÁGINA PROTEGIDA
    # ======================================================

    def acessar_pagina_protegida(self, pagina=None):

        pagina = pagina or self.page

        if pagina is None:

            return False

        url = obter_env("GCOM_URL_PROTEGIDA")

        if not url:

            raise ValueError("GCOM_URL_PROTEGIDA " "não definida no .env")

        try:

            pagina.goto(url, wait_until="domcontentloaded", timeout=30000)

            pagina.wait_for_timeout(700)

            texto = pagina.locator("body").inner_text().lower()

            # Se encontrou formulário de login,
            # sessão expirou ou não está autenticada.
            if "fazer login" in texto and "empresa" in texto and "senha" in texto:

                return False

            return True

        except Exception as exception:

            erro("Erro ao testar página protegida: " f"{exception}")

            return False

    # ======================================================
    # URL ATUAL
    # ======================================================

    def obter_url_atual(self):

        if not self.page:

            return ""

        try:

            return self.page.url

        except Exception:

            return ""

    # ======================================================
    # FECHAR
    # ======================================================

    def fechar(self):

        try:

            if self.context:

                self.context.close()

        except Exception:

            pass

        try:

            if self.playwright:

                self.playwright.stop()

        except Exception:

            pass

        self.page = None
        self.context = None
        self.playwright = None
