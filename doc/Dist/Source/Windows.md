# Instrucciones de instalación manual mediante el código fuente en Windows 🪟

## Índice

- [Instrucciones de instalación manual mediante el código fuente en Windows 🪟](#instrucciones-de-instalación-manual-mediante-el-código-fuente-en-windows-)
  - [Índice](#índice)
  - [Descarga](#descarga)
    - [Descargar el código como archivo comprimido](#descargar-el-código-como-archivo-comprimido)
    - [Clonar el repositorio mediante Git](#clonar-el-repositorio-mediante-git)
  - [Preparación del entorno](#preparación-del-entorno)
    - [1. Comprobar la versión de Python](#1-comprobar-la-versión-de-python)
      - [Instalar python](#instalar-python)
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

Antes de compilar el proyecto, es necesario preparar el entorno de Python e instalar todas las dependencias necesarias.

### 1. Comprobar la versión de Python

El proyecto requiere **Python 3.12.12**.

No obstante, en Windows puede resultar complicado disponer exactamente de esta versión. Por este motivo, se puede utilizar **Python 3.12.10**, disponible mediante el [instalador oficial](https://www.python.org/downloads/windows/#:~:text=3%2E12%2E10), sin que esto suponga ningún problema para el proyecto.

Para comprobar la versión de Python instalada, abre una terminal, preferiblemente **PowerShell**, aunque también puedes utilizar el **Símbolo del sistema (cmd)**, y ejecuta:

```powershell
py --version
```

Si tienes varias versiones de Python instaladas, puedes consultar todas las versiones disponibles mediante:

```powershell
py --list
```

Tanto si tienes una única versión instalada como si tienes varias, esto no supone ningún inconveniente, ya que durante el proceso se utilizarán comandos que especifican explícitamente la versión de Python que se debe utilizar.

#### Instalar python

Si necesitas instalar Python, sigue estos pasos:

1. [Descarga el instalador oficial de Python 3.12.10](https://www.python.org/downloads/windows/#:~:text=3%2E12%2E10)

2. Ejecuta el instalador **sin permisos de administrador**.

3. Selecciona las siguientes opciones:
   - **Otorgar priviliegios durante la instalación.**
   - **Añadir al PATH.**

4. Haz clic en **Install Now**.

Una vez finalizada la instalación, puedes comprobar que Python 3.12.10 se ha instalado correctamente mediante los comandos anteriores o, específicamente, con:

```powershell
py -3.12 --version
```

### 2. Crear un entorno virtual

Desde la carpeta raíz del proyecto, crea un entorno virtual. Sustituye `nombre_del_entorno` por el nombre que quieras utilizar. En este documento utilizaremos `.venv`.

```powershell
# py -3.12 -m venv nombre_del_entorno
py -3.12 -m venv .venv
```

### 3. Activar el entorno virtual

Si estás utilizando **PowerShell**, activa el entorno virtual mediante los siguientes comandos:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

- Este comando permite ejecutar scripts de PowerShell durante la sesión actual, lo que es necesario para poder activar el entorno virtual. En concreto, `RemoteSigned` permite ejecutar scripts creados localmente y exige que los scripts descargados de Internet estén firmados. Al utilizar `-Scope Process`, este cambio solo se aplica a la sesión actual de PowerShell y se revierte automáticamente al cerrarla.

```powershell
# .\nombre_del_entorno\Scripts\Activate.ps1
.\.venv\Scripts\Activate.ps1
```

Si estás utilizando el **Símbolo del sistema (cmd)**, utiliza:

```cmd
REM nombre_del_entorno\Scripts\activate.bat
.venv\Scripts\activate.bat
```

Una vez activado el entorno virtual, su nombre aparecerá normalmente al principio de la línea de comandos.

Puedes comprobar que estás utilizando las versiones de **Python** y **pip** correspondientes al entorno virtual mediante:

```powershell
where.exe python
where.exe pip
```

La primera ruta mostrada en cada caso debería apuntar a los ejecutables situados dentro de la carpeta del entorno virtual.

### 4. Instalar las dependencias

Asegúrate de encontrarte en la **carpeta raíz del proyecto**, es decir, en la carpeta que contiene el archivo `requirements.txt`.

A continuación, instala las dependencias del proyecto mediante:

```powershell
pip install -r requirements.txt
```

Una vez finalizada la instalación, puedes comprobar las dependencias instaladas mediante:

```powershell
pip list
```

## Compilación

Una vez preparado el entorno virtual y con este activado, sitúate en la **carpeta raíz del proyecto**.

La aplicación se compila mediante el **script de compilación** de Windows, que se encarga de configurar y ejecutar **PyInstaller**, incluyendo las dependencias y recursos necesarios.

Ejecuta el siguiente comando en **PowerShell**:

```powershell
python .\compile\windows\build.py
```

El script realiza automáticamente la limpieza de compilaciones anteriores, configura los parámetros de PyInstaller y recopila las dependencias que requieren un tratamiento especial, como `cryptography`, `cffi` y `oracledb`.

Durante el proceso de compilación, PyInstaller generará varias carpetas y archivos temporales. Una vez finalizado el proceso, el resultado se encontrará en la carpeta:

```text
dist\
```

Dentro de esta carpeta se encontrará el ejecutable:

```text
dist\GeiMesDB.exe
```

Este archivo es el ejecutable de la aplicación. Contiene el intérprete de Python y las dependencias necesarias para su ejecución, por lo que **no es necesario tener Python instalado** en el sistema donde se ejecute la aplicación.

## Ubicación y ejecución del programa

Puedes mover el ejecutable `GeiMesDB.exe` de la carpeta `dist\` a la ubicación donde quieras instalar la aplicación.

Por ejemplo, desde PowerShell:

```powershell
New-Item -ItemType Directory -Path "$HOME\GeiMesDB" -Force
Copy-Item "dist\GeiMesDB.exe" "$HOME\GeiMesDB\"
```

A continuación, puedes ejecutar la aplicación mediante:

```powershell
& "$HOME\GeiMesDB\GeiMesDB.exe"
```

También puedes ejecutar el archivo directamente desde el explorador de archivos haciendo doble clic sobre `GeiMesDB.exe`.

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
