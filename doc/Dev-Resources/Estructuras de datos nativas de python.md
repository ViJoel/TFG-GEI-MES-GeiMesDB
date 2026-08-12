# Apuntes completos de las 4 estructuras de datos nativas en Python

---

## 1. Listas (`list`)

Son colecciones ordenadas, mutables (modificables) y permiten elementos duplicados.

- **Cómo se crean:** Con corchetes `[]` o la función `list()`.

```python
frutas = ["manzana", "pera", "mango"]
vacia = []

```

- **Cómo se accede a los valores:** Mediante su índice (posición), empezando desde `0`. Soporta índices negativos (el `-1` es el último).

```python
print(frutas[0])   # "manzana"
print(frutas[-1])  # "mango"
```

- **Cómo se manipulan:**

```python
frutas.append("naranja")  # Añade al final -> ["manzana", "pera", "mango", "naranja"]
frutas.insert(1, "uva")   # Añade en una posición -> ["manzana", "uva", "pera", "mango", "naranja"]
frutas.remove("pera")     # Elimina por valor
frutas[0] = "plátano"     # Modifica un elemento directo
```

---

## 2. Tuplas (`tuple`)

Son colecciones ordenadas pero **inmutables** (no se pueden modificar, añadir ni eliminar elementos una vez creadas).

- **Cómo se crean:** Con paréntesis `()` o la función `tuple()`. *Ojo: si es de un solo elemento, lleva una coma al final `(elem,)`.*

```python
coordenadas = (40.71, -74.00)
un_solo_elemento = (5,)
vacia = ()
```

- **Cómo se accede a los valores:** Igual que las listas, por su índice.

```python
print(coordenadas[0])  # 40.71
```

- **Cómo se manipulan:** **No se pueden manipular.** Si intentas hacer `coordenadas[0] = 10.5` o usar un `.append()`, Python te dará un error (`TypeError`). Para cambiarlas, tendrías que transformarla en lista, modificarla y volverla a hacer tupla.

---

## 3. Diccionarios (`dict`)

Colecciones de pares **clave-valor**. Las claves deben ser únicas e inmutables (cadenas, números o tuplas), pero los valores pueden ser cualquier cosa.

- **Cómo se crean:** Con llaves `{}` y dos puntos `:` para separar clave de valor.

```python
usuario = {"nombre": "Elena", "edad": 28}
vacit = {}  # Recuerda que las llaves vacías crean un dict por defecto
```

- **Cómo se accede a los valores:** Usando la clave entre corchetes, o el método `.get()` (este último no rompe el programa si la clave no existe).

```python
print(usuario["nombre"])       # "Elena"
print(usuario.get("ciudad"))   # Devuelve None (no da error)
```

- **Cómo se manipulan:**

```python
usuario["ciudad"] = "Madrid"   # Añade una nueva clave-valor
usuario["edad"] = 29           # Modifica un valor existente
del usuario["nombre"]          # Elimina la clave "nombre"
```

---

## 4. Conjuntos (`set`)

Colecciones desordenadas de elementos **únicos**. No permite duplicados.

- **Cómo se crean:** Con llaves `{}` (con elementos dentro) o la función `set()` (obligatoria si lo quieres crear vacío).

```python
numeros = {1, 2, 3, 3, 4}  # Al guardarse será {1, 2, 3, 4}
vacio = set()              # Conjunto vacío
```

- **Cómo se accede a los valores:** No tienen orden ni índices, por lo que **no puedes usar `[0]**`. Solo puedes verificar si un elemento existe o recorrerlos con un bucle.

```python
print(2 in numeros)  # Devuelve True
```

- **Cómo se manipulan:**

```python
numeros.add(5)       # Añade un elemento
numeros.remove(2)    # Elimina un elemento (da error si no existe)
numeros.discard(9)   # Elimina un elemento (NO da error si no existe)
```

---

### Resumen rápido de trucos ("Etc.")

- **Saber cuántos elementos hay:** Usa la función `len(estructura)` en cualquiera de las cuatro.
- **Saber si un elemento existe:** Usa la palabra clave `in` (ej: `"manzana" in frutas`). En diccionarios, busca en las *claves*.
- **Conversiones de emergencia:** Puedes transformar una estructura en otra fácilmente: `list(tupla)`, `set(lista)` (ideal para borrar duplicados rápido), `tuple(lista)`.
