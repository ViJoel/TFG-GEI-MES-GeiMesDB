from dataclasses import dataclass


@dataclass(
    kw_only=True,
    slots=True,
)
class UnsavedChangesCount:
    """
    Entidad que almacena los cambios no guardados
    en los editores con archivos abiertos para la
    comprobación en durante el cierre de la aplicación.
    """

    connection_name: str
    unsaved_changes: int
