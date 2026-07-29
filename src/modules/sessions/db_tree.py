from typing import Any

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.sqltypes import NullType

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

    try:

        logger.info(
            "Loading database tree for connection '%s'.",
            connection_id,
        )

        tree_data = _extract_schema_metadata(session.engine)

        logger.success(
            "Database tree loaded successfully for connection '%s'.",
            connection_id,
        )

        return tree_data

    except Exception:

        logger.exception(
            "Unable to load database tree for connection '%s'.",
            connection_id,
        )

        return None


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

    logger.debug(
        "Found %d tables and %d views.",
        len(tables_data),
        len(views_data),
    )

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

    logger.debug(
        "Inspecting table '%s'.",
        table_name,
    )

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


def _build_columns(
    columns_data: list[dict[str, Any]],
    table_name: str,
    pk_cols: set[str] | None = None,
    fk_cols: set[str] | None = None,
    unique_cols: set[str] | None = None,
) -> list[
    dict[
        str,
        Any,
    ]
]:
    """
    Construye la representación interna de un conjunto de columnas.

    Normaliza la información devuelta por SQLAlchemy para que todas las
    columnas (tanto de tablas como de vistas) compartan el mismo modelo de
    datos dentro de la aplicación.

    Los tipos de datos no reconocidos por SQLAlchemy (`NullType`) se
    representan como `"UNKNOWN TYPE"`.

    Args:
        columns_data:
            Lista de diccionarios de columnas devuelta por
            `Inspector.get_columns()`.

        pk_cols:
            Conjunto de nombres de columnas pertenecientes a la clave
            primaria.

        fk_cols:
            Conjunto de nombres de columnas que forman parte de una clave
            foránea.

        unique_cols:
            Conjunto de nombres de columnas con una restricción UNIQUE.

    Returns:
        list[dict[str, Any]]:
            Lista de diccionarios normalizados con los atributos:

            - `name`
            - `type`
            - `pk`
            - `fk`
            - `unique`
            - `nullable`
            - `default`
    """

    pk_cols = pk_cols or set()
    fk_cols = fk_cols or set()
    unique_cols = unique_cols or set()

    columns = []

    for col in columns_data:

        if isinstance(col["type"], NullType):

            column_type = "UNKNOWN TYPE"

            logger.warning(
                "Unknown SQL type detected in '%s.%s'. Using placeholder type.",
                table_name,
                col["name"],
            )

        else:
            column_type = str(col["type"])

        columns.append(
            {
                "name": col["name"],
                "type": column_type,
                "pk": col["name"] in pk_cols,
                "fk": col["name"] in fk_cols,
                "unique": col["name"] in unique_cols,
                "nullable": col.get("nullable", True),
                "default": (
                    str(col["default"]) if col.get("default") is not None else None
                ),
            }
        )

    logger.debug(
        "Found %d columns in '%s'.",
        len(columns),
        table_name,
    )

    return columns


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
    Extrae y normaliza las columnas de una tabla.

    Obtiene la definición de las columnas mediante el `Inspector` de
    SQLAlchemy y delega la construcción del modelo interno en
    `_build_columns()`.

    Args:
        inspector:
            Instancia de SQLAlchemy Inspector.

        table_name:
            Nombre de la tabla.

        pk_cols:
            Conjunto de nombres de columnas que forman la clave primaria.

        fk_cols:
            Conjunto de nombres de columnas que forman claves foráneas.

        unique_cols:
            Conjunto de nombres de columnas con una restricción UNIQUE.

    Returns:
        list[dict[str, Any]]:
            Lista de columnas normalizadas según el modelo interno de la
            aplicación.
    """

    return _build_columns(
        inspector.get_columns(table_name),
        table_name,
        pk_cols,
        fk_cols,
        unique_cols,
    )


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

    logger.debug(
        "Found %d constraints in '%s'.",
        len(constraints),
        table_name,
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

    indexes = [
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

    logger.debug(
        "Found %d indexes in '%s'.",
        len(indexes),
        table_name,
    )

    return indexes


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
        logger.debug("Current SQLAlchemy dialect does not support standard views.")

    try:
        materialized_view_names = inspector.get_materialized_view_names()
    except (
        AttributeError,
        NotImplementedError,
    ):
        materialized_view_names = []
        logger.debug("Current SQLAlchemy dialect does not support materialized views.")

    all_views = [(v, False) for v in view_names] + [
        (mv, True) for mv in materialized_view_names
    ]

    logger.debug(
        "Found %d views (%d standard, %d materialized).",
        len(all_views),
        len(view_names),
        len(materialized_view_names),
    )

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
    Extrae los metadatos de una vista específica.

    Obtiene la definición SQL, las columnas normalizadas y, en el caso de
    vistas materializadas, los índices asociados.

    Args:
        inspector:
            Instancia de SQLAlchemy Inspector.

        view_name:
            Nombre de la vista.

        is_materialized:
            Indica si la vista es materializada.

    Returns:
        dict[str, Any]:
            Diccionario con los siguientes atributos:

            - `is_materialized`
            - `definition`
            - `columns`
            - `indexes`
    """

    logger.debug(
        "Inspecting view '%s'.",
        view_name,
    )

    try:
        columns = _build_columns(
            inspector.get_columns(view_name),
            view_name,
        )
    except (
        AttributeError,
        NotImplementedError,
    ):
        columns = []
        logger.debug(
            "Unable to retrieve columns for view '%s'.",
            view_name,
        )

    try:
        definition = inspector.get_view_definition(view_name)
    except (
        AttributeError,
        NotImplementedError,
    ):
        definition = None
        logger.debug(
            "View '%s' does not expose its SQL definition.",
            view_name,
        )

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
            logger.debug(
                "Materialized view '%s' does not expose indexes.",
                view_name,
            )

    return {
        "is_materialized": is_materialized,
        "definition": definition,
        "columns": columns,
        "indexes": indexes,
    }
