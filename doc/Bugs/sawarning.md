# Warning conocido: SQLAlchemy no reconoce algunos tipos de datos del SGBD

## Índice

- [Warning conocido: SQLAlchemy no reconoce algunos tipos de datos del SGBD](#warning-conocido-sqlalchemy-no-reconoce-algunos-tipos-de-datos-del-sgbd)
  - [Índice](#índice)
  - [Descripción](#descripción)
  - [Entorno afectado](#entorno-afectado)
  - [Reproducción mínima](#reproducción-mínima)
  - [Comportamiento observado](#comportamiento-observado)
  - [Investigación realizada](#investigación-realizada)
  - [Impacto](#impacto)
  - [Estado](#estado)
  - [Solución actual](#solución-actual)

---

## Descripción

Durante la extracción del catálogo de la base de datos mediante el `Inspector`
de SQLAlchemy, algunos tipos de datos específicos del SGBD pueden no ser
reconocidos por el dialecto correspondiente.

En estos casos SQLAlchemy emite un warning similar al siguiente:

```text
SAWarning: Did not recognize type 'xml' of column 'metadatos_xml'
```

Como consecuencia, el tipo de la columna es representado internamente mediante
`NullType`.

---

## Entorno afectado

- SQLAlchemy 2.x
- PostgreSQL (al menos con el tipo `XML`)
- Potencialmente cualquier SGBD que disponga de tipos propios no soportados por
  el dialecto de SQLAlchemy.

---

## Reproducción mínima

Suponiendo una tabla como:

```sql
CREATE TABLE ejemplo (
    id INTEGER PRIMARY KEY,
    metadatos_xml XML
);
```

Al ejecutar:

```python
from sqlalchemy import inspect

inspector = inspect(engine)

columns = inspector.get_columns("ejemplo")
```

puede aparecer el warning:

```text
SAWarning: Did not recognize type 'xml' of column 'metadatos_xml'
```

---

## Comportamiento observado

Aunque el warning se muestra en consola, la extracción de columnas continúa con
normalidad.

Sin embargo, el campo:

```python
col["type"]
```

contiene un objeto `NullType` en lugar del tipo real de la columna.

Si se convierte directamente a texto:

```python
str(col["type"])
```

el resultado es:

```text
NULL
```

lo cual puede inducir a error, ya que no representa el tipo real de la columna,
sino únicamente que SQLAlchemy no ha podido identificarlo.

---

## Investigación realizada

Se comprobó que:

- La columna existe correctamente en la base de datos.
- El warning es emitido por SQLAlchemy durante la reflexión del esquema.
- La información restante de la columna (`nullable`, `default`, nombre, etc.)
  se obtiene correctamente.
- El problema únicamente afecta a la representación del tipo de dato.

El comportamiento corresponde a una limitación del dialecto de SQLAlchemy y no
a un error del código de la aplicación.

---

## Impacto

Muy bajo.

La construcción del catálogo continúa correctamente y únicamente se pierde la
representación textual del tipo de dato.

No afecta a:

- La navegación del árbol.
- El autocompletado.
- La detección de claves primarias.
- La detección de claves foráneas.
- La detección de índices.
- La extracción del resto del esquema.

---

## Estado

Conocido.

Puede aparecer con cualquier tipo de dato no soportado por el dialecto de
SQLAlchemy utilizado.

---

## Solución actual

Durante la construcción del catálogo se detectan los objetos `NullType`.

Cuando esto ocurre, el tipo almacenado en el modelo interno pasa a ser:

```text
UNKNOWN TYPE
```

en lugar de:

```text
NULL
```

De esta forma:

- El árbol refleja que el tipo no ha podido identificarse.
- Se evita mostrar un valor incorrecto al usuario.
- La aplicación continúa funcionando sin necesidad de implementar soporte
específico para cada tipo propietario de cada SGBD.
