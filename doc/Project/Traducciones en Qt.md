# Traducciones en Qt

GeiMesDB utiliza el sistema de internacionalización de **Qt** mediante `QObject.tr()` para marcar los textos traducibles.

## Generar el archivo de traducciones

El comando `pyside6-lupdate` analiza el código fuente y extrae todas las cadenas marcadas con `tr()` hacia un archivo `.ts`.

> **Importante:** En proyectos Python es necesario indicar la extensión de los archivos mediante `-extensions py`. De lo contrario, `lupdate` solo buscará archivos C++ y no encontrará ninguna cadena.

### Ejemplo incorrecto

```bash
(venv) usuario$ pyside6-lupdate src -ts src/ui/translations/geimesdb_es.ts

Scanning directory 'src'...
Updating 'src/ui/translations/geimesdb_es.ts'...
    Found 0 source text(s) (0 new and 0 already existing)
```

No se detectó ninguna cadena traducible porque `lupdate` no analiza archivos Python por defecto.

### Ejemplo correcto

```bash
(venv) usuario$ pyside6-lupdate -extensions py src -ts src/ui/translations/geimesdb_es.ts

Scanning directory 'src'...
Updating 'src/ui/translations/geimesdb_es.ts'...
    Found 111 source text(s) (111 new and 0 already existing)
```

En este caso, indicando explícitamente la extensión `.py`, `lupdate` analizó correctamente todos los archivos Python del proyecto y generó el archivo `geimesdb_es.ts` con las cadenas marcadas mediante `tr()`.

El archivo generado (`.ts`) contiene todas las cadenas traducibles de la aplicación y puede editarse con **Qt Linguist**.

## Editar las traducciones

Abrir el archivo de traducciones con:

```bash
pyside6-linguist src/ui/translations/geimesdb_es.ts
```

En Qt Linguist se introduce la traducción correspondiente a cada cadena y se marca como finalizada.

## Compilar las traducciones

Una vez completadas las traducciones, el archivo `.ts` debe compilarse a formato `.qm`, que es el utilizado por la aplicación en tiempo de ejecución:

```bash
pyside6-lrelease src/ui/translations/geimesdb_es.ts
```

Esto generará:

```text
src/translations/geimesdb_es.qm
```

## Idioma base

El idioma original de GeiMesDB es el **inglés**, por lo que no es necesario mantener un archivo `geimesdb_en.ts`. Cuando no se carga ningún traductor, Qt muestra automáticamente los textos originales definidos en el código fuente.

Por este motivo, únicamente es necesario crear archivos `.ts` para los idiomas adicionales que se deseen soportar, por ejemplo:

```text
src/
└── ui/
    └── translations/
        ├── geimesdb_es.ts
        ├── geimesdb_es.qm
        ├── geimesdb_fr.ts
        └── geimesdb_fr.qm
```

## Resumen de comandos

```bash
pyside6-lupdate -extensions py src -ts src/ui/translations/geimesdb_es.ts
pyside6-linguist src/ui/translations/geimesdb_es.ts
pyside6-lrelease src/ui/translations/geimesdb_es.ts
```
