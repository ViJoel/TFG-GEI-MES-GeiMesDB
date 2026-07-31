# Fallo de destrucción de widgets provocado por `QProxyStyle`

## Contexto

Durante la implementación del componente `NavigationTree`, basado en `QTreeView`, se introdujo una personalización visual mediante un estilo derivado de `QProxyStyle`:

```python
tree_view.setStyle(
    NoFocusStyle(
        tree_view.style(),
    )
)
```

El objetivo era eliminar el rectángulo de foco dibujado por Qt sobre el árbol.

La clase utilizada era:

```python
class NoFocusStyle(QProxyStyle):

    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PE_FrameFocusRect:
            return

        super().drawPrimitive(
            element,
            option,
            painter,
            widget,
        )
```

La personalización funcionaba visualmente, pero provocaba un fallo durante la destrucción dinámica del workspace que contenía el árbol.

---

## Causa raíz

El problema estaba relacionado con el modelo de ownership de `QProxyStyle`.

Según la documentación oficial de Qt, el constructor:

```cpp
QProxyStyle(QStyle *style = nullptr)
```

transfiere la propiedad del estilo recibido al objeto `QProxyStyle`. Es decir, el estilo base pasado como argumento deja de ser propiedad del widget original y pasa a estar gestionado por el proxy.

En este caso:

```python
NoFocusStyle(tree_view.style())
```

estaba pasando directamente el estilo interno que Qt había asignado al `QTreeView`.

La cadena resultante era conceptualmente:

```text
QTreeView
   |
   +-- NoFocusStyle (QProxyStyle)
          |
          +-- estilo original de Qt
```

El problema aparece porque el estilo original no era un objeto creado exclusivamente para ese proxy, sino un estilo compartido/gestionado por Qt.

Al destruir el widget:

```text
Workspace
   |
   +-- NavigationTree
          |
          +-- QTreeView
```

Qt iniciaba la limpieza de recursos internos. El `QProxyStyle` mantenía referencias al estilo base y podía provocar una destrucción incorrecta del objeto de estilo.

El resultado era un cierre abrupto desde la capa C++ de Qt, sin excepción Python ni traceback.

---

## Evidencia experimental

Se realizaron varias pruebas para aislar el problema:

| Prueba                                                                      | Resultado              |
| --------------------------------------------------------------------------- | ---------------------- |
| Sustituir `NavigationTree` por un `QWidget` vacío                           | Funciona               |
| Ejecutar `hide()` antes de eliminar                                         | Falla                  |
| `removeWidget()` del `QStackedWidget`                                       | Falla                  |
| Destruir modelos `QStandardItemModel` y `QSortFilterProxyModel` manualmente | Falla                  |
| Añadir logs en `hideEvent`, `closeEvent`, `__del__`                         | No llegan a ejecutarse |
| Eliminar `QProxyStyle`                                                      | Funciona               |

Esto permitió descartar:

* modelos del árbol,
* carga asíncrona,
* señales,
* eliminación del workspace,
* gestión de sesiones.

El fallo estaba localizado exclusivamente en la sustitución del estilo.

---

## Solución aplicada

Al tratarse únicamente de una modificación visual, se sustituyó la implementación basada en `QProxyStyle` por Qt Style Sheets:

```css
QTreeView:focus {
    outline: none;
}
```

Esta solución modifica únicamente la representación visual del widget y mantiene el sistema de estilos interno de Qt.

Ventajas:

* No altera ownership de objetos C++.
* No crea nuevos objetos `QStyle`.
* Mantiene el ciclo de vida estándar de Qt.
* Evita problemas de destrucción.

---

## Lección técnica

`QProxyStyle` no debe utilizarse como mecanismo general de personalización visual.

Debe reservarse para casos donde realmente sea necesario modificar el comportamiento de pintura o métricas de Qt.

Para cambios visuales:

| Necesidad                            | Solución recomendada |
| ------------------------------------ | -------------------- |
| Colores                              | QSS                  |
| Bordes                               | QSS                  |
| Estados hover/focus                  | QSS                  |
| Iconos                               | QSS / delegates      |
| Pintado complejo                     | `paintEvent()`       |
| Cambiar comportamiento interno de Qt | `QProxyStyle`        |

La documentación de Qt también indica que cuando se utiliza un estilo proxy específico para un widget debe crearse un estilo separado y gestionarse correctamente su ownership, en lugar de reutilizar directamente el estilo existente del widget.
