# Clicks repetidos sobre el botón de conexión

## Índice

- [Clicks repetidos sobre el botón de conexión](#clicks-repetidos-sobre-el-botón-de-conexión)
  - [Índice](#índice)
  - [Problema](#problema)
  - [Solución propuesta](#solución-propuesta)

---

## Problema

La interfaz permite realizar múltiples pulsaciones consecutivas sobre el botón de conectar mientras se está procesando la apertura de la sesión.

Aunque el backend impide la creación de múltiples sesiones para una misma conexión, cada pulsación genera un nuevo intento de conexión que es añadido a la cola de eventos. Esto provoca que la interfaz deje de responder temporalmente hasta que todos los eventos pendientes son procesados, degradando la experiencia de usuario.

Cada intento adicional acaba siendo rechazado por el backend, pero aun así consume recursos innecesariamente y puede dar la sensación de que la aplicación se ha bloqueado.

---

## Solución propuesta

Deshabilitar temporalmente el botón de conexión mientras se está procesando la apertura de la sesión y volver a habilitarlo una vez finalice la operación, independientemente de si la conexión se ha establecido correctamente o ha fallado.

De esta forma se evita la generación de eventos redundantes, se mejora la capacidad de respuesta de la interfaz y se garantiza que únicamente exista un intento de conexión activo por cada solicitud del usuario.
