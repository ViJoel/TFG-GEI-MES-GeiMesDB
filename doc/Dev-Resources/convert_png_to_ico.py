"""
Script utilizado para generar un .ico a partir de un .png.
"""

from pathlib import Path

from PIL import Image

base_dir = Path(__file__).parent

input_file = base_dir / "icon.png"
output_file = base_dir / "icon.ico"

image = Image.open(input_file)

image.save(
    output_file,
    format="ICO",
    sizes=[
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256),
    ],
)

print(f"Icono generado: {output_file}")
