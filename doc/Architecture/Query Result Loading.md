# Limitación conocida: carga completa de resultados en memoria

## Índice

- [Limitación conocida: carga completa de resultados en memoria](#limitación-conocida-carga-completa-de-resultados-en-memoria)
  - [Índice](#índice)
  - [Descripción del problema](#descripción-del-problema)
  - [Problemas derivados](#problemas-derivados)
  - [Alternativa técnica](#alternativa-técnica)
  - [Implicaciones arquitectónicas](#implicaciones-arquitectónicas)
  - [Justificación de la decisión adoptada](#justificación-de-la-decisión-adoptada)
  - [Simplicidad arquitectónica](#simplicidad-arquitectónica)
  - [Ámbito del proyecto](#ámbito-del-proyecto)
  - [Experiencia de usuario](#experiencia-de-usuario)
  - [Relación coste-beneficio](#relación-coste-beneficio)
  - [Trabajo futuro](#trabajo-futuro)
  - [Justificación basada en el patrón de uso y el caso de uso](#justificación-basada-en-el-patrón-de-uso-y-el-caso-de-uso)

## Descripción del problema

Actualmente el backend de ejecución de consultas recupera la totalidad del conjunto de resultados mediante la llamada a `CursorResult.fetchall()`. Posteriormente, todas las filas son almacenadas en memoria dentro del objeto `ResultSet`, que es utilizado por la interfaz para representar los datos en un `QTableView`.

El flujo actual puede resumirse de la siguiente forma:

```text
Usuario ejecuta una consulta
            │
            ▼
SQLAlchemy ejecuta la consulta
            │
            ▼
CursorResult.fetchall()
            │
            ▼
Todas las filas se cargan en memoria
            │
            ▼
Creación del ResultSet
            │
            ▼
Visualización en el QTableView
```

Este enfoque simplifica la arquitectura del proyecto, ya que el resultado de una consulta queda completamente desacoplado de la conexión utilizada para ejecutarla. Una vez construido el `ResultSet`, la conexión puede cerrarse inmediatamente y la interfaz trabaja únicamente con estructuras de datos en memoria.

---

## Problemas derivados

La principal limitación aparece cuando una consulta devuelve un volumen elevado de registros.

Por ejemplo, una consulta como:

```sql
SELECT * FROM tabla_grande;
```

puede devolver cientos de miles o incluso millones de filas.

En este escenario:

- todas las filas son almacenadas simultáneamente en memoria;
- el tiempo necesario para construir el `ResultSet` aumenta considerablemente;
- el consumo de memoria crece de forma proporcional al número de registros devueltos.

Además, el proyecto genera una representación textual completa del conjunto de resultados para la consola de salida. Esto implica recorrer nuevamente todas las filas y construir una cadena de gran tamaño, incrementando todavía más el consumo de memoria y el tiempo de procesamiento.

En consecuencia, el diseño actual no resulta adecuado para conjuntos de datos muy grandes.

---

## Alternativa técnica

Qt proporciona un mecanismo específico para este tipo de situaciones mediante los métodos:

- `QAbstractItemModel.canFetchMore()`
- `QAbstractItemModel.fetchMore()`

La idea consiste en que el modelo vaya solicitando nuevas filas únicamente cuando el usuario se aproxima al final de la tabla.

Para que esta estrategia funcione es necesario que el resultado SQL permanezca abierto mientras exista la vista.

En lugar de ejecutar:

```python
rows = result.fetchall()
```

el modelo iría realizando llamadas sucesivas similares a:

```python
rows = result.fetchmany(100)
```

obteniendo únicamente pequeños bloques de registros.

De esta forma el consumo de memoria permanece prácticamente constante independientemente del tamaño total del resultado.

---

## Implicaciones arquitectónicas

Aunque el cambio pueda parecer sencillo, realmente implica un rediseño importante del backend.

Actualmente el ciclo de vida de una consulta es:

```text
Conexión
    │
    ▼
Ejecución SQL
    │
    ▼
fetchall()
    │
    ▼
ResultSet
    │
    ▼
Cierre de la conexión
```

Con carga incremental sería necesario mantener viva la conexión mientras el usuario continúe navegando por el resultado:

```text
Conexión abierta
        │
        ▼
CursorResult
        │
        ├── fetchMore()
        ├── fetchMore()
        ├── fetchMore()
        ▼
QTableView
```

Esto obliga a introducir nuevos componentes de ejecución en tiempo real, responsables de:

- Mantener el `CursorResult` abierto;
- Conservar la conexión asociada;
- Suministrar bloques de filas bajo demanda;
- Liberar correctamente los recursos cuando el usuario cierre la pestaña del resultado.

En consecuencia, el modelo actual basado en un `ResultSet` completamente materializado dejaría de ser válido.

---

## Justificación de la decisión adoptada

Durante el desarrollo del proyecto se decidió mantener la estrategia de carga completa de resultados por los siguientes motivos.

## Simplicidad arquitectónica

El diseño actual desacopla completamente la interfaz gráfica de la conexión a la base de datos.

Una vez construido el `ResultSet`, la conexión puede cerrarse inmediatamente, evitando tener cursores o conexiones persistentes asociados a cada pestaña de resultados.

Esta aproximación reduce considerablemente la complejidad del backend.

## Ámbito del proyecto

La aplicación está orientada principalmente a tareas de desarrollo, administración y aprendizaje sobre bases de datos.

El uso previsto consiste en ejecutar consultas de validación, pruebas o mantenimiento sobre bases de datos de tamaño reducido o moderado.

No constituye un visor especializado para explotación de grandes volúmenes de información.

## Experiencia de usuario

Las consultas SQL se ejecutan en un hilo de trabajo independiente de la interfaz gráfica.

Como consecuencia, incluso cuando una consulta tarda varios segundos en completarse, la aplicación permanece completamente interactiva y no bloquea la interfaz del usuario.

## Relación coste-beneficio

La implementación de una carga incremental requeriría modificar una parte importante de la arquitectura existente:

- Rediseño del ciclo de vida de las consultas;
- Gestión de cursores persistentes;
- Mantenimiento de conexiones abiertas por resultado;
- Modificación del modelo de datos utilizado por la interfaz;
- Rediseño de la salida textual de resultados.

Dado el alcance temporal del Trabajo Fin de Grado y el perfil de uso esperado de la aplicación, el beneficio obtenido no compensa el esfuerzo de implementación y validación requerido.

Por este motivo se ha considerado una mejora futura y no un requisito funcional del proyecto.

---

## Trabajo futuro

Como línea de mejora se propone implementar un sistema de carga incremental de resultados basado en `CursorResult.fetchmany()` y en los mecanismos `canFetchMore()` y `fetchMore()` proporcionados por Qt.

Esta solución permitiría:

- Reducir significativamente el consumo de memoria;
- Visualizar tablas de millones de registros;
- Mejorar la escalabilidad de la aplicación;
- Mantener una experiencia de usuario fluida independientemente del tamaño del conjunto de resultados.

No obstante, esta mejora requiere un rediseño de la arquitectura de ejecución de consultas y de la gestión del ciclo de vida de las conexiones, por lo que queda fuera del alcance del presente Trabajo Fin de Grado.

## Justificación basada en el patrón de uso y el caso de uso

Otro aspecto que justifica la decisión adoptada es el patrón de utilización esperado de la aplicación.

La finalidad principal de la aplicación es permitir al usuario inspeccionar de forma interactiva el resultado de consultas SQL. En este contexto, resulta poco habitual ejecutar deliberadamente una consulta como:

```sql
SELECT * FROM tabla_grande;
```

sobre una tabla que contiene millones de registros con el objetivo de revisar visualmente todo su contenido.

La inspección manual de un conjunto de datos de esa magnitud no constituye una práctica habitual, ya que ningún usuario puede analizar millones de filas navegando por una tabla. Cuando una tabla alcanza un volumen elevado de información, el usuario normalmente conoce su tamaño y formula consultas más específicas utilizando cláusulas como `WHERE`, `ORDER BY` o `LIMIT`, reduciendo el conjunto de resultados a un número de filas que pueda inspeccionarse de forma razonable y que contenga únicamente la información relevante para la tarea que desea realizar.

Por este motivo, el escenario en el que un usuario ejecuta un `SELECT *` sobre una tabla de gran tamaño con la intención de visualizar íntegramente su contenido en la aplicación se considera un caso de uso excepcional y con escasa utilidad práctica. La visualización completa de millones de registros en un componente gráfico como `QTableView` no aporta un beneficio real al usuario, ya que el volumen de información excede ampliamente la capacidad de inspección manual.

En aquellos escenarios donde sí resulta necesario recuperar la totalidad de los registros de una tabla, el objetivo suele ser distinto al de una inspección visual interactiva. Habitualmente se trata de procesos de exportación de datos, integración entre sistemas (ETL), generación de informes o análisis automatizados, casos de uso que normalmente emplean herramientas o procesos específicos y no una interfaz gráfica diseñada para explorar resultados de consultas.

Por tanto, aunque la carga completa del conjunto de resultados representa una limitación conocida desde el punto de vista de la escalabilidad, su impacto práctico sobre el caso de uso previsto para la aplicación se considera reducido. En consecuencia, se ha priorizado una arquitectura más sencilla y desacoplada basada en la carga completa de resultados, identificando la incorporación de un sistema de carga incremental como una mejora futura orientada a escenarios donde la exploración de grandes volúmenes de datos constituya un requisito funcional.
