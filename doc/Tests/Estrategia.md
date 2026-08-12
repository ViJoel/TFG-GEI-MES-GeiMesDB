# Estrategia de tests E2E para la interfaz Qt

## Índice

- [Estrategia de tests E2E para la interfaz Qt](#estrategia-de-tests-e2e-para-la-interfaz-qt)
  - [Índice](#índice)
  - [Contexto](#contexto)
  - [Problema detectado](#problema-detectado)
  - [Aislamiento del problema](#aislamiento-del-problema)
  - [El problema no es específico de un driver](#el-problema-no-es-específico-de-un-driver)
  - [Diferencia entre `keyClicks()` y `setText()`](#diferencia-entre-keyclicks-y-settext)
  - [Prueba realizada](#prueba-realizada)
  - [Decisión para los tests E2E](#decisión-para-los-tests-e2e)
  - [Ejemplo de E2E recomendado](#ejemplo-de-e2e-recomendado)
  - [¿Qué ocurre con las interacciones reales?](#qué-ocurre-con-las-interacciones-reales)
  - [Tests específicos de interacción](#tests-específicos-de-interacción)
  - [Criterio general](#criterio-general)
  - [Tests E2E funcionales](#tests-e2e-funcionales)
  - [Tests de interacción](#tests-de-interacción)
  - [Separación entre pruebas automatizadas y pruebas manuales](#separación-entre-pruebas-automatizadas-y-pruebas-manuales)
    - [Pruebas automatizadas](#pruebas-automatizadas)
    - [Pruebas manuales](#pruebas-manuales)
  - [Principio adoptado](#principio-adoptado)
  - [Conclusión](#conclusión)

## Contexto

El proyecto utiliza:

- **Python:** 3.12.12
- **Qt:** Qt Widgets
- **Framework GUI:** PySide6
- **Persistencia:** SQLAlchemy
- **Base de datos de la aplicación:** SQLite embebida
- **Tests:** pytest
- **Tests Qt:** pytest-qt
- **Tipo de pruebas:** E2E (End-to-End)

Los tests E2E se utilizan principalmente para comprobar que los flujos completos de la aplicación funcionan correctamente, desde la interacción con la interfaz hasta el resultado final en la aplicación y en la base de datos.

---

## Problema detectado

Durante el desarrollo de los tests E2E para la creación de conexiones se detectó un comportamiento inconsistente.

Los tests funcionaban correctamente cuando se ejecutaban individualmente, pero algunos fallaban cuando se ejecutaban conjuntamente.

El problema se observó al utilizar `pytest-qt` para simular las interacciones del usuario con los widgets de Qt.

Inicialmente, los formularios se rellenaban simulando la escritura real del usuario mediante `qtbot.keyClicks()` y los botones se accionaban mediante `qtbot.mouseClick()`.

Por ejemplo:

```python
qtbot.keyClicks(
    form.name_input,
    "PostgreSQL connection",
)

form.driver_input.setCurrentText(
    Driver.POSTGRESQL.value,
)

qtbot.keyClicks(
    form.host_input,
    "localhost",
)

qtbot.keyClicks(
    form.port_input,
    "5432",
)

qtbot.keyClicks(
    form.database_input,
    "postgres",
)

qtbot.keyClicks(
    form.username_input,
    "postgres",
)

qtbot.keyClicks(
    form.password_input,
    "postgres",
)

qtbot.mouseClick(
    form.save_button,
    Qt.MouseButton.LeftButton,
)
```

En determinadas circunstancias, al ejecutar los tests conjuntamente, el flujo no llegaba a crear la conexión.

El resultado era:

```text
assert len(connections) == 1

E       assert 0 == 1
E        +  where 0 = len([])
```

---

## Aislamiento del problema

Antes de modificar los tests se comprobó que el problema no estuviera provocado por datos compartidos entre tests.

La aplicación utiliza una **base de datos SQLite embebida**, que es la propia base de datos de la aplicación donde se almacenan las conexiones.

En el entorno de tests, cada test genera su propia instancia de esta base de datos SQLite embebida.

Por tanto, cada test comienza con su propio estado de persistencia y no reutiliza las conexiones creadas por otros tests.

Además, el estado inicial podía comprobarse mediante:

```python
connections = get_all_connections()

assert len(connections) == 0
```

Cuando el test fallaba, la base de datos comenzaba vacía.

Por tanto, se descartó que el problema estuviera provocado por:

- una conexión creada por un test anterior;
- datos persistentes entre tests;
- reutilización de la base de datos de otro test;
- contaminación de los datos;
- una sesión de SQLAlchemy compartida incorrectamente.

El problema estaba relacionado con el procesamiento de las interacciones de Qt.

---

## El problema no es específico de un driver

Durante la investigación se comprobó el comportamiento con diferentes drivers de conexión.

El problema no debe considerarse un problema específico de PostgreSQL.

La diferencia relevante está en **la forma en que se introducen los datos en los widgets** y en cómo Qt procesa esas interacciones.

El caso de PostgreSQL permitió detectar el problema porque el test original utilizaba intensivamente `qtbot.keyClicks()`.

Al modificar el test para establecer directamente los valores de los widgets, el flujo pasó a ejecutarse de forma consistente.

El mismo criterio puede aplicarse a los tests de otros drivers, como SQLite o MySQL.

Por tanto, la decisión no es:

> "Los tests de PostgreSQL deben utilizar `setText()`."

La decisión es:

> "Los tests E2E funcionales deben utilizar preferentemente operaciones directas sobre los widgets y no depender de la simulación detallada de eventos de teclado y ratón."

---

## Diferencia entre `keyClicks()` y `setText()`

Algunos campos de la interfaz utilizan mecanismos de validación, como regex o validadores de Qt.

Esto hace que:

```python
qtbot.keyClicks(
    form.port_input,
    "5432",
)
```

no sea equivalente desde el punto de vista del procesamiento de eventos a:

```python
form.port_input.setText("5432")
```

Con `keyClicks()`, Qt procesa una secuencia de eventos equivalente a:

```text
"5"
"54"
"543"
"5432"
```

El validador y las señales asociadas al `QLineEdit` pueden intervenir durante cada modificación.

En cambio:

```python
form.port_input.setText("5432")
```

establece directamente el valor del widget.

Por tanto, `keyClicks()` introduce en el test el comportamiento del event loop y del procesamiento de eventos de teclado de Qt, mientras que `setText()` se centra en el estado que necesita el flujo.

---

## Prueba realizada

Se modificó el test para rellenar directamente los widgets:

```python
form.name_input.setText("PostgreSQL connection")
form.driver_input.setCurrentText(Driver.POSTGRESQL.value)
form.host_input.setText("localhost")
form.port_input.setText("5432")
form.database_input.setText("postgres")
form.username_input.setText("postgres")
form.password_input.setText("postgres")

form.save_button.click()
```

Con esta implementación el test pasa de forma consistente, incluso ejecutando la suite completa.

Esto demuestra que la forma de interactuar con los widgets tiene un impacto en la estabilidad de los tests.

No se está modificando el flujo funcional de la aplicación: se están modificando únicamente las operaciones utilizadas por el test para establecer el estado inicial del formulario.

---

## Decisión para los tests E2E

Los tests E2E estarán orientados principalmente a comprobar **flujos funcionales completos**.

El objetivo de un test como:

```python
test_create_postgresql_connection_success
```

es comprobar:

> Dado un formulario con los datos necesarios para crear una conexión, al guardar se crea correctamente la conexión y la interfaz refleja el nuevo estado.

El objetivo no es comprobar:

> Que pytest-qt puede simular correctamente que un usuario escribe carácter por carácter en cada campo.

Por este motivo, en los E2E funcionales se utilizará preferentemente:

```python
setText()
setCurrentText()
setValue()
click()
```

en lugar de:

```python
keyClicks()
mouseClick()
```

cuando no sea necesario comprobar específicamente la interacción física con el widget.

---

## Ejemplo de E2E recomendado

Un test de creación de conexión puede quedar así:

```python
def test_create_postgresql_connection_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que se crea correctamente una conexión PostgreSQL válida.
    """

    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.name_input.setText(
        "PostgreSQL connection",
    )

    form.driver_input.setCurrentText(
        Driver.POSTGRESQL.value,
    )

    form.host_input.setText(
        "localhost",
    )

    form.port_input.setText(
        "5432",
    )

    form.database_input.setText(
        "postgres",
    )

    form.username_input.setText(
        "postgres",
    )

    form.password_input.setText(
        "postgres",
    )

    form.save_button.click()

    connections = get_all_connections()

    assert len(connections) == 1

    connection = connections[0]

    assert connection.name == "PostgreSQL connection"
    assert connection.driver == Driver.POSTGRESQL
    assert connection.host == "localhost"
    assert connection.port == 5432
    assert connection.database == "postgres"
    assert connection.username == "postgres"
    assert connection.password == "postgres"

    assert main_window.stack.currentWidget() is main_window.home_page

    assert (
        main_window.sidebar.connections_list.list_widget.count()
        == 1
    )
```

Este test comprueba el flujo completo:

```text
Abrir formulario
      ↓
Seleccionar driver
      ↓
Establecer los datos
      ↓
Guardar
      ↓
Persistir conexión en la BD SQLite embebida
      ↓
Volver a Home
      ↓
Mostrar conexión en la interfaz
```

---

## ¿Qué ocurre con las interacciones reales?

Las interacciones como:

- hacer clic;
- escribir con el teclado;
- recibir el foco;
- validar cada carácter;
- reaccionar a señales;
- cambiar dinámicamente los campos;
- utilizar atajos de teclado;

siguen siendo importantes.

Sin embargo, no es necesario que todos los tests E2E reproduzcan estas acciones carácter por carácter.

La interfaz debe comprobarse manualmente durante las pruebas de aceptación y validación de la aplicación.

Por ejemplo, manualmente se puede comprobar que:

1. El usuario puede entrar en el formulario.
2. Puede seleccionar el driver correspondiente.
3. Puede escribir un nombre.
4. Puede introducir los datos de conexión.
5. Puede introducir un puerto válido.
6. El campo rechaza caracteres no permitidos.
7. Puede completar el resto de campos.
8. Puede guardar la conexión.
9. La aplicación muestra correctamente el resultado.

Esto permite comprobar la experiencia real del usuario sin convertir todos los tests automatizados en simulaciones detalladas de eventos de teclado y ratón.

---

## Tests específicos de interacción

Si en algún momento se considera necesario automatizar el comportamiento de un widget concreto, se puede crear un test específico para ello.

Por ejemplo, para comprobar el validador de un puerto:

```python
def test_port_rejects_invalid_characters(
    qtbot: QtBot,
    main_window: MainWindow,
):
    form = _open_connection_form(
        qtbot,
        main_window,
    )

    form.driver_input.setCurrentText(
        Driver.POSTGRESQL.value,
    )

    qtbot.keyClicks(
        form.port_input,
        "abc",
    )

    assert form.port_input.text() == ""
```

Este test sí tiene sentido utilizando `keyClicks()`, porque en este caso el objetivo concreto es comprobar el comportamiento del `QLineEdit` y su validador ante una entrada de teclado.

La diferencia fundamental es que este test no pretende comprobar todo el flujo de creación de una conexión.

---

## Criterio general

La estrategia será:

## Tests E2E funcionales

Utilizar preferentemente:

```python
setText()
setCurrentText()
setValue()
click()
```

Objetivo:

> Comprobar que un flujo completo de la aplicación funciona correctamente.

Ejemplos:

- crear una conexión;
- editar una conexión;
- eliminar una conexión;
- cambiar de página;
- guardar una configuración;
- cargar datos;
- comprobar el resultado persistido.

---

## Tests de interacción

Utilizar cuando sea necesario:

```python
keyClicks()
mouseClick()
setFocus()
```

Objetivo:

> Comprobar específicamente el comportamiento de la interfaz ante acciones del usuario.

Ejemplos:

- validación de campos;
- restricciones de entrada;
- comportamiento del teclado;
- señales producidas por cambios;
- foco;
- comportamiento de botones;
- interacción específica entre widgets.

Estos tests no tienen que formar parte necesariamente de todos los flujos E2E.

---

## Separación entre pruebas automatizadas y pruebas manuales

La estrategia distingue claramente dos objetivos.

### Pruebas automatizadas

Comprueban principalmente:

```text
¿El flujo funcional funciona correctamente?
```

Por ejemplo:

```text
Datos válidos
    ↓
Guardar
    ↓
Conexión creada
    ↓
Datos persistidos
    ↓
Interfaz actualizada
```

### Pruebas manuales

Comprueban principalmente:

```text
¿El usuario puede utilizar correctamente la interfaz?
```

Por ejemplo:

```text
Click
  ↓
Foco
  ↓
Escritura
  ↓
Validación
  ↓
Cambio de campos
  ↓
Feedback visual
```

No es necesario que ambas pruebas reproduzcan exactamente las mismas acciones.

---

## Principio adoptado

La suite E2E debe priorizar la **estabilidad y la comprobación del comportamiento funcional de la aplicación**.

No se considera necesario reproducir artificialmente cada acción física que realizaría un usuario si esa interacción no es el objetivo específico del test.

Por tanto:

```text
                  TEST E2E
                     │
                     ▼
          ¿Qué comportamiento quiero
                 comprobar?
                     │
             ┌───────┴────────┐
             │                │
             ▼                ▼
       Flujo funcional    Interacción UI
             │                │
             ▼                ▼
        setText()         keyClicks()
        setValue()        mouseClick()
        click()           setFocus()
             │                │
             ▼                ▼
       Resultado del      Comportamiento
          flujo             del widget
```

La finalidad es evitar que los tests E2E fallen por detalles relacionados con la simulación de eventos de Qt cuando esos eventos no forman parte del comportamiento que realmente se pretende verificar.

---

## Conclusión

El fallo encontrado durante los tests de creación de conexiones no estaba relacionado con un driver concreto ni con el estado de la base de datos.

Cada test dispone de su propia instancia de la **base de datos SQLite embebida de la aplicación**, utilizada para almacenar las conexiones, por lo que los datos generados por un test no se reutilizan entre tests.

El problema estaba relacionado con la forma de simular determinadas interacciones con Qt mediante `pytest-qt`, especialmente mediante `keyClicks()` sobre campos que tienen validación.

La solución adoptada es utilizar manipulación directa de los widgets en los E2E funcionales:

```python
form.name_input.setText(...)
form.driver_input.setCurrentText(...)
form.port_input.setText(...)
form.save_button.click()
```

y reservar la simulación detallada de teclado, ratón y foco para pruebas específicas de interacción cuando sea necesario.

De esta forma se obtiene una suite E2E más:

- **estable**;
- **determinista**;
- **rápida de ejecutar**;
- **centrada en los flujos funcionales**;
- **menos dependiente de detalles internos del procesamiento de eventos de Qt**.

La interfaz seguirá siendo validada manualmente para garantizar que el usuario puede utilizar correctamente la aplicación.

El objetivo de los E2E automatizados será principalmente comprobar que **los flujos de la aplicación funcionan correctamente de principio a fin**.
