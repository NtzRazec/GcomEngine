from database.initializer import inicializar_banco
from services.logger_service import registrar_inicio, registrar_encerramento
from app.window import MainWindow


def main():
    inicializar_banco()
    registrar_inicio()

    app = MainWindow()

    try:
        app.mainloop()
    finally:
        registrar_encerramento()


if __name__ == "__main__":
    main()
