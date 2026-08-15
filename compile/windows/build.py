from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# ============================================================================
# Rutas
# ============================================================================

# build.py está en:
#   <raiz>/compile/windows/build.py
#
# Por tanto, la raíz del proyecto está dos niveles por encima.
ROOT_DIR = Path(__file__).resolve().parents[2]

ENTRY_POINT = ROOT_DIR / "src" / "main.py"
ICON = ROOT_DIR / "icon" / "icon.ico"

BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"

APP_NAME = "GeiMesDB"


# ============================================================================
# Paquetes que deben recogerse completamente
# ============================================================================

# Estas librerías necesitan --collect-all para que la conexión Oracle
# funcione correctamente en el ejecutable generado por PyInstaller.
COLLECT_ALL = [
    "cryptography",
    "cffi",
    "oracledb",
]


# ============================================================================
# Recursos de la aplicación
# ============================================================================

# Tupla:
#   (ruta relativa desde la raíz, ruta dentro del ejecutable)
DATA = [
    ("src/data", "data"),
    ("src/ui/resources", "ui/resources"),
    ("src/ui/styles", "ui/styles"),
    ("src/ui/translations", "ui/translations"),
]


# ============================================================================
# Validación
# ============================================================================


def check_required_paths() -> None:
    """Comprueba que existen los recursos necesarios para compilar."""

    required_files = [
        ENTRY_POINT,
        ICON,
    ]

    for path in required_files:
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo requerido: {path}")

    for source, _ in DATA:
        path = ROOT_DIR / source

        if not path.exists():
            raise FileNotFoundError(f"No se encontró el directorio de datos: {path}")


# ============================================================================
# Limpieza
# ============================================================================


def clean_previous_build() -> None:
    """Elimina los directorios de compilaciones anteriores."""

    for directory in (BUILD_DIR, DIST_DIR):
        if directory.exists():
            print(f"Eliminando: {directory}")
            shutil.rmtree(directory)


# ============================================================================
# Comando PyInstaller
# ============================================================================


def build_command() -> list[str]:
    """Construye los argumentos para PyInstaller."""

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        APP_NAME,
        "--onefile",
        "--clean",
        "--noconfirm",
        "--icon",
        str(ICON),
        "--paths",
        str(ROOT_DIR / "src"),
    ]

    # ------------------------------------------------------------------------
    # Paquetes que requieren recolección completa
    # ------------------------------------------------------------------------

    for package in COLLECT_ALL:
        command.extend(
            [
                "--collect-all",
                package,
            ]
        )

    # ------------------------------------------------------------------------
    # Recursos
    # ------------------------------------------------------------------------

    for source, destination in DATA:
        command.extend(
            [
                "--add-data",
                f"{ROOT_DIR / source};{destination}",
            ]
        )

    # ------------------------------------------------------------------------
    # Punto de entrada
    # ------------------------------------------------------------------------

    command.append(str(ENTRY_POINT))

    return command


# ============================================================================
# Información del entorno
# ============================================================================


def print_environment() -> None:
    """Muestra información sobre el entorno utilizado."""

    print()
    print("=" * 70)
    print("GeiMesDB - Compilación Windows")
    print("=" * 70)
    print()

    print(f"Raíz del proyecto: {ROOT_DIR}")
    print(f"Python:            {sys.version.split()[0]}")
    print(f"Python executable: {sys.executable}")
    print()

    print("Paquetes con --collect-all:")

    for package in COLLECT_ALL:
        print(f"  - {package}")

    print()


# ============================================================================
# Compilación
# ============================================================================


def main() -> int:
    print_environment()

    try:
        # Comprobar estructura del proyecto.
        check_required_paths()

        # Eliminar compilaciones anteriores.
        clean_previous_build()

        # Construir comando.
        command = build_command()

        print("Ejecutando PyInstaller...")
        print()

        # Mostrar el comando completo para facilitar la depuración.
        print("Comando PyInstaller:")
        print()
        print(" ".join(command))
        print()

        # Ejecutar PyInstaller desde la raíz del proyecto.
        result = subprocess.run(
            command,
            cwd=ROOT_DIR,
        )

        if result.returncode != 0:
            print()
            print("=" * 70)
            print("ERROR: la compilación ha fallado.")
            print("=" * 70)
            return result.returncode

        executable = DIST_DIR / f"{APP_NAME}.exe"

        print()
        print("=" * 70)
        print("COMPILACIÓN COMPLETADA")
        print("=" * 70)
        print()

        if executable.exists():
            size_mb = executable.stat().st_size / (1024 * 1024)

            print(f"Ejecutable: {executable}")
            print(f"Tamaño:     {size_mb:.2f} MB")
        else:
            print("ADVERTENCIA: no se encontró el ejecutable esperado:")
            print(f"  {executable}")

        print()

        return 0

    except FileNotFoundError as error:
        print()
        print(f"ERROR: {error}")
        return 1

    except KeyboardInterrupt:
        print()
        print()
        print("Compilación cancelada por el usuario.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
