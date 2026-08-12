def function(
    arg: str,
) -> bool:
    """
    Verifica si existe una conexión registrada.

    Args:
        arg (str):
            Identificador único de la conexión.

    Returns:
        bool:
            True si existe, False en caso contrario.

    Raises:
        DatabaseError:
            Si ocurre un error durante la consulta.
    """
