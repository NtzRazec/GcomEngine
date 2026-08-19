from database.connection import conectar


def _colunas_tabela(cursor, tabela):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return {linha["name"] for linha in cursor.fetchall()}


def _adicionar_coluna_se_faltar(cursor, tabela, coluna, definicao):
    if coluna not in _colunas_tabela(cursor, tabela):
        cursor.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"
        )


def inicializar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        # =====================================================
        # TABELA PRINCIPAL DOS TOTENS
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_totens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aba TEXT DEFAULT '',
                marca TEXT DEFAULT '',
                tipo TEXT DEFAULT '',
                data TEXT DEFAULT '',
                empresa_gcom TEXT DEFAULT '',
                cnpj TEXT DEFAULT '',
                etb TEXT DEFAULT '',
                unidade TEXT DEFAULT '',
                status TEXT DEFAULT '',
                responsavel TEXT DEFAULT '',
                quantidade INTEGER DEFAULT 0,
                impressora TEXT DEFAULT '',
                dados_json TEXT DEFAULT '{}',
                atualizado_em TEXT DEFAULT ''
            )
            """
        )

        # Garante compatibilidade com bancos de versões anteriores.
        colunas_totens = [
            ("aba", "TEXT DEFAULT ''"),
            ("marca", "TEXT DEFAULT ''"),
            ("tipo", "TEXT DEFAULT ''"),
            ("data", "TEXT DEFAULT ''"),
            ("empresa_gcom", "TEXT DEFAULT ''"),
            ("cnpj", "TEXT DEFAULT ''"),
            ("etb", "TEXT DEFAULT ''"),
            ("unidade", "TEXT DEFAULT ''"),
            ("status", "TEXT DEFAULT ''"),
            ("responsavel", "TEXT DEFAULT ''"),
            ("quantidade", "INTEGER DEFAULT 0"),
            ("impressora", "TEXT DEFAULT ''"),
            ("dados_json", "TEXT DEFAULT '{}'"),
            ("atualizado_em", "TEXT DEFAULT ''"),
        ]

        for coluna, definicao in colunas_totens:
            _adicionar_coluna_se_faltar(
                cursor,
                "cache_totens",
                coluna,
                definicao,
            )

        # =====================================================
        # ACESSOS DOS TOTENS
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                totem_id INTEGER NOT NULL,
                identificador TEXT DEFAULT '',
                anydesk TEXT DEFAULT '',
                terminal TEXT DEFAULT '',

                FOREIGN KEY (totem_id)
                REFERENCES cache_totens(id)
                ON DELETE CASCADE
            )
            """
        )

        colunas_acessos = [
            ("totem_id", "INTEGER"),
            ("identificador", "TEXT DEFAULT ''"),
            ("anydesk", "TEXT DEFAULT ''"),
            ("terminal", "TEXT DEFAULT ''"),
        ]

        for coluna, definicao in colunas_acessos:
            _adicionar_coluna_se_faltar(
                cursor,
                "cache_acessos",
                coluna,
                definicao,
            )

        # =====================================================
        # CACHE DA AGENDA
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_agenda (
                chamado TEXT PRIMARY KEY,
                id_agendamento TEXT,
                titulo TEXT,
                status TEXT,
                data_inicio TEXT,
                data_fim_previsto TEXT,
                data_inicio_real TEXT,
                data_fim_real TEXT,
                usuario_agendamento TEXT,
                usuario_execucao TEXT,
                chamado_execucao TEXT,
                tempo_execucao TEXT,
                observacoes TEXT,
                duracao_minutos INTEGER DEFAULT 0,
                ocupa_vaga INTEGER DEFAULT 1,
                capacidade INTEGER DEFAULT 4,
                horario_calendario TEXT,
                texto_evento TEXT,
                hash_resumo TEXT,
                atualizado_em TEXT,
                loja TEXT DEFAULT '',
                marca TEXT DEFAULT '',
                servico TEXT DEFAULT '',
                data_inicio_iso TEXT DEFAULT '',
                data_fim_previsto_iso TEXT DEFAULT ''
            )
            """
        )

        colunas_agenda = [
            ("loja", "TEXT DEFAULT ''"),
            ("marca", "TEXT DEFAULT ''"),
            ("servico", "TEXT DEFAULT ''"),
            ("data_inicio_iso", "TEXT DEFAULT ''"),
            ("data_fim_previsto_iso", "TEXT DEFAULT ''"),
        ]

        for coluna, definicao in colunas_agenda:
            _adicionar_coluna_se_faltar(
                cursor,
                "cache_agenda",
                coluna,
                definicao,
            )

        # =====================================================
        # ÍNDICES
        # =====================================================

        indices = [
            "CREATE INDEX IF NOT EXISTS idx_totens_etb ON cache_totens(etb)",
            "CREATE INDEX IF NOT EXISTS idx_totens_cnpj ON cache_totens(cnpj)",
            "CREATE INDEX IF NOT EXISTS idx_totens_unidade ON cache_totens(unidade)",
            "CREATE INDEX IF NOT EXISTS idx_totens_empresa ON cache_totens(empresa_gcom)",
            "CREATE INDEX IF NOT EXISTS idx_acessos_totem ON cache_acessos(totem_id)",
            "CREATE INDEX IF NOT EXISTS idx_acessos_anydesk ON cache_acessos(anydesk)",
            "CREATE INDEX IF NOT EXISTS idx_acessos_identificador ON cache_acessos(identificador)",
            "CREATE INDEX IF NOT EXISTS idx_agenda_chamado ON cache_agenda(chamado)",
            "CREATE INDEX IF NOT EXISTS idx_agenda_status ON cache_agenda(status)",
            "CREATE INDEX IF NOT EXISTS idx_agenda_loja ON cache_agenda(loja)",
            "CREATE INDEX IF NOT EXISTS idx_agenda_servico ON cache_agenda(servico)",
            "CREATE INDEX IF NOT EXISTS idx_agenda_inicio_iso ON cache_agenda(data_inicio_iso)",
        ]

        for comando in indices:
            cursor.execute(comando)

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()
