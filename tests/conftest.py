"""
Configura el entorno de pruebas para
que el código de 'src' sea importable
utilizando los mismos imports absolutos
que emplea la aplicación.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = str(ROOT / "src")

if SRC not in sys.path:
    sys.path.insert(
        0,
        SRC,
    )
