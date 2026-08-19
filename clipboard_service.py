import pyperclip


def copiar_texto(texto):
    if texto is None:
        return False

    texto = str(texto).strip()

    if not texto:
        return False

    try:
        pyperclip.copy(texto)
        return True
    except Exception:
        return False


def copiar_anydesk(anydesk):
    numero = "".join(
        c
        for c in str(anydesk or "")
        if c.isdigit()
    )
    return copiar_texto(numero)


def copiar_cnpj(cnpj):
    numero = "".join(
        c
        for c in str(cnpj or "")
        if c.isdigit()
    )
    return copiar_texto(numero)
