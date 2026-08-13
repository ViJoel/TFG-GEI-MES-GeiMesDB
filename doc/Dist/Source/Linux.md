# Instrucciones de instalación manual mediante el código fuente en Linux 🐧

## Índice

- [Instrucciones de instalación manual mediante el código fuente en Linux 🐧](#instrucciones-de-instalación-manual-mediante-el-código-fuente-en-linux-)
  - [Índice](#índice)
  - [Descarga](#descarga)
    - [Descargar el código como archivo comprimido](#descargar-el-código-como-archivo-comprimido)
    - [Clonar el repositorio mediante Git](#clonar-el-repositorio-mediante-git)
  - [Preparación del entorno](#preparación-del-entorno)
    - [1. Comprobar la versión de Python](#1-comprobar-la-versión-de-python)
    - [2. Crear un entorno virtual](#2-crear-un-entorno-virtual)
    - [3. Activar el entorno virtual](#3-activar-el-entorno-virtual)
    - [4. Instalar las dependencias](#4-instalar-las-dependencias)
  - [Compilación](#compilación)
  - [Ubicación y ejecución del programa](#ubicación-y-ejecución-del-programa)
    - [Archivos generados por la aplicación](#archivos-generados-por-la-aplicación)
  - [Finalización](#finalización)

## Descarga

El código fuente del proyecto está disponible en el [repositorio de GitHub](https://github.com/ViJoel/TFG-GEI-MES-GeiMesDB).

Puedes obtener el código fuente de dos formas:

- Desde la rama `main`.
- Desde el *tag* correspondiente a la última versión publicada, identificado con el número de versión más alto.

Ambas opciones contienen la versión más reciente del proyecto, por lo que puedes utilizar la que prefieras.

### Descargar el código como archivo comprimido

Si descargas el proyecto como un archivo comprimido desde GitHub:

1. Crea una carpeta vacía en la ubicación donde quieras trabajar.
2. Descarga el proyecto y coloca el archivo comprimido dentro de dicha carpeta.
3. Descomprime el archivo.

Se recomienda utilizar una carpeta independiente para el proyecto para mantener todos sus archivos agrupados y evitar modificar accidentalmente otros archivos del sistema.

### Clonar el repositorio mediante Git

Si prefieres utilizar Git en lugar de descargar el archivo comprimido, clona el repositorio directamente dentro de una carpeta destinada al proyecto.

Una vez descargado o clonado el proyecto, sitúate en su carpeta raíz para continuar con los siguientes pasos.

## Preparación del entorno

Antes de compilar el proyecto es necesario preparar el entorno de Python e instalar todas las dependencias.

### 1. Comprobar la versión de Python

El proyecto requiere **Python 3.12.12**.

Puedes comprobar la versión instalada ejecutando:

```bash
python3.12 --version
```

Debería mostrarse:

```text
Python 3.12.12
```

Si tienes varias versiones de Python instaladas, es importante utilizar explícitamente **Python 3.12** para crear el entorno virtual y realizar el resto de los pasos de instalación.

Además, debes disponer del módulo [`venv`](https://docs.python.org/es/3.12/library/venv.html), necesario para crear entornos virtuales.

Puedes comprobar que está disponible para Python 3.12 ejecutando:

```bash
python3.12 -m venv --help
```

### 2. Crear un entorno virtual

Desde la carpeta raíz del proyecto, crea un entorno virtual. Sustituye `nombre_del_entorno` por el nombre que quieras utilizar. En este documento utilizaremos `.venv`.

```bash
# python3.12 -m venv nombre_del_entorno
python3.12 -m venv .venv
```

### 3. Activar el entorno virtual

Activa el entorno virtual mediante:

```bash
# source nombre_del_entorno/bin/activate
source .venv/bin/activate
```

Una vez activado, el nombre del entorno aparecerá normalmente al principio de la línea de comandos.

Puedes comprobar que estás utilizando el **Python** y el **pip** correspondientes al entorno virtual mediante:

```bash
which python
which pip
```

Las rutas mostradas deberían apuntar a los ejecutables situados dentro de la carpeta del entorno virtual.

También puedes comprobar directamente la versión de Python utilizada:

```bash
python --version
```

Debería mostrarse:

```text
Python 3.12.12
```

### 4. Instalar las dependencias

Asegúrate de encontrarte en la **carpeta raíz del proyecto**, es decir, en la carpeta que contiene el archivo `requirements.txt`.

A continuación, instala las dependencias:

```bash
pip install -r requirements.txt
```

Puedes comprobar que las dependencias se han instalado correctamente mediante:

```bash
pip list
```

## Compilación

Una vez preparado el entorno virtual y con este activado, sitúate en la **carpeta raíz del proyecto**.

La aplicación se compila utilizando PyInstaller. Ejecuta el siguiente comando:

```bash
pyinstaller \
    --name GeiMesDB \
    --onefile \
    --clean \
    --noconfirm \
    --icon "icon/icon.ico" \
    --paths src \
    --add-data "src/data:data" \
    --add-data "src/ui/resources:ui/resources" \
    --add-data "src/ui/styles:ui/styles" \
    --add-data "src/ui/translations:ui/translations" \
    src/main.py
```

> [!NOTE]
>
> En Linux, PyInstaller ignora la opción `--icon`, ya que la asignación de iconos al ejecutable no está soportada en esta plataforma. Esto genera un aviso durante la compilación, pero no afecta al funcionamiento del ejecutable.

Así puedes **mantener exactamente el mismo comando en Windows y Linux**. En Windows se aplicará el icono y en Linux simplemente se mostrará el aviso correspondiente.

Durante el proceso, PyInstaller generará varias carpetas y archivos temporales. El resultado final se encontrará en la carpeta:

```text
dist/
```

Dentro de ella estará el ejecutable:

```text
dist/GeiMesDB
```

Este archivo es el ejecutable de la aplicación. Contiene el intérprete de Python y las dependencias necesarias para su ejecución, por lo que no es necesario tener Python instalado en el sistema donde se ejecute.

## Ubicación y ejecución del programa

Puedes mover el ejecutable `GeiMesDB` de la carpeta `dist/` a la ubicación donde quieras instalar la aplicación.

Por ejemplo:

```bash
mkdir -p ~/GeiMesDB
cp dist/GeiMesDB ~/GeiMesDB/
```

A continuación, puedes ejecutar la aplicación mediante:

```bash
~/GeiMesDB/GeiMesDB
```

### Archivos generados por la aplicación

> [!IMPORTANT]
> La aplicación genera determinados archivos necesarios para su funcionamiento en la misma carpeta en la que se encuentra el ejecutable.

Si estos archivos ya existen, la aplicación los reutilizará en lugar de generarlos de nuevo.

Por este motivo, debes tener en cuenta lo siguiente:

- La primera vez que ejecutes la aplicación, se generarán los archivos necesarios junto al ejecutable.
- Si posteriormente mueves el ejecutable a otra carpeta y ejecutas la aplicación allí, se generarán nuevos archivos en esa ubicación.
- Si vuelves a colocar el ejecutable en la carpeta original y los archivos generados anteriormente siguen allí, la aplicación volverá a utilizarlos.
- No debes eliminar ni modificar estos archivos si quieres conservar el estado o la configuración que la aplicación haya almacenado en ellos.

Por tanto, se recomienda mantener el ejecutable y los archivos que genere la aplicación juntos en una carpeta dedicada exclusivamente a `GeiMesDB`.

## Finalización

> [!WARNING]
>
> Una vez generado el ejecutable de la aplicación, puedes eliminar el entorno de Python utilizado para la compilación, ya que el ejecutable generado por PyInstaller contiene el intérprete de Python y las dependencias necesarias para ejecutar la aplicación.
>
> **Se recomienda conservar una copia del código fuente del proyecto**, ya que será necesario para realizar modificaciones o generar nuevamente el ejecutable en el futuro.
>
> **Nota:** el ejecutable generado por PyInstaller es específico del sistema operativo para el que se ha realizado la compilación.
