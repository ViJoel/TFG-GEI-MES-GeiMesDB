# Bug conocido: múltiples intentos de conexión por pulsaciones repetidas del botón

## Índice

- [Bug conocido: múltiples intentos de conexión por pulsaciones repetidas del botón](#bug-conocido-múltiples-intentos-de-conexión-por-pulsaciones-repetidas-del-botón)
  - [Índice](#índice)
  - [Descripción](#descripción)
  - [Reproducción](#reproducción)
  - [Comportamiento observado](#comportamiento-observado)
  - [Causa](#causa)
  - [Impacto](#impacto)
  - [Estado](#estado)
  - [Solución propuesta](#solución-propuesta)

---

## Descripción

Durante el proceso de apertura de una conexión, la interfaz permite pulsar repetidamente el botón **Conectar** antes de que finalice la operación.

Cada pulsación genera una nueva solicitud de conexión que es enviada al bucle de eventos de la aplicación, aunque ya exista un intento de conexión en curso.

---

## Reproducción

1. Iniciar una conexión.
2. Antes de que finalice, pulsar repetidamente el botón **Conectar**.
3. Observar el comportamiento de la interfaz.

---

## Comportamiento observado

Cada pulsación adicional genera un nuevo intento de conexión.

Aunque el backend impide que existan varias sesiones activas para la misma conexión y rechaza los intentos posteriores, todas las solicitudes deben procesarse antes de que el bucle de eventos quede completamente libre.

Como consecuencia:

- Se ejecutan operaciones redundantes.
- Se consumen recursos innecesariamente.
- La interfaz puede dejar de responder temporalmente.
- El usuario puede interpretar que la aplicación se ha bloqueado.

---

## Causa

El botón de conexión permanece habilitado mientras la operación de apertura sigue en curso.

Esto permite que el usuario genere múltiples solicitudes antes de recibir la respuesta del primer intento.

El backend protege correctamente la creación de sesiones duplicadas, pero la interfaz no impide la generación de solicitudes redundantes.

---

## Impacto

No se producen conexiones duplicadas ni inconsistencias en el estado de la aplicación.

Sin embargo:

- Se degrada la capacidad de respuesta de la interfaz.
- Se incrementa el trabajo del backend.
- Se reduce la calidad de la experiencia de usuario.

---

## Estado

Pendiente de implementación.

---

## Solución propuesta

Deshabilitar el botón **Conectar** inmediatamente después de iniciar una solicitud de conexión.

El botón deberá volver a habilitarse cuando la operación finalice, independientemente de si:

- la conexión se establece correctamente;
- se produce un error;
- el usuario cancela la operación.

De este modo se garantiza que únicamente exista un intento de conexión iniciado desde la interfaz para cada solicitud del usuario, evitando la generación de eventos redundantes y mejorando la capacidad de respuesta de la aplicación.
