#!/bin/bash

# Array para guardar carpetas a eliminar
dirs_a_eliminar=()

# Buscar carpetas __pycache__ recursivamente
while IFS= read -r dir; do
    dirs_a_eliminar+=("$dir")
done < <(find . -type d -name "__pycache__")

# Verificar si hay carpetas
if [ ${#dirs_a_eliminar[@]} -eq 0 ]; then
    echo "No se encontraron carpetas __pycache__."
    exit 0
fi

# Listar carpetas encontradas
echo "Se encontraron las siguientes carpetas __pycache__:"
for dir in "${dirs_a_eliminar[@]}"; do
    echo "  $dir"
done

# Confirmación
read -p "¿Deseas eliminarlas? (s/n): " confirmar
if [[ "$confirmar" =~ ^[Ss]$ ]]; then
    for dir in "${dirs_a_eliminar[@]}"; do
        rm -r "$dir"
    done
    echo "Carpetas eliminadas."
else
    echo "Operación cancelada."
fi