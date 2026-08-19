import hashlib
import re
from datetime import datetime, timedelta
from database.connection import conectar


def gerar_hash_resumo(texto):
    return hashlib.sha256(
        str(texto or "").strip().encode("utf-8")
    ).hexdigest()


def converter_para_iso(valor):
    valor = str(valor or "").strip()
    if not valor:
        return ""

    for formato in ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(valor, formato).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return ""


def extrair_loja_do_titulo(titulo):
    grupos = re.findall(r"\(([^()]*)\)", str(titulo or ""))
    candidatos = [
        g.strip()
        for g in grupos
        if g.strip() and "agendamento" not in g.lower()
    ]
    return candidatos[-1] if candidatos else ""


def extrair_marca_da_loja(loja):
    loja = str(loja or "").strip()
    return loja.split(" - ", 1)[0].strip() if " - " in loja else ""


def extrair_servico_do_titulo(titulo):
    titulo = re.sub(r"^#\d+\s*-\s*", "", str(titulo or "").strip())
    titulo = re.split(r"\s*\(agendamento\)", titulo, flags=re.IGNORECASE)[0]
    return titulo.strip(" -")


def _normalizar_registro(linha):
    registro = dict(linha)
    registro["ocupa_vaga"] = bool(registro.get("ocupa_vaga", 1))
    return registro


def buscar_chamado(chamado):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM cache_agenda WHERE chamado = ? LIMIT 1",
        (str(chamado),),
    )
    linha = cur.fetchone()
    con.close()
    return _normalizar_registro(linha) if linha else None


def buscar_hashes_cache():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT chamado, hash_resumo FROM cache_agenda")
    resultado = {
        str(linha["chamado"]): linha["hash_resumo"]
        for linha in cur.fetchall()
    }
    con.close()
    return resultado


def evento_precisa_atualizar(chamado, texto_evento):
    atual = buscar_chamado(chamado)
    return atual is None or gerar_hash_resumo(texto_evento) != atual.get("hash_resumo")


def salvar_agendamento(dados):
    chamado = str(dados.get("chamado_agendamento", "")).strip()
    if not chamado:
        return False

    titulo = dados.get("titulo", "")
    loja = dados.get("loja", "") or extrair_loja_do_titulo(titulo)
    marca = dados.get("marca", "") or extrair_marca_da_loja(loja)
    servico = dados.get("servico", "") or extrair_servico_do_titulo(titulo)
    data_inicio = dados.get("data_inicio", "")
    data_fim_previsto = dados.get("data_fim_previsto", "")
    texto_evento = dados.get("texto_evento", "")

    con = conectar()
    cur = con.cursor()

    cur.execute('''
        INSERT INTO cache_agenda (
            chamado,id_agendamento,titulo,status,data_inicio,data_fim_previsto,
            data_inicio_real,data_fim_real,usuario_agendamento,usuario_execucao,
            chamado_execucao,tempo_execucao,observacoes,duracao_minutos,
            ocupa_vaga,capacidade,horario_calendario,texto_evento,hash_resumo,
            atualizado_em,loja,marca,servico,data_inicio_iso,data_fim_previsto_iso
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(chamado) DO UPDATE SET
            id_agendamento=excluded.id_agendamento,
            titulo=excluded.titulo,
            status=excluded.status,
            data_inicio=excluded.data_inicio,
            data_fim_previsto=excluded.data_fim_previsto,
            data_inicio_real=excluded.data_inicio_real,
            data_fim_real=excluded.data_fim_real,
            usuario_agendamento=excluded.usuario_agendamento,
            usuario_execucao=excluded.usuario_execucao,
            chamado_execucao=excluded.chamado_execucao,
            tempo_execucao=excluded.tempo_execucao,
            observacoes=excluded.observacoes,
            duracao_minutos=excluded.duracao_minutos,
            ocupa_vaga=excluded.ocupa_vaga,
            capacidade=excluded.capacidade,
            horario_calendario=excluded.horario_calendario,
            texto_evento=excluded.texto_evento,
            hash_resumo=excluded.hash_resumo,
            atualizado_em=excluded.atualizado_em,
            loja=excluded.loja,
            marca=excluded.marca,
            servico=excluded.servico,
            data_inicio_iso=excluded.data_inicio_iso,
            data_fim_previsto_iso=excluded.data_fim_previsto_iso
    ''', (
        chamado,
        dados.get("id", ""),
        titulo,
        dados.get("status", ""),
        data_inicio,
        data_fim_previsto,
        dados.get("data_inicio_real", ""),
        dados.get("data_fim_real", ""),
        dados.get("usuario_agendamento", ""),
        dados.get("usuario_execucao", ""),
        dados.get("chamado_execucao", ""),
        dados.get("tempo_execucao", ""),
        dados.get("observacoes", ""),
        int(dados.get("duracao_minutos", 0) or 0),
        1 if dados.get("ocupa_vaga", True) else 0,
        int(dados.get("capacidade", 4) or 4),
        dados.get("horario_calendario", ""),
        texto_evento,
        gerar_hash_resumo(texto_evento),
        datetime.now().isoformat(timespec="seconds"),
        loja,
        marca,
        servico,
        converter_para_iso(data_inicio),
        converter_para_iso(data_fim_previsto),
    ))

    con.commit()
    con.close()
    return True


def buscar_por_data(data):
    inicio_iso = datetime.combine(data, datetime.min.time()).strftime("%Y-%m-%d %H:%M:%S")
    fim_iso = datetime.combine(data, datetime.max.time()).strftime("%Y-%m-%d %H:%M:%S")

    con = conectar()
    cur = con.cursor()
    cur.execute('''
        SELECT * FROM cache_agenda
        WHERE
            (data_inicio_iso <> '' AND data_inicio_iso BETWEEN ? AND ?)
            OR
            (data_inicio_iso = '' AND substr(data_inicio, 1, 10) = ?)
        ORDER BY
            CASE
                WHEN data_inicio_iso <> '' THEN data_inicio_iso
                ELSE substr(data_inicio, 7, 4) || '-' ||
                     substr(data_inicio, 4, 2) || '-' ||
                     substr(data_inicio, 1, 2) || ' ' ||
                     substr(data_inicio, 12)
            END
    ''', (inicio_iso, fim_iso, data.strftime("%d/%m/%Y")))

    dados = [_normalizar_registro(linha) for linha in cur.fetchall()]
    con.close()
    return dados


def buscar_proximos_dias(data_inicial, quantidade_dias=7):
    quantidade_dias = max(1, int(quantidade_dias))
    data_final = data_inicial + timedelta(days=quantidade_dias - 1)

    inicio_iso = datetime.combine(data_inicial, datetime.min.time()).strftime("%Y-%m-%d %H:%M:%S")
    fim_iso = datetime.combine(data_final, datetime.max.time()).strftime("%Y-%m-%d %H:%M:%S")

    con = conectar()
    cur = con.cursor()
    cur.execute('''
        SELECT * FROM cache_agenda
        WHERE
            (data_inicio_iso <> '' AND data_inicio_iso BETWEEN ? AND ?)
            OR
            (
                data_inicio_iso = ''
                AND datetime(
                    substr(data_inicio, 7, 4) || '-' ||
                    substr(data_inicio, 4, 2) || '-' ||
                    substr(data_inicio, 1, 2) || ' ' ||
                    substr(data_inicio, 12)
                ) BETWEEN ? AND ?
            )
        ORDER BY
            CASE
                WHEN data_inicio_iso <> '' THEN data_inicio_iso
                ELSE substr(data_inicio, 7, 4) || '-' ||
                     substr(data_inicio, 4, 2) || '-' ||
                     substr(data_inicio, 1, 2) || ' ' ||
                     substr(data_inicio, 12)
            END
    ''', (inicio_iso, fim_iso, inicio_iso, fim_iso))

    dados = [_normalizar_registro(linha) for linha in cur.fetchall()]
    con.close()
    return dados


def pesquisar_historico_loja(termo, limite=50):
    termo = str(termo or "").strip()
    if len(termo) < 3:
        return []

    limite = max(1, min(int(limite), 200))
    pesquisa = f"%{termo}%"

    con = conectar()
    cur = con.cursor()
    cur.execute('''
        SELECT * FROM cache_agenda
        WHERE
            loja LIKE ? COLLATE NOCASE
            OR titulo LIKE ? COLLATE NOCASE
        ORDER BY
            CASE
                WHEN data_inicio_iso <> '' THEN data_inicio_iso
                ELSE substr(data_inicio, 7, 4) || '-' ||
                     substr(data_inicio, 4, 2) || '-' ||
                     substr(data_inicio, 1, 2) || ' ' ||
                     substr(data_inicio, 12)
            END DESC
        LIMIT ?
    ''', (pesquisa, pesquisa, limite))

    dados = [_normalizar_registro(linha) for linha in cur.fetchall()]
    con.close()
    return dados


def atualizar_campos_derivados():
    con = conectar()
    cur = con.cursor()
    cur.execute('''
        SELECT chamado,titulo,data_inicio,data_fim_previsto,
               loja,marca,servico,data_inicio_iso,data_fim_previsto_iso
        FROM cache_agenda
    ''')

    registros = cur.fetchall()

    for registro in registros:
        titulo = registro["titulo"] or ""
        loja = registro["loja"] or extrair_loja_do_titulo(titulo)
        marca = registro["marca"] or extrair_marca_da_loja(loja)
        servico = registro["servico"] or extrair_servico_do_titulo(titulo)
        inicio_iso = registro["data_inicio_iso"] or converter_para_iso(registro["data_inicio"])
        fim_iso = registro["data_fim_previsto_iso"] or converter_para_iso(registro["data_fim_previsto"])

        cur.execute('''
            UPDATE cache_agenda
            SET loja=?, marca=?, servico=?, data_inicio_iso=?, data_fim_previsto_iso=?
            WHERE chamado=?
        ''', (
            loja, marca, servico, inicio_iso, fim_iso, registro["chamado"]
        ))

    con.commit()
    con.close()
    return len(registros)
