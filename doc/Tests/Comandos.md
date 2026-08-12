# Comandos de pytest

```bash
pytest
```

**Ejecutar todos los tests:** Busca y ejecuta automáticamente todas las pruebas del proyecto (archivos que empiecen por `test_*.py` o terminen en `*_test.py`).

---

```bash
pytest -vv
```

**Ejecutar todos los tests con información detallada:** Ejecuta todas las pruebas mostrando información más completa sobre cada test, incluyendo su ruta y nombre completo, así como el resultado individual (`PASSED`, `FAILED`, etc.).

---

```bash
pytest -p no:warnings
```

**Desactivar todos los avisos:** Deshabilita completamente el plugin de captura de warnings de pytest, evitando que aparezcan advertencias de cualquier tipo en la consola.

---

```bash
pytest -W ignore::DeprecationWarning
```

**Ocultar solo avisos de depreciación:** Ignora específicamente los `DeprecationWarning` (funciones o librerías obsoletas), manteniendo activos los demás avisos.

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

---

```bash
pytest path/to/test/file.py -vv
```

**Ejecutar un archivo específico con información detallada:** Ejecuta todos los tests del archivo indicado mostrando información detallada de cada prueba.

---

```bash
pytest path/to/test/file.py::test_name -vv
```

**Ejecutar un test específico con información detallada:** Ejecuta únicamente el test indicado y muestra información detallada sobre su ejecución.

---

## Comandos grandes para generar reporte de covertura

```bash
pytest --cov=src --cov-branch --cov-report=xml --cov-report=html tests
pytest --cov=src --cov-branch --cov-report=xml --cov-report=html -vv tests
pytest --cov=src --cov-branch --cov-report=xml --cov-report=html -vv -p no:warnings tests
```
