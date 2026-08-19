from database.initializer import inicializar_banco
from database.agenda_repository import atualizar_campos_derivados

inicializar_banco()
quantidade = atualizar_campos_derivados()

print(
    f"{quantidade} registro(s) da agenda foram revisados/migrados."
)
