# Comandos de GIT

```bash
git --no-pager diff --name-status <ORIGEN_ANTIGUO> ... <DESTINO_RECIENTE>
│   │          │    │            │                 │   │
│   │          │    │            │                 │   └─ Rama con tus cambios nuevos (ej. feature/mi-rama o HEAD).
│   │          │    │            │                 └─ Operador de 3 puntos (compara desde el ancestro común).
│   │          │    │            └─ Rama de partida/base antigua (ej. main o develop).
│   │          │    └─ Formato resumido: Estado (A|M|D) + Nombre de archivo.
│   │          └─ Muestra las diferencias.
│   └─ Salida directa a la terminal (sin pausar con paginador).
└─ Comando principal de Git.
```

---

```bash
git --no-pager diff --name-status develop...HEAD
```

Muestra una lista limpia de los archivos añadidos, modificados o eliminados en tu rama actual (`HEAD`) en comparación con la rama `develop`, imprimiendo el resultado directo en la terminal sin pausar.
