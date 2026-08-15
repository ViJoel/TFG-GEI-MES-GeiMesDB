"""
Configura el entorno de pruebas para que:
- 'src' sea importable mediante imports absolutos.
- 'tests' pueda utilizarse como paquete auxiliar.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SRC_PATH_STR = str(ROOT / "src")
ROOT_PATH_STR = str(ROOT)

for path in (ROOT_PATH_STR, SRC_PATH_STR):
    if path not in sys.path:
        sys.path.insert(
            0,
            path,
        )
