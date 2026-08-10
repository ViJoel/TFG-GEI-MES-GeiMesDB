# Comandos de pytest

```bash
pytest
```

**Ejecutar todos los tests:** Busca y ejecuta automáticamente todas las pruebas del proyecto (archivos que empiecen por `test_*.py` o terminen en `*_test.py`).

---

```bash
pytest -p no:warnings
```

**Desactivar todos los avisos:** Deshabilita completamente el plugin de captura de warnings de pytest, evitando que aparezcan advertencias de cualquier tipo en la consola.

---

```bash
pytest -W ignore::DeprecationWarning
```

**Ocultar solo avisos de depreciación:** Ignora específicamente los `DeprecationWarning` (funciones o librerías obsoletas) manteniendo activos los demás avisos.

---

```bash
pytest path/to/test/file.py
```

**Ejecutar un archivo específico:** Lanza únicamente los tests contenidos en el archivo indicado en la ruta.

---

```bash
pytest path/to/test/file.py::test_name
```

**Ejecutar una función de test específica:** Lanza únicamente el test individual `test_name` dentro del archivo especificado.
