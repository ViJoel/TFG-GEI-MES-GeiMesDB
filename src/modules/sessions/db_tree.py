from typing import Any

from sqlalchemy import (
    create_engine,
    inspect,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector

from log.app_logger import get_logger
from modules.sessions.manager import get_session

logger = get_logger(__name__)

# ==================
# === PUBLIC API ===
# ==================


def get_db_tree(
    connection_id: str,
) -> (
    dict[
        str,
        Any,
    ]
    | None
):
    """
    Obtiene la estructura completa de metadatos (tablas y vistas)
    de una base de datos activa.

    Args:
        connection_id:
            Identificador único de la conexión/sesión activa.

    Returns:
        dict[str,Any]:
            Un diccionario con la estructura de la base de datos ("tables" y "views").

        None:
            Si no existe una sesión activa para el identificador proporcionado.
    """

    session = get_session(connection_id)

    if session is None:
        logger.warning(
            "There is no active session for the connection %s.",
            connection_id,
        )
        return None

    return _extract_schema_metadata(session.engine)


# ==========================================
# EXTRACCIÓN DE DATOS
# ==========================================


def _extract_schema_metadata(
    engine: Engine,
) -> dict[
    str,
    Any,
]:
    """
    Extrae los metadatos completos del esquema de la base de datos
    asociada a un Engine.

    Args:
        engine (Engine):
            Instancia de SQLAlchemy Engine para inspeccionar.

    Returns:
        dict[str, Any]:
            Diccionario raíz con dos claves primarias: 'tables' y 'views'.
    """

    inspector = inspect(engine)

    tables_data = {
        table: _extract_table_metadata(inspector, table)
        for table in inspector.get_table_names()
    }

    views_data = _extract_all_views_metadata(inspector)

    return {
        "tables": tables_data,
        "views": views_data,
    }


# ==========================================
# SUBFUNCIONES PARA TABLAS
# ==========================================


def _extract_table_metadata(
    inspector: Inspector,
    table_name: str,
) -> dict[
    str,
    Any,
]:
    """
    Extrae las columnas, restricciones e índices de una tabla específica.

    Args:
        inspector:
            Instancia de SQLAlchemy Inspector.

        table_name:
            Nombre de la tabla a inspeccionar.

    Returns:
        dict[str, Any]:
            Diccionario con las claves 'columns', 'constraints' e 'indexes'.
    """

    pk_constraint = inspector.get_pk_constraint(table_name)
    pk_cols = set(
        pk_constraint.get(
            "constrained_columns",
            [],
        )
    )

    foreign_keys = inspector.get_foreign_keys(table_name)
    fk_cols = {
        col
        for fk in foreign_keys
        for col in fk.get(
            "constrained_columns",
            [],
        )
    }

    unique_cols = {
        uq["column_names"][0]
        for uq in inspector.get_unique_constraints(table_name)
        if len(uq.get("column_names", [])) == 1
    }

    return {
        "columns": _extract_columns(
            inspector,
            table_name,
            pk_cols,
            fk_cols,
            unique_cols,
        ),
        "constraints": _extract_constraints(
            inspector,
            table_name,
            pk_constraint,
            pk_cols,
            foreign_keys,
        ),
        "indexes": _extract_indexes(
            inspector,
            table_name,
        ),
    }


def _extract_columns(
    inspector: Inspector,
    table_name: str,
    pk_cols: set[str],
    fk_cols: set[str],
    unique_cols: set[str],
) -> list[
    dict[
        str,
        Any,
    ]
]:
    """
    Construye la lista de definición de columnas para una tabla.

    Args:
        inspector:
            Instancia de SQLAlchemy Inspector.

        table_name:
            Nombre de la tabla.

        pk_cols:
            Conjunto de nombres de columnas que forman la clave primaria.

        fk_cols:
            Conjunto de nombres de columnas que forman claves foráneas.

    Returns:
        list[dict[str, Any]]:
            Lista de diccionarios con atributos de cada columna
            (name, type, pk, fk, nullable, default).
    """

    columns = []
    for col in inspector.get_columns(table_name):
        columns.append(
            {
                "name": col["name"],
                "type": str(col["type"]),
                "pk": col["name"] in pk_cols,
                "fk": col["name"] in fk_cols,
                "unique": col["name"] in unique_cols,
                "nullable": col.get("nullable", True),
                "default": (
                    str(col["default"]) if col.get("default") is not None else None
                ),
            }
        )
    return columns


def _extract_constraints(
    inspector: Inspector,
    table_name: str,
    pk_constraint: dict,
    pk_cols: set[str],
    foreign_keys: list[dict],
) -> list[
    dict[
        str,
        Any,
    ]
]:
    """
    Recopila las restricciones (Primary Key, Foreign Keys, Unique) de una tabla.

    Args:
        inspector:
            Instancia de SQLAlchemy Inspector.

        table_name:
            Nombre de la tabla.

        pk_constraint:
            Diccionario de la restricción primaria devuelto por SQLAlchemy.

        pk_cols:
            Conjunto de columnas primarias.

        foreign_keys:
            Lista de diccionarios con claves foráneas.

    Returns:
        list[dict[str, Any]]:
            Lista de restricciones formateadas en diccionarios.
    """

    constraints = []

    if pk_constraint.get("name") and pk_cols:
        constraints.append(
            {
                "name": pk_constraint["name"],
                "type": "PRIMARY_KEY",
                "columns": list(pk_cols),
            }
        )

    for fk in foreign_keys:
        constraints.append(
            {
                "name": fk.get("name") or f"fk_{table_name}_{fk['referred_table']}",
                "type": "FOREIGN_KEY",
                "columns": fk.get(
                    "constrained_columns",
                    [],
                ),
                "referred_table": fk.get("referred_table"),
                "referred_columns": fk.get(
                    "referred_columns",
                    [],
                ),
            }
        )

    for uq in inspector.get_unique_constraints(table_name):
        constraints.append(
            {
                "name": uq.get("name"),
                "type": "UNIQUE",
                "columns": uq.get(
                    "column_names",
                    [],
                ),
            }
        )

    return constraints


def _extract_indexes(
    inspector: Inspector,
    table_name: str,
) -> list[
    dict[
        str,
        Any,
    ]
]:
    """
    Obtiene los índices configurados en una tabla o vista materializada.

    Args:
        inspector:
            Instancia de SQLAlchemy Inspector.

        table_name:
            Nombre de la tabla o vista.

    Returns:
        list[dict[str, Any]]:
            Lista de diccionarios detallando el nombre, columnas y unicidad de
            cada índice.
    """

    return [
        {
            "name": idx.get("name"),
            "columns": idx.get(
                "column_names",
                [],
            ),
            "unique": idx.get(
                "unique",
                False,
            ),
        }
        for idx in inspector.get_indexes(table_name)
    ]


# ==========================================
# SUBFUNCIONES PARA VISTAS
# ==========================================


def _extract_all_views_metadata(
    inspector: Inspector,
) -> dict[
    str,
    dict[
        str,
        Any,
    ],
]:
    """
    Obtiene la información de todas las vistas (estándar y materializadas)
    soportadas.

    Args:
        inspector:
            Instancia de SQLAlchemy Inspector.

    Returns:
        dict[str, dict[str, Any]]:
            Diccionario indexado por nombre de vista con sus respectivos metadatos.
    """

    try:
        view_names = inspector.get_view_names()
    except (
        AttributeError,
        NotImplementedError,
    ):
        view_names = []

    try:
        materialized_view_names = inspector.get_materialized_view_names()
    except (
        AttributeError,
        NotImplementedError,
    ):
        materialized_view_names = []

    all_views = [(v, False) for v in view_names] + [
        (mv, True) for mv in materialized_view_names
    ]

    return {
        view_name: _extract_single_view_metadata(
            inspector,
            view_name,
            is_mat,
        )
        for view_name, is_mat in all_views
    }


def _extract_single_view_metadata(
    inspector: Inspector,
    view_name: str,
    is_materialized: bool,
) -> dict[
    str,
    Any,
]:
    """
    Extrae las columnas, código SQL de definición e índices de una vista específica.

    Args:
        inspector:
            Instancia de SQLAlchemy Inspector.

        view_name:
            Nombre de la vista.

        is_materialized:
            Indica si la vista es materializada.

    Returns:
        dict[str, Any]:
            Diccionario con atributos 'is_materialized', 'definition', 'columns' e 'indexes'.
    """

    try:
        columns = [
            {
                "name": col["name"],
                "type": str(
                    col["type"],
                ),
            }
            for col in inspector.get_columns(view_name)
        ]
    except (
        AttributeError,
        NotImplementedError,
    ):
        columns = []

    try:
        definition = inspector.get_view_definition(view_name)
    except (
        AttributeError,
        NotImplementedError,
    ):
        definition = None

    indexes = []
    if is_materialized:
        try:
            indexes = _extract_indexes(
                inspector,
                view_name,
            )
        except (
            AttributeError,
            NotImplementedError,
        ):
            pass

    return {
        "is_materialized": is_materialized,
        "definition": definition,
        "columns": columns,
        "indexes": indexes,
    }


# --- Ejemplo de uso con SQLite ---
if __name__ == "__main__":
    import pprint

    # Base de datos en memoria
    engine = create_engine("sqlite:///:memory:")

    # En SQLAlchemy 2.0+ las sentencias SQL se ejecutan usando un bloque de conexión y text()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE
            );
        """))

        conn.execute(text("""
            CREATE TABLE pedidos (
                id INTEGER PRIMARY KEY,
                usuario_id INTEGER,
                total DECIMAL(10,2),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            );
        """))

        conn.execute(text("""
            CREATE VIEW vista_pedidos AS 
            SELECT p.id, u.email, p.total 
            FROM pedidos p 
            JOIN usuarios u ON p.usuario_id = u.id;
        """))

        # Confirmamos los cambios en la base de datos en memoria
        conn.commit()

    # Ejecutamos la extracción pasando el engine
    metadata_extraida = _extract_schema_metadata(engine)
    pprint.pprint(metadata_extraida)
