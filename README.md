# TFG-GEI-MES-GeiMesDB

## Índice

- [TFG-GEI-MES-GeiMesDB](#tfg-gei-mes-geimesdb)
  - [Índice](#índice)
  - [Descripción del proyecto](#descripción-del-proyecto)
  - [Características principales](#características-principales)
  - [Tecnologías utilizadas](#tecnologías-utilizadas)
    - [Sistema operativo](#sistema-operativo)
    - [Lenguaje y framework](#lenguaje-y-framework)
    - [Base de datos](#base-de-datos)
    - [Herramientas de desarrollo](#herramientas-de-desarrollo)
    - [Testing y calidad del código](#testing-y-calidad-del-código)
    - [Generación del ejecutable](#generación-del-ejecutable)
    - [Cifrado y seguridad](#cifrado-y-seguridad)
    - [Icono del ejecutable de la aplicación](#icono-del-ejecutable-de-la-aplicación)
  - [Requisitos previos](#requisitos-previos)
  - [Instalación](#instalación)
  - [Configuración](#configuración)
  - [Uso](#uso)
  - [Estructura del proyecto](#estructura-del-proyecto)
  - [Base de datos y logs](#base-de-datos-y-logs)
    - [Estructura](#estructura)
    - [Base de datos](#base-de-datos-1)
    - [Logs](#logs)
  - [Capturas de pantalla / ejemplos](#capturas-de-pantalla--ejemplos)
  - [Autor](#autor)
  - [Licencia](#licencia)

## Descripción del proyecto

**GeiMesDB** es una aplicación de escritorio orientada a la interacción, administración y gestión de **bases de datos relacionales**.

El principal objetivo del proyecto es ofrecer una herramienta **sencilla, clara y fácil de utilizar**, centrada en las funcionalidades habituales para trabajar con bases de datos relacionales. Se busca evitar la incorporación de funcionalidades poco comunes o de uso poco frecuente que puedan añadir complejidad innecesaria a la aplicación.

De esta forma, GeiMesDB apuesta por una experiencia de uso directa, manteniendo el foco en las tareas esenciales de administración y trabajo con bases de datos.

## Características principales

- **Gestión de bases de datos relacionales**
  Permite interactuar con bases de datos relacionales de forma sencilla y centralizada.
- **Interfaz gráfica intuitiva**
  Diseñada para facilitar el trabajo con bases de datos sin añadir complejidad innecesaria.
- **Consulta y manipulación de datos**
  Permite consultar, insertar, modificar y eliminar información de las bases de datos.
- **Gestión de estructuras**
  Permite trabajar con los diferentes elementos que componen una base de datos relacional.
- **Gestión de conexiones**
  Permite configurar y administrar las conexiones con las bases de datos.
- **Seguridad de credenciales**
  Protección y almacenamiento seguro de las credenciales utilizadas para las conexiones.
- **Sistema de logs**
  Registro de la actividad de la aplicación para facilitar el seguimiento y diagnóstico de posibles problemas.
- **Simplicidad como principio de diseño**
  La aplicación se centra en las funcionalidades habituales, evitando características poco comunes que puedan dificultar su uso.

## Tecnologías utilizadas

### Sistema operativo

- **Linux Mint Cinnamon** — Sistema operativo utilizado como entorno principal de desarrollo.

### Lenguaje y framework

- **Python 3.12.12** — Lenguaje principal utilizado para el desarrollo de la aplicación.
- **Qt** — Framework utilizado para el desarrollo de la aplicación.
- **Qt Widgets** — Módulo de Qt utilizado para desarrollar la interfaz gráfica.
- **PySide6** — Bindings de Qt para Python.

### Base de datos

- **SQLite** — Sistema de base de datos utilizado por la aplicación.
- **SQLAlchemy** — ORM utilizado para la gestión y comunicación con la base de datos.

### Herramientas de desarrollo

- **Visual Studio Code** — Entorno de desarrollo utilizado para programar y gestionar el proyecto.
- **Git** — Sistema de control de versiones utilizado para realizar el seguimiento de los cambios del proyecto.
- **GitHub** — Plataforma utilizada para alojar y gestionar el repositorio del proyecto.

### Testing y calidad del código

- **pytest** — Framework utilizado para las pruebas automatizadas.
- **pytest-qt** — Herramienta para realizar pruebas sobre componentes Qt.
- **pytest-cov** — Utilizado para medir la cobertura de las pruebas.
- **pytest-mock** — Soporte para el uso de mocks durante las pruebas.
- **Black** — Formateador automático de código Python.
- **isort** — Herramienta utilizada para organizar los imports.

### Generación del ejecutable

- **PyInstaller** — Utilizado para empaquetar la aplicación y generar el ejecutable distribuible.

### Cifrado y seguridad

- **cryptography** — Librería utilizada para las funcionalidades de cifrado y protección de información sensible.
- **keyring** — Gestión segura de credenciales y claves almacenadas en el sistema.
- **SecretStorage** — Almacenamiento seguro de información sensible mediante los servicios de credenciales del sistema.

### Icono del ejecutable de la aplicación

> [!NOTE]
>
> **Pillow** se utilizó únicamente durante el desarrollo para convertir el icono de la aplicación al formato `.ico`. No forma parte de las dependencias de la aplicación y, por tanto, no se incluye en `requirements.txt`.
>
> ```bash
> pip install Pillow
> ```

## Requisitos previos

> Vacío

## Instalación

> Vacío

## Configuración

> Vacío

## Uso

> Vacío

## Estructura del proyecto

La estructura principal del proyecto es la siguiente:

```text
GeiMesDB/
├── doc/                # Documentación del proyecto.
├── src/                # Código fuente de la aplicación.
├── tests/              # Pruebas automatizadas.
├── .vscode/            # Configuración de Visual Studio Code.
├── .gitignore          # Archivos y directorios ignorados por Git.
├── LICENSE             # Licencia del proyecto.
├── pytest.ini          # Configuración de pytest.
├── README.md           # Documentación principal del proyecto.
└── requirements.txt    # Dependencias del proyecto.
```

## Base de datos y logs

La aplicación utiliza **SQLite** como sistema de gestión de base de datos y dispone de un archivo de logs para registrar la actividad de la aplicación.

Ambos recursos son **generados automáticamente por la aplicación**. Cada vez que se inicia GeiMesDB, se comprueba la existencia de los archivos necesarios. Si alguno de ellos no existe, la aplicación se encarga de crearlo automáticamente.

### Estructura

Los archivos se encuentran organizados de la siguiente manera respecto al directorio del ejecutable:

```text
Carpeta/
├── ejecutable
├── geimesdb_data/
│   └── app.db
└── geimesdb_logs/
    └── app.log
```

### Base de datos

El archivo `app.db` contiene la base de datos SQLite utilizada por GeiMesDB.

- **Ubicación:** `geimesdb_data/app.db`
- Se genera automáticamente si no existe.
- La aplicación comprueba su existencia cada vez que se inicia.

### Logs

El archivo `app.log` almacena los registros generados durante la ejecución de la aplicación.

- **Ubicación:** `geimesdb_logs/app.log`
- Se genera automáticamente si no existe.
- Al iniciar la aplicación, el contenido anterior del archivo se **elimina y se sobrescribe**, comenzando un nuevo registro para la ejecución actual.

## Capturas de pantalla / ejemplos

> Vacío

## Autor

$✦$ $Víctor$ $Jöel$ $Viejo$ $Álvarez$ $✦$

## Licencia

Este proyecto está bajo la **Licencia MIT**.

Puedes consultar el texto completo de la licencia en el archivo [`LICENSE`](LICENSE) incluido en este repositorio.

La Licencia MIT permite utilizar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y vender copias del software, siempre que se mantenga el aviso de copyright y la licencia original.
