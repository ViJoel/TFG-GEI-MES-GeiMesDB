#!/bin/bash

# Carpeta objetivo (puedes cambiarla o pasarla como argumento)
DIRECTORIO="${1:-.}"

echo "Buscando archivos __init__.py en: $DIRECTORIO"

# Mostrar los archivos antes de borrarlos
find "$DIRECTORIO" -type f -name "__init__.py"

echo "¿Seguro que quieres eliminarlos? (s/n)"
read CONFIRMACION

if [[ "$CONFIRMACION" == "s" || "$CONFIRMACION" == "S" ]]; then
    find "$DIRECTORIO" -type f -name "__init__.py" -delete
    echo "Archivos eliminados."
else
    echo "Operación cancelada."
fi