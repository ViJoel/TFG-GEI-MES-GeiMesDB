# Warning conocido: warnings de `qt.accessibility.atspi` al mostrar el popup de autocompletado

## Índice

- [Warning conocido: warnings de `qt.accessibility.atspi` al mostrar el popup de autocompletado](#warning-conocido-warnings-de-qtaccessibilityatspi-al-mostrar-el-popup-de-autocompletado)
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

En determinados entornos Linux, Qt puede emitir mensajes de advertencia procedentes del backend de accesibilidad **AT-SPI** cuando se muestra un popup que es creado y destruido rápidamente.

En el editor, este comportamiento ocurre con el popup de autocompletado.

Los mensajes observados son similares a:

```text
qt.accessibility.atspi: Could not find accessible on path: "/org/a11y/atspi/accessible/2147483905"
qt.accessibility.atspi: Could not find accessible on path: "/org/a11y/atspi/accessible/2147483906"
qt.accessibility.atspi: Could not find accessible on path: "/org/a11y/atspi/accessible/2147483908"
```

---

## Entorno afectado

- Sistema operativo: Linux Mint Cinnamon
- PySide6: 6.11.0
- Qt: 6.11.0

---

## Reproducción mínima

1. Abrir el editor.
2. Escribir texto hasta que aparezca el popup de autocompletado.
3. Continuar escribiendo de forma que el popup se actualice, cierre o vuelva a abrirse rápidamente.
4. Observar la salida de la terminal.

---

## Comportamiento observado

Durante la creación y destrucción del popup aparecen mensajes como:

```text
qt.accessibility.atspi: Could not find accessible on path: "/org/a11y/atspi/accessible/2147483905"
qt.accessibility.atspi: Could not find accessible on path: "/org/a11y/atspi/accessible/2147483906"
qt.accessibility.atspi: Could not find accessible on path: "/org/a11y/atspi/accessible/2147483908"
```

Los identificadores del objeto accesible cambian entre ejecuciones.

---

## Investigación realizada

Se comprobó que:

- El popup de autocompletado se crea y destruye correctamente.
- No se producen excepciones ni errores en el código Python.
- El comportamiento funcional del autocompletado es correcto.
- El warning únicamente aparece cuando el widget es destruido poco después de ser creado.

Todo apunta a que el backend de accesibilidad **AT-SPI** intenta acceder a un objeto accesible que ya ha sido destruido antes de completar la sincronización con el árbol de accesibilidad.

No se han encontrado indicios de un uso incorrecto de la API pública de PySide6.

---

## Impacto

Ninguno.

Las siguientes funcionalidades continúan funcionando correctamente:

- Apertura del popup de autocompletado.
- Actualización de sugerencias.
- Navegación mediante teclado.
- Selección de elementos.
- Inserción del texto seleccionado.

Los mensajes son únicamente warnings emitidos por la infraestructura de accesibilidad de Qt.

---

## Estado

Pendiente de verificar en versiones posteriores de PySide6 / Qt.

Todo indica que se trata de una condición de carrera interna entre la destrucción del widget y la actualización del árbol de accesibilidad AT-SPI.

---

## Solución actual

Ninguna.

No se han detectado problemas funcionales derivados de estos warnings.

Mientras no afecten al comportamiento del editor, pueden considerarse un problema interno del backend de accesibilidad de Qt/PySide6 y ser ignorados.
