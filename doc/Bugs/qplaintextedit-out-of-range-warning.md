# Bug conocido: warnings espurios de `QTextCursor::setPosition()` en `QPlainTextEdit`

## Índice

- [Bug conocido: warnings espurios de `QTextCursor::setPosition()` en `QPlainTextEdit`](#bug-conocido-warnings-espurios-de-qtextcursorsetposition-en-qplaintextedit)
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

En determinados entornos Linux, `QPlainTextEdit` genera mensajes de advertencia en la terminal mientras se escribe texto o cuando el cursor se encuentra al final del documento:

```text
QTextCursor::setPosition: Position '1' out of range
QTextCursor::setPosition: Position '2' out of range
QTextCursor::setPosition: Position '3' out of range
...
```

El warning aparece incluso utilizando un `QPlainTextEdit` vacío sin ninguna personalización.

---

## Entorno afectado

- Sistema operativo: Linux Mint Cinnamon
- PySide6: 6.11.0
- Qt: 6.11.0

---

## Reproducción mínima

```python
from PySide6.QtWidgets import QApplication, QPlainTextEdit

app = QApplication([])

editor = QPlainTextEdit()
editor.show()

app.exec()
```

1. Escribir texto:

   ```text
   1234
   ```

2. Mantener el cursor al final del documento.

3. Observar los warnings en la terminal.

---

## Comportamiento observado

Al escribir:

```text
1
12
123
1234
```

aparecen mensajes como:

```text
QTextCursor::setPosition: Position '1' out of range
QTextCursor::setPosition: Position '2' out of range
QTextCursor::setPosition: Position '3' out of range
QTextCursor::setPosition: Position '4' out of range
QTextCursor::setPosition: Position '5' out of range
```

Los warnings desaparecen cuando el cursor deja de estar situado al final del documento.

---

## Investigación realizada

Se verificó que el cursor expuesto por la API pública de `QPlainTextEdit` siempre permanece en posiciones válidas:

```python
cursor = self.textCursor()

print(
    f"text='{self.toPlainText()}' "
    f"len={len(self.toPlainText())} "
    f"pos={cursor.position()} "
    f"anchor={cursor.anchor()}"
)
```

Ejemplo:

```text
text='1234' len=4 pos=4 anchor=4
```

Por tanto:

- El cursor principal del editor es válido.
- El warning es generado por un cursor interno de Qt.
- No se detectaron errores funcionales en el widget.

---

## Impacto

Ninguno.

Las siguientes funcionalidades operan correctamente:

- Escritura de texto.
- Edición multilínea.
- Movimiento del cursor.
- Selección de texto.
- Copiar y pegar.
- Undo / Redo.

Los warnings son únicamente mensajes de consola.

---

## Estado

Pendiente de verificar en versiones posteriores de PySide6 / Qt.

---

## Solución actual

Ninguna.

Se considera un problema interno de Qt/PySide6 y puede ignorarse mientras no afecte al funcionamiento del editor.
