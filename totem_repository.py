from database.connection import conectar


def substituir_totens(
    lista_totens
):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "DELETE FROM cache_acessos"
        )
        cursor.execute(
            "DELETE FROM cache_totens"
        )

        for item in lista_totens:
            cursor.execute(
                """
                INSERT INTO cache_totens (
                    aba,
                    marca,
                    tipo,
                    data,
                    empresa_gcom,
                    cnpj,
                    etb,
                    unidade,
                    status,
                    responsavel,
                    quantidade,
                    impressora,
                    dados_json,
                    atualizado_em
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    item.get("aba", ""),
                    item.get("marca", ""),
                    item.get("tipo", ""),
                    item.get("data", ""),
                    item.get("empresa_gcom", ""),
                    item.get("cnpj", ""),
                    item.get("etb", ""),
                    item.get("unidade", ""),
                    item.get("status", ""),
                    item.get("responsavel", ""),
                    item.get("quantidade", 0),
                    item.get("impressora", ""),
                    item.get("dados_json", "{}"),
                    item.get("atualizado_em", "")
                )
            )

            totem_id = cursor.lastrowid

            for acesso in item.get(
                "acessos",
                []
            ):
                cursor.execute(
                    """
                    INSERT INTO cache_acessos (
                        totem_id,
                        identificador,
                        anydesk,
                        terminal
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        totem_id,
                        acesso.get(
                            "identificador",
                            ""
                        ),
                        acesso.get(
                            "anydesk",
                            ""
                        ),
                        acesso.get(
                            "terminal",
                            ""
                        )
                    )
                )

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def pesquisar_totens(
    termo
):
    termo = str(
        termo or ""
    ).strip()

    if not termo:
        return []

    numeros = "".join(
        c
        for c in termo
        if c.isdigit()
    )

    pesquisa = f"%{termo}%"
    pesquisa_numeros = (
        f"%{numeros}%"
        if numeros
        else "%"
    )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT DISTINCT t.*
        FROM cache_totens t

        LEFT JOIN cache_acessos a
        ON a.totem_id = t.id

        WHERE
            t.etb LIKE ?
            OR t.cnpj LIKE ?
            OR t.empresa_gcom LIKE ?
            OR t.unidade LIKE ?
            OR t.data LIKE ?
            OR t.tipo LIKE ?
            OR t.marca LIKE ?
            OR a.identificador LIKE ?
            OR a.anydesk LIKE ?
            OR a.terminal LIKE ?

        ORDER BY t.unidade
        """,
        (
            pesquisa,
            pesquisa_numeros,
            pesquisa,
            pesquisa,
            pesquisa,
            pesquisa,
            pesquisa,
            pesquisa,
            pesquisa_numeros,
            pesquisa
        )
    )

    registros = []

    for linha in cursor.fetchall():
        registro = dict(
            linha
        )

        cursor.execute(
            """
            SELECT
                identificador,
                anydesk,
                terminal
            FROM cache_acessos
            WHERE totem_id = ?
            ORDER BY identificador
            """,
            (
                registro["id"],
            )
        )

        registro["acessos"] = [
            dict(acesso)
            for acesso in cursor.fetchall()
        ]

        registros.append(
            registro
        )

    conexao.close()

    return registros
