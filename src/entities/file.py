from dataclasses import (
    dataclass,
    field,
)
from pathlib import Path
from uuid import (
    UUID,
    uuid4,
)


@dataclass(
    kw_only=True,
    slots=True,
)
class File:
    """
    Representa un archivo gestionado por la aplicación.
    """

    _id: UUID = field(default_factory=uuid4)
    """
    UUID4 único generado automáticamente.
    """

    path: Path | None = None
    """
    Ruta relativa del archivo.
    """

    name: str = field(init=False)
    """
    Nombre del archivo.
    """

    _saved_name: str = field(init=False)
    """
    Nombre del archivo desde el último guardado.
    """

    content: str = ""
    """
    Contenido del archivo.
    """

    _saved_content: str = field(init=False, default="")
    """
    Contenido original del archivo desde el último guardado.
    """

    def __post_init__(
        self,
    ) -> None:
        """
        Inicializa los atributos derivados.
        """

        self.name = self.path.name if self.path else f"Script_{self._id.hex[:8]}.sql"
        self._saved_name = self.name
        self._saved_content = self.content

    @property
    def has_changes(
        self,
    ) -> bool:
        """
        Indica si el archivo contiene cambios
        pendientes de guardar.

        Returns:
            bool:
                - `True` si existen cambios.
                - `False` en caso contrario.
        """

        return self.name != self._saved_name or self.content != self._saved_content

    def rename(
        self,
        new_name: str,
    ) -> None:
        """
        Cambia el nombre del archivo manteniendo
        el mismo directorio.

        Args:
            new_name:
                Nuevo nombre del archivo.
        """

        if new_name == self.name:
            return

        if self.path is not None:
            self.path = self.path.with_name(new_name)

        self.name = new_name

    def save_changes(
        self,
    ) -> None:
        """
        Guarda los cambios producidos en el archivo.
        """

        self._saved_name = self.name
        self._saved_content = self.content
