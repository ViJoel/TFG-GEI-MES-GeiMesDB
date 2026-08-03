# Desaparición aparente del editor al recargar el árbol

**Estado:** No reproducible actualmente.

## Descripción

Tras implementar la actualización automática del autocompletador cuando se recarga el árbol de navegación, se observó un comportamiento anómalo:

- El árbol se reconstruía correctamente.
- El esquema para el autocompletador (`SQL_SCHEMA_COMPLETION_DATA`) se actualizaba correctamente.
- El editor SQL activo parecía desaparecer del `QStackedWidget`.
- El editor no se cerraba realmente (`deleteLater()` no intervenía), pero dejaba de ser accesible desde la interfaz y tampoco era posible cerrarlo.

No se producía ninguna excepción.

---

## Flujo implicado

```text
NavigationTree
        │
        ├── Actualiza SQL_SCHEMA_COMPLETION_DATA
        ├── Emite tree_reloaded
        ▼
Workspace
        ▼
SqlEditorArea.force_update_editors_completers()
        ▼
SqlEditor.force_update_completer()
        ▼
SqlCompleter.update_document_completion(force_update=True)
        ▼
SqlCompleterModel.refresh()
        ▼
QStandardItemModel.clear()
appendRow(...)
```

La actualización forzada únicamente reconstruye el modelo del autocompletador.

No modifica:

- `SqlEditor`
- `QStackedWidget`
- `QStackedWidget.currentIndex()`
- Lista de archivos abiertos

---

## Comportamiento observado

Añadiendo únicamente los siguientes `print()` alrededor del bucle de actualización:

```python
print("count_before:", self.editors.count())
print("current_before:", self.editors.currentWidget())
print("index_before:", self.editors.currentIndex())

editor = self.editors.widget(i)
editor.force_update_completer()

print("count:", self.editors.count())
print("current:", self.editors.currentWidget())
print("index:", self.editors.currentIndex())
```

el problema desapareció completamente.

Posteriormente se eliminaron los `print()` y el bug siguió sin reproducirse.

No se realizó ninguna otra modificación en el código.

---

## Hipótesis

Todo apunta a un **Heisenbug** relacionado con Qt.

Posibles causas:

- Reentrada del event loop.
- Orden interno de procesamiento de señales.
- Actualización interna del `QCompleter` durante la reconstrucción del modelo.
- Algún estado temporal del popup del autocompletador.

No existen evidencias de un error lógico en el código del árbol ni del autocompletador.

---

## Información para futuras investigaciones

Si el problema vuelve a aparecer, comprobar inmediatamente:

```python
print(self.editors.count())
print(self.editors.currentIndex())
print(self.editors.currentWidget())

for i in range(self.editors.count()):
    print(i, self.editors.widget(i))
```

También verificar:

- si `tree_reloaded` se emite más de una vez;
- si `force_update_editors_completers()` se ejecuta más de una vez;
- si el popup del `QCompleter` está visible durante la actualización;
- si `QStackedWidget.currentIndex()` cambia inesperadamente;
- si el editor realmente desaparece del `QStackedWidget` o simplemente deja de ser el widget activo.

---

## Estado actual

El problema no ha vuelto a reproducirse.

La arquitectura actual se mantiene:

```text
NavigationTree
        │
        ├── Actualiza SQL_SCHEMA_COMPLETION_DATA
        ├── Emite tree_reloaded
        ▼
Workspace
        ▼
SqlEditorArea
        ▼
Todos los SqlEditor
        ▼
SqlCompleter
        ▼
SqlCompleterModel.refresh()
```

No se ha aplicado ninguna corrección específica, ya que el comportamiento desapareció sin cambios funcionales en el código. Se mantiene este documento como referencia en caso de que el bug vuelva a manifestarse.
