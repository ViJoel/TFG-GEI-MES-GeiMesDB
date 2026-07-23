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

    _saved_path: Path | None = field(init=False)
    """
    Ruta del archivo desde el último guardado.
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
        self._saved_path = self.path
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

    @property
    def existsOnDisk(
        self,
    ) -> bool:
        """
        Indica si el archivo existe físicamente en disco
        utilizando el path (si no tiene path es que es un
        arcihvo creado por la aplicacion que todavía no
        existe en disco).

        Returns:
            bool:
                - `True` si el archivo existe.
                - `False` en caso contrario.
        """

        if self.path is not None:
            return True
        else:
            return False

    def rename(
        self,
        new_name: str,
    ) -> None:
        """
        Cambia el nombre del archivo y
        actualiza el directorio si corresponde.

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

        self._saved_path = self.path
        self._saved_name = self.name
        self._saved_content = self.content

    def change_path(
        self,
        path: Path,
    ) -> None:
        """
        Modifica el path y el nombre del
        archivo para mantenerlo sincronizado.
        """

        self.path = path
        self.name = path.name
