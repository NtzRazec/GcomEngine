# Agenda rápida: Próximos dias + Histórico por loja

Substitua estes arquivos no projeto:

- database/initializer.py
- database/agenda_repository.py
- agendamento/tela.py

Depois copie `migrar_cache_agenda.py` para a raiz do projeto e execute uma vez:

```powershell
python migrar_cache_agenda.py
```

Depois rode:

```powershell
python main.py
```

## Comportamento

- A aba **Próximos dias** carrega somente 3, 7 ou 14 dias.
- O padrão é 7 dias.
- Ela não carrega todo o histórico.
- A aba **Histórico** começa vazia.
- O histórico só pesquisa quando você informa pelo menos 3 caracteres da loja.
- Cada pesquisa retorna no máximo 50 resultados.
- O banco existente é migrado automaticamente, sem precisar apagar o SQLite.
