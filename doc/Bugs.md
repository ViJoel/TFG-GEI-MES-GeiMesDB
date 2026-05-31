# Bugs

## Clicks infinitos sobre el botón de conectar

- **Problema:**
  Aunque el backend bloquea la creación de varias sesiones para una misma conexión. La interfaz permite clickar de forma infinita sobre el botón. Esto hace que la interfaz que empiece a quedar pillada hasta que termina de procesar todos los clicks y en cada uno de ellos se intenta abrir una sesión para la conexión.
</br>

- **Solución:**
  De alguna forma deshabilitar el botón de conectar durante el intento de conexión.
