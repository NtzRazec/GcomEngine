import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import sqlite3
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

APP_NAME = "GCOM Engine"

# =========================================================
# CAMINHOS
# =========================================================

def obter_diretorio_base():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = obter_diretorio_base()
DATA_DIR = os.path.join(BASE_DIR, "data")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
GOOGLE_DIR = os.path.join(DATA_DIR, "google")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(GOOGLE_DIR, exist_ok=True)

DB_FILE = os.path.join(DATA_DIR, "gcom_engine.db")
SESSION_FILE = os.path.join(SESSIONS_DIR, "engine_session.txt")

# Ajuste estes caminhos caso seus arquivos tenham outros nomes.
GCOM_SESSION_FILE = os.path.join(SESSIONS_DIR, "gcom_session.json")
GOOGLE_TOKEN_FILE = os.path.join(GOOGLE_DIR, "token.json")

# =========================================================
# TEMA
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#08111F"
CARD = "#0D1B2A"
CARD_2 = "#10243A"
BORDER = "#1C3D5A"
TEXT = "#EAF4FF"
TEXT_MUTED = "#8FA9C0"
ACCENT = "#18B7FF"
ACCENT_HOVER = "#0B94D1"
GREEN = "#2DD881"
RED = "#FF5C6C"
YELLOW = "#FFC857"

# =========================================================
# BANCO
# =========================================================

def conectar():
    return sqlite3.connect(DB_FILE)

def inicializar_banco():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            senha_salt TEXT NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessoes_app (
            token TEXT PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            expira_em TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()

# =========================================================
# SEGURANÇA
# =========================================================

def gerar_hash_senha(senha: str, salt_hex: str | None = None):
    if salt_hex is None:
        salt = secrets.token_bytes(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)

    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        200_000
    ).hex()

    return senha_hash, salt_hex

def validar_senha(senha, hash_salvo, salt_salvo):
    calculado, _ = gerar_hash_senha(senha, salt_salvo)
    return hmac.compare_digest(calculado, hash_salvo)

# =========================================================
# USUÁRIOS
# =========================================================

def quantidade_usuarios():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total = cur.fetchone()[0]
    conn.close()
    return total

def criar_usuario(nome, login, senha):
    nome = nome.strip()
    login = login.strip().lower()

    if not nome or not login or not senha:
        raise ValueError("Preencha nome, usuário e senha.")

    if len(senha) < 6:
        raise ValueError("A senha deve possuir pelo menos 6 caracteres.")

    senha_hash, salt = gerar_hash_senha(senha)

    conn = conectar()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO usuarios (
                nome,
                login,
                senha_hash,
                senha_salt,
                ativo,
                criado_em
            )
            VALUES (?, ?, ?, ?, 1, ?)
        """, (
            nome,
            login,
            senha_hash,
            salt,
            datetime.now().isoformat(timespec="seconds")
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Este usuário já existe.")
    finally:
        conn.close()

def autenticar_usuario(login, senha):
    login = login.strip().lower()

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, login, senha_hash, senha_salt, ativo
        FROM usuarios
        WHERE login = ?
    """, (login,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    usuario_id, nome, login_db, senha_hash, salt, ativo = row

    if not ativo:
        return None

    if not validar_senha(senha, senha_hash, salt):
        return None

    return {
        "id": usuario_id,
        "nome": nome,
        "login": login_db
    }

# =========================================================
# SESSÃO LOCAL DO GCOM ENGINE
# =========================================================

def criar_sessao_app(usuario_id):
    token = secrets.token_urlsafe(48)
    expira_em = datetime.now() + timedelta(days=30)

    conn = conectar()
    cur = conn.cursor()

    cur.execute("DELETE FROM sessoes_app WHERE usuario_id = ?", (usuario_id,))
    cur.execute("""
        INSERT INTO sessoes_app (token, usuario_id, expira_em)
        VALUES (?, ?, ?)
    """, (
        token,
        usuario_id,
        expira_em.isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()

    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        f.write(token)

def remover_sessao_app():
    if not os.path.exists(SESSION_FILE):
        return

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            token = f.read().strip()

        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM sessoes_app WHERE token = ?", (token,))
        conn.commit()
        conn.close()
    except Exception:
        pass

    try:
        os.remove(SESSION_FILE)
    except OSError:
        pass

def carregar_sessao_app():
    if not os.path.exists(SESSION_FILE):
        return None

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            token = f.read().strip()

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                u.id,
                u.nome,
                u.login,
                s.expira_em
            FROM sessoes_app s
            JOIN usuarios u ON u.id = s.usuario_id
            WHERE s.token = ?
              AND u.ativo = 1
        """, (token,))

        row = cur.fetchone()
        conn.close()

        if not row:
            remover_sessao_app()
            return None

        usuario_id, nome, login, expira_em = row

        if datetime.fromisoformat(expira_em) <= datetime.now():
            remover_sessao_app()
            return None

        return {
            "id": usuario_id,
            "nome": nome,
            "login": login
        }

    except Exception:
        remover_sessao_app()
        return None

# =========================================================
# STATUS DAS INTEGRAÇÕES
# =========================================================

def status_integracoes():
    # Aqui estamos verificando apenas se os arquivos de sessão existem.
    # A validação real do GCOM deve ser feita pelo Playwright ao abrir o módulo.
    return {
        "gcom": os.path.exists(GCOM_SESSION_FILE),
        "google": os.path.exists(GOOGLE_TOKEN_FILE)
    }

# =========================================================
# TELA PRINCIPAL DEMONSTRATIVA
# =========================================================

class MainWindow(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()

        self.usuario = usuario

        self.title(APP_NAME)
        self.geometry("1120x680")
        self.minsize(980, 600)
        self.configure(fg_color=BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._sidebar()
        self._conteudo()

    def _sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=CARD
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="GCOM ENGINE",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ACCENT
        ).pack(pady=(28, 8))

        ctk.CTkLabel(
            sidebar,
            text=self.usuario["nome"],
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        ).pack(pady=(0, 28))

        botoes = [
            ("⌂  Início", self.mostrar_inicio),
            ("▣  Agendamento", lambda: self.modulo("Agendamento")),
            ("▤  Totens GCOM", lambda: self.modulo("Totens GCOM")),
            ("✓  Fechamentos", lambda: self.modulo("Fechamentos")),
            ("◎  Consumo IA", lambda: self.modulo("Consumo IA")),
        ]

        for texto, comando in botoes:
            ctk.CTkButton(
                sidebar,
                text=texto,
                command=comando,
                height=42,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                hover_color=CARD_2,
                text_color=TEXT,
                font=ctk.CTkFont(size=14)
            ).pack(fill="x", padx=14, pady=3)

        ctk.CTkButton(
            sidebar,
            text="Sair",
            command=self.logout,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#3A1720",
            text_color=RED
        ).pack(side="bottom", fill="x", padx=14, pady=18)

    def _conteudo(self):
        self.content = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.mostrar_inicio()

    def limpar_conteudo(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpar_conteudo()

        ctk.CTkLabel(
            self.content,
            text=f"Olá, {self.usuario['nome']}",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=36, pady=(34, 4))

        ctk.CTkLabel(
            self.content,
            text="Central de ferramentas GCOM",
            font=ctk.CTkFont(size=15),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=36, pady=(0, 28))

        status = status_integracoes()

        painel = ctk.CTkFrame(
            self.content,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )
        painel.pack(fill="x", padx=36, pady=8)

        ctk.CTkLabel(
            painel,
            text="Conexões",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=22, pady=(18, 12))

        self._linha_status(
            painel,
            "Portal GCOM",
            status["gcom"]
        )

        self._linha_status(
            painel,
            "Google",
            status["google"]
        )

        ctk.CTkLabel(
            painel,
            text=(
                "As sessões são reaproveitadas automaticamente. "
                "Quando uma sessão expirar, o módulo correspondente "
                "deve solicitar uma nova autenticação."
            ),
            wraplength=700,
            justify="left",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=22, pady=(10, 20))

        modulos = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        modulos.pack(fill="x", padx=36, pady=24)

        self._card_modulo(
            modulos,
            "Agendamento",
            "Consultar e organizar agendamentos.",
            lambda: self.modulo("Agendamento")
        )

        self._card_modulo(
            modulos,
            "Totens GCOM",
            "Consultar lojas, CNPJ, AnyDesk e demais dados.",
            lambda: self.modulo("Totens GCOM")
        )

        self._card_modulo(
            modulos,
            "Fechamentos",
            "Preparar chamados com IA e processar a fila em massa.",
            lambda: self.modulo("Fechamentos")
        )

    def _linha_status(self, parent, titulo, conectado):
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.pack(fill="x", padx=22, pady=5)

        ctk.CTkLabel(
            linha,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT
        ).pack(side="left")

        ctk.CTkLabel(
            linha,
            text="● Conectado" if conectado else "● Não conectado",
            text_color=GREEN if conectado else YELLOW,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right")

    def _card_modulo(self, parent, titulo, descricao, comando):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )
        card.pack(fill="x", pady=7)

        texto = ctk.CTkFrame(card, fg_color="transparent")
        texto.pack(side="left", fill="both", expand=True, padx=20, pady=18)

        ctk.CTkLabel(
            texto,
            text=titulo,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            texto,
            text=descricao,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(
            card,
            text="Abrir",
            width=100,
            command=comando,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#001521"
        ).pack(side="right", padx=20)

    def modulo(self, nome):
        messagebox.showinfo(
            APP_NAME,
            f"Módulo '{nome}' selecionado.\n\n"
            "Aqui você conecta a tela já existente do seu GCOM Engine."
        )

    def logout(self):
        remover_sessao_app()
        self.destroy()
        abrir_login()

# =========================================================
# LOGIN
# =========================================================

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} - Login")
        self.geometry("920x560")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._painel_esquerdo()
        self._painel_login()

        self.after(200, self.tentar_sessao_salva)

    def _painel_esquerdo(self):
        painel = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#071827"
        )
        painel.grid(row=0, column=0, sticky="nsew")

        container = ctk.CTkFrame(painel, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container,
            text="GCOM",
            font=ctk.CTkFont(size=46, weight="bold"),
            text_color=ACCENT
        ).pack()

        ctk.CTkLabel(
            container,
            text="ENGINE",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=TEXT
        ).pack(pady=(0, 18))

        ctk.CTkLabel(
            container,
            text="Uma única entrada para suas\nferramentas de suporte.",
            justify="center",
            font=ctk.CTkFont(size=15),
            text_color=TEXT_MUTED
        ).pack()

    def _painel_login(self):
        painel = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=BG
        )
        painel.grid(row=0, column=1, sticky="nsew")

        form = ctk.CTkFrame(
            painel,
            width=350,
            fg_color="transparent"
        )
        form.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            form,
            text="Entrar",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            form,
            text="Acesse o GCOM Engine",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(4, 24))

        self.entry_login = ctk.CTkEntry(
            form,
            width=330,
            height=44,
            placeholder_text="Usuário",
            fg_color=CARD,
            border_color=BORDER,
            text_color=TEXT
        )
        self.entry_login.pack(pady=6)

        self.entry_senha = ctk.CTkEntry(
            form,
            width=330,
            height=44,
            placeholder_text="Senha",
            show="●",
            fg_color=CARD,
            border_color=BORDER,
            text_color=TEXT
        )
        self.entry_senha.pack(pady=6)

        self.manter = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(
            form,
            text="Manter conectado",
            variable=self.manter,
            text_color=TEXT_MUTED,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER
        ).pack(anchor="w", pady=(10, 18))

        ctk.CTkButton(
            form,
            text="ENTRAR",
            width=330,
            height=44,
            command=self.entrar,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#001521",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack()

        if quantidade_usuarios() == 0:
            ctk.CTkButton(
                form,
                text="Criar primeiro usuário",
                width=330,
                height=38,
                command=self.abrir_cadastro,
                fg_color="transparent",
                hover_color=CARD_2,
                border_width=1,
                border_color=BORDER,
                text_color=TEXT
            ).pack(pady=(12, 0))

        self.entry_senha.bind("<Return>", lambda event: self.entrar())

    def tentar_sessao_salva(self):
        usuario = carregar_sessao_app()
        if usuario:
            self.abrir_sistema(usuario)

    def entrar(self):
        login = self.entry_login.get()
        senha = self.entry_senha.get()

        usuario = autenticar_usuario(login, senha)

        if not usuario:
            messagebox.showerror(
                APP_NAME,
                "Usuário ou senha inválidos."
            )
            return

        if self.manter.get():
            criar_sessao_app(usuario["id"])
        else:
            remover_sessao_app()

        self.abrir_sistema(usuario)

    def abrir_cadastro(self):
        CadastroWindow(self)

    def abrir_sistema(self, usuario):
        self.destroy()
        app = MainWindow(usuario)
        app.mainloop()

# =========================================================
# CADASTRO INICIAL
# =========================================================

class CadastroWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("Criar usuário")
        self.geometry("430x450")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text="Criar primeiro usuário",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color=TEXT
        ).pack(pady=(28, 20))

        self.nome = self._campo("Nome")
        self.login = self._campo("Usuário")
        self.senha = self._campo("Senha", senha=True)
        self.confirmacao = self._campo("Confirmar senha", senha=True)

        ctk.CTkButton(
            self,
            text="CRIAR USUÁRIO",
            width=320,
            height=42,
            command=self.salvar,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#001521",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=20)

    def _campo(self, placeholder, senha=False):
        campo = ctk.CTkEntry(
            self,
            width=320,
            height=42,
            placeholder_text=placeholder,
            show="●" if senha else "",
            fg_color=CARD,
            border_color=BORDER,
            text_color=TEXT
        )
        campo.pack(pady=6)
        return campo

    def salvar(self):
        if self.senha.get() != self.confirmacao.get():
            messagebox.showerror(
                APP_NAME,
                "As senhas não coincidem."
            )
            return

        try:
            criar_usuario(
                self.nome.get(),
                self.login.get(),
                self.senha.get()
            )

            messagebox.showinfo(
                APP_NAME,
                "Usuário criado com sucesso."
            )

            self.destroy()

        except ValueError as erro:
            messagebox.showerror(APP_NAME, str(erro))

# =========================================================
# EXECUÇÃO
# =========================================================

def abrir_login():
    inicializar_banco()
    app = LoginWindow()
    app.mainloop()

if __name__ == "__main__":
    abrir_login()
