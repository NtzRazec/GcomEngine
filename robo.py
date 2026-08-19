import re

from config.config import obter_env

from services.browser_service import BrowserService

from services.logger_service import registrar_robo, registrar_erro_robo

from agendamento.regras import analisar_agendamento_existente

from database.agenda_repository import (
    gerar_hash_resumo,
    buscar_hashes_cache,
    salvar_agendamento,
)


class RoboAgendamento:

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    def __init__(self, on_progresso=None):

        self.browser = BrowserService()

        self.page = None

        self.on_progresso = on_progresso

        self.url_agendamento = obter_env("GCOM_AGENDAMENTO_URL")

    # ======================================================
    # PROGRESSO
    # ======================================================

    def _progresso(
        self, atual, total, mensagem="", novos=0, alterados=0, porcentagem=None
    ):

        if porcentagem is None:

            if total <= 0:
                porcentagem = 0

            else:
                porcentagem = int(atual / total * 100)

        porcentagem = max(0, min(100, porcentagem))

        if self.on_progresso:

            try:

                self.on_progresso(
                    {
                        "atual": atual,
                        "total": total,
                        "porcentagem": porcentagem,
                        "mensagem": mensagem,
                        "novos": novos,
                        "alterados": alterados,
                    }
                )

            except Exception as exception:

                registrar_erro_robo("Erro ao enviar progresso: " f"{exception}")

    # ======================================================
    # ABRIR AGENDA
    # ======================================================

    def abrir_agenda(self):

        try:

            self._progresso(
                atual=0, total=1, porcentagem=0, mensagem=("Abrindo Portal GCOM...")
            )

            self.page = self.browser.abrir_com_sessao()

            if self.page is None:

                registrar_erro_robo("Nenhuma sessão disponível.")

                return False

            if not self.url_agendamento:

                registrar_erro_robo("GCOM_AGENDAMENTO_URL " "não configurada.")

                return False

            self.page.goto(
                self.url_agendamento, wait_until="domcontentloaded", timeout=30000
            )

            self.page.wait_for_timeout(1200)

            texto = self.page.locator("body").inner_text().lower()

            if "fazer login" in texto and "empresa" in texto and "senha" in texto:

                registrar_erro_robo("Sessão expirada.")

                return False

            registrar_robo("Agenda aberta.")

            return True

        except Exception as exception:

            registrar_erro_robo("Erro ao abrir agenda: " f"{exception}")

            return False

    # ======================================================
    # LOCALIZAR EVENTOS
    # ======================================================

    def localizar_eventos(self):

        eventos = self.page.locator("a.fc-daygrid-event")

        quantidade = eventos.count()

        registrar_robo(f"{quantidade} eventos encontrados.")

        if quantidade == 0:
            return None

        return eventos

    # ======================================================
    # LER EVENTO RESUMIDO
    # ======================================================

    def ler_evento_resumido(self, evento):

        texto = evento.inner_text().strip()

        horario_match = re.search(r"\b(\d{1,2}:\d{2})\b", texto)

        chamado_match = re.search(r"#(\d+)", texto)

        horario = horario_match.group(1) if horario_match else ""

        chamado = chamado_match.group(1) if chamado_match else ""

        return {"texto": texto, "horario": horario, "chamado": chamado}

    # ======================================================
    # ABRIR DETALHES
    # ======================================================

    def abrir_detalhes_evento(self, evento):

        try:

            evento.scroll_into_view_if_needed()

            evento.click()

            self.page.wait_for_timeout(350)

            return True

        except Exception as exception:

            registrar_erro_robo("Erro ao abrir evento: " f"{exception}")

            return False

    # ======================================================
    # LOCALIZAR MODAL
    # ======================================================

    def localizar_modal(self):

        seletores = ("[role='dialog']", ".modal.show", ".modal", "[class*='modal']")

        for seletor in seletores:

            modais = self.page.locator(seletor)

            quantidade = modais.count()

            for indice in range(quantidade):

                modal = modais.nth(indice)

                try:

                    if not modal.is_visible():
                        continue

                    texto = modal.inner_text()

                    if "Detalhes Agendamento" in texto:

                        return modal

                except Exception:
                    continue

        return None

    # ======================================================
    # LER MODAL
    # ======================================================

    def ler_modal(self):

        modal = self.localizar_modal()

        if modal is None:

            registrar_erro_robo("Modal de detalhes não encontrado.")

            return None

        texto = modal.inner_text()

        mapa = {
            "ID": "id",
            "TÍTULO": "titulo",
            "TITULO": "titulo",
            "STATUS": "status",
            "DATA INÍCIO": "data_inicio",
            "DATA INICIO": "data_inicio",
            "DATA ÍNICIO": "data_inicio",
            "DATA FIM PREVISTO": "data_fim_previsto",
            "DATA INÍCIO REAL": "data_inicio_real",
            "DATA INICIO REAL": "data_inicio_real",
            "DATA ÍNICIO REAL": "data_inicio_real",
            "DATA FIM REAL": "data_fim_real",
            "USUÁRIO AGENDAMENTO": "usuario_agendamento",
            "USUARIO AGENDAMENTO": "usuario_agendamento",
            "CHAMADO AGENDAMENTO": "chamado_agendamento",
            "USUÁRIO EXECUÇÃO": "usuario_execucao",
            "USUARIO EXECUCAO": "usuario_execucao",
            "CHAMADO EXECUÇÃO": "chamado_execucao",
            "CHAMADO EXECUCAO": "chamado_execucao",
            "TEMPO DE EXECUÇÃO": "tempo_execucao",
            "TEMPO DE EXECUCAO": "tempo_execucao",
            "OBSERVAÇÕES": "observacoes",
            "OBSERVACOES": "observacoes",
        }

        dados = {valor: "" for valor in set(mapa.values())}

        itens = []

        for linha in texto.splitlines():

            partes = [parte.strip() for parte in linha.split("\t") if parte.strip()]

            itens.extend(partes)

        itens = [item for item in itens if (item.upper() != "DETALHES AGENDAMENTO")]

        indice = 0

        while indice < len(itens):

            chave = itens[indice].upper()

            if chave in mapa:

                valor = ""

                if indice + 1 < len(itens):

                    proximo = itens[indice + 1].upper()

                    if proximo not in mapa:

                        valor = itens[indice + 1]

                        indice += 1

                dados[mapa[chave]] = valor

            indice += 1

        # ==================================================
        # CHAMADO PELO TÍTULO
        # ==================================================

        if not dados.get("chamado_agendamento") and dados.get("titulo"):

            match = re.search(r"#(\d+)", dados["titulo"])

            if match:

                dados["chamado_agendamento"] = match.group(1)

        # ==================================================
        # REGRAS
        # ==================================================

        return analisar_agendamento_existente(dados)

    # ======================================================
    # FECHAR MODAL
    # ======================================================

    def fechar_modal(self):

        seletores = ("[aria-label='Close']", "button.btn-close", ".modal button.close")

        for seletor in seletores:

            botoes = self.page.locator(seletor)

            quantidade = botoes.count()

            for indice in range(quantidade):

                botao = botoes.nth(indice)

                try:

                    if botao.is_visible():

                        botao.click()

                        self.page.wait_for_timeout(150)

                        return True

                except Exception:
                    continue

        try:

            self.page.keyboard.press("Escape")

            self.page.wait_for_timeout(150)

        except Exception:
            pass

        return True

    # ======================================================
    # SINCRONIZAR CACHE
    # ======================================================

    def sincronizar_cache(self):

        # ==================================================
        # ABRIR AGENDA
        # ==================================================

        if not self.page:

            if not self.abrir_agenda():

                return {
                    "sucesso": False,
                    "total": 0,
                    "novos": 0,
                    "alterados": 0,
                    "atualizados": 0,
                    "ignorados": 0,
                    "erros": 0,
                }

        # ==================================================
        # LOCALIZAR EVENTOS
        # ==================================================

        eventos = self.localizar_eventos()

        if eventos is None:

            self._progresso(
                atual=0,
                total=0,
                porcentagem=100,
                mensagem=("Nenhum evento encontrado."),
            )

            return {
                "sucesso": True,
                "total": 0,
                "novos": 0,
                "alterados": 0,
                "atualizados": 0,
                "ignorados": 0,
                "erros": 0,
            }

        total = eventos.count()

        registrar_robo("Iniciando sincronização de " f"{total} eventos.")

        self._progresso(
            atual=0, total=total, porcentagem=1, mensagem=("Preparando comparação...")
        )

        # ==================================================
        # CACHE EM MEMÓRIA
        # ==================================================

        hashes_cache = buscar_hashes_cache()

        registrar_robo(f"{len(hashes_cache)} " "chamados já existem no cache.")

        # ==================================================
        # FASE 1
        # ==================================================

        pendentes = []

        ignorados = 0
        erros = 0
        novos = 0
        alterados = 0

        registrar_robo("Fase 1/2 | " "Comparando calendário com cache...")

        for indice in range(total):

            try:

                evento = eventos.nth(indice)

                resumo = self.ler_evento_resumido(evento)

                chamado = str(resumo.get("chamado", "")).strip()

                texto = resumo.get("texto", "")

                if not chamado:

                    erros += 1

                else:

                    hash_novo = gerar_hash_resumo(texto)

                    hash_antigo = hashes_cache.get(chamado)

                    # ======================================
                    # NOVO
                    # ======================================

                    if hash_antigo is None:

                        pendentes.append(
                            {
                                "indice": indice,
                                "chamado": chamado,
                                "resumo": resumo,
                                "tipo": "novo",
                            }
                        )

                        novos += 1

                    # ======================================
                    # ALTERADO
                    # ======================================

                    elif hash_novo != hash_antigo:

                        pendentes.append(
                            {
                                "indice": indice,
                                "chamado": chamado,
                                "resumo": resumo,
                                "tipo": "alterado",
                            }
                        )

                        alterados += 1

                    # ======================================
                    # IGUAL
                    # ======================================

                    else:

                        ignorados += 1

            except Exception as exception:

                erros += 1

                registrar_erro_robo(
                    "Erro ao comparar evento " f"{indice + 1}/{total}: " f"{exception}"
                )

            # ==============================================
            # PROGRESSO 0 → 90
            # ==============================================

            percentual = int((indice + 1) / total * 90)

            self._progresso(
                atual=indice + 1,
                total=total,
                porcentagem=percentual,
                mensagem=("Verificando agenda..."),
                novos=novos,
                alterados=alterados,
            )

            # ==============================================
            # LOG A CADA 50
            # ==============================================

            if (indice + 1) % 50 == 0 or indice + 1 == total:

                registrar_robo(f"Comparados " f"{indice + 1}/{total} " "eventos.")

        # ==================================================
        # RESUMO FASE 1
        # ==================================================

        registrar_robo(
            "Comparação concluída | "
            f"Novos: {novos} | "
            f"Alterados: {alterados} | "
            f"Cache: {ignorados}"
        )

        # ==================================================
        # NADA PARA ATUALIZAR
        # ==================================================

        if not pendentes:

            self._progresso(
                atual=total,
                total=total,
                porcentagem=100,
                mensagem=("Agenda já está atualizada."),
                novos=novos,
                alterados=alterados,
            )

            registrar_robo("Agenda já está totalmente atualizada.")

            return {
                "sucesso": True,
                "total": total,
                "novos": 0,
                "alterados": 0,
                "atualizados": 0,
                "ignorados": ignorados,
                "erros": erros,
            }

        # ==================================================
        # FASE 2
        # ==================================================

        registrar_robo(
            "Fase 2/2 | " f"Lendo detalhes de " f"{len(pendentes)} evento(s)..."
        )

        atualizados = 0

        total_pendentes = len(pendentes)

        for posicao, pendente in enumerate(pendentes, start=1):

            chamado = pendente["chamado"]

            resumo = pendente["resumo"]

            tipo = pendente["tipo"]

            try:

                registrar_robo(
                    f"[{posicao}/"
                    f"{total_pendentes}] "
                    f"{tipo.upper()} "
                    f"#{chamado}"
                )

                # ==========================================
                # LOCALIZAR EVENTO NOVAMENTE
                # ==========================================

                evento = (
                    self.page.locator("a.fc-daygrid-event")
                    .filter(has_text=(f"#{chamado}"))
                    .first
                )

                if evento.count() == 0:

                    erros += 1

                    registrar_erro_robo(
                        "Evento " f"#{chamado} " "não encontrado novamente."
                    )

                    continue

                # ==========================================
                # ABRIR
                # ==========================================

                if not (self.abrir_detalhes_evento(evento)):

                    erros += 1

                    registrar_erro_robo("Não foi possível abrir " f"#{chamado}.")

                    continue

                # ==========================================
                # LER
                # ==========================================

                dados = self.ler_modal()

                if not dados:

                    erros += 1

                    registrar_erro_robo("Não foi possível ler " f"#{chamado}.")

                    self.fechar_modal()

                    continue

                # ==========================================
                # COMPLETAR DADOS
                # ==========================================

                dados["texto_evento"] = resumo.get("texto", "")

                dados["horario_calendario"] = resumo.get("horario", "")

                if not dados.get("chamado_agendamento"):

                    dados["chamado_agendamento"] = chamado

                # ==========================================
                # SALVAR
                # ==========================================

                salvar_agendamento(dados)

                atualizados += 1

                registrar_robo(
                    f"#{chamado} salvo | "
                    f"{dados.get('status', '')} | "
                    f"{dados.get('data_inicio', '')}"
                )

                self.fechar_modal()

            except Exception as exception:

                erros += 1

                registrar_erro_robo("Erro no chamado " f"#{chamado}: " f"{exception}")

                try:
                    self.fechar_modal()
                except Exception:
                    pass

            # ==============================================
            # PROGRESSO 90 → 100
            # ==============================================

            progresso_segunda_fase = int((posicao / total_pendentes) * 10)

            porcentagem = 90 + progresso_segunda_fase

            self._progresso(
                atual=posicao,
                total=total_pendentes,
                porcentagem=porcentagem,
                mensagem=("Atualizando detalhes " f"do chamado #{chamado}..."),
                novos=novos,
                alterados=alterados,
            )

        # ==================================================
        # FINAL
        # ==================================================

        self._progresso(
            atual=total,
            total=total,
            porcentagem=100,
            mensagem=("Atualização concluída."),
            novos=novos,
            alterados=alterados,
        )

        registrar_robo(
            "Sincronização concluída | "
            f"Total: {total} | "
            f"Atualizados: {atualizados} | "
            f"Novos: {novos} | "
            f"Alterados: {alterados} | "
            f"Cache: {ignorados} | "
            f"Erros: {erros}"
        )

        return {
            "sucesso": True,
            "total": total,
            "novos": novos,
            "alterados": alterados,
            "atualizados": atualizados,
            "ignorados": ignorados,
            "erros": erros,
        }

    # ======================================================
    # FECHAR ROBÔ
    # ======================================================

    def fechar(self):

        try:

            self.browser.fechar()

        except Exception:
            pass

        self.page = None
