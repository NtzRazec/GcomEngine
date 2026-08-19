from PIL import Image


imagem = Image.open(
    "assets/gcom_engine.png"
).convert(
    "RGBA"
)

imagem.save(
    "assets/gcom_engine.ico",
    format="ICO",
    sizes=[
        (16, 16),
        (24, 24),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256),
    ]
)

print(
    "Ícone criado: assets/gcom_engine.ico"
)
