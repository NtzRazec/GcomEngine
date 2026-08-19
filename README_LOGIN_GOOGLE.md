# GCOM Engine - versão com login Google

Nesta versão, o módulo Totens não usa Service Account.

O próprio usuário conecta sua conta Google pelo navegador.

## Como funciona

1. O usuário abre `Totens GCOM`.
2. Clica em `Conectar Google`.
3. O navegador abre.
4. O usuário seleciona a conta Google que já possui acesso à planilha.
5. Autoriza acesso somente leitura ao Google Sheets.
6. O token é salvo localmente em:

   `data/sessions/google_token.json`

7. Nas próximas execuções, o usuário não precisa fazer login novamente enquanto o token puder ser renovado.

## Configuração do Google Cloud

No Google Cloud:

1. Ative a Google Sheets API.
2. Configure a tela de consentimento OAuth.
3. Crie um OAuth Client ID do tipo `Desktop app`.
4. Baixe o JSON.
5. Renomeie para:

   `google_oauth_client.json`

6. Coloque em:

   `credentials/google_oauth_client.json`

## .env

O `.env` real não está incluído.

Use `.env.example` como base.

## Dependências

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Executar

```powershell
python main.py
```

## Segurança

Não envie para Git:

- `.env`
- `credentials/google_oauth_client.json`
- `data/sessions/google_token.json`
- `data/sessions/gcom_session.json`
