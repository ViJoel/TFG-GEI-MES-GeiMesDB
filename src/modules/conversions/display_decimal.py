from dataclasses import dataclass


@dataclass(
    slots=True,
    frozen=True,
)
class DisplayDecimal:
    """
    Representa un valor Decimal normalizado para
    su visualización.

    Permite diferenciar un decimal convertido de
    una cadena de texto original durante el
    formateo de colecciones.
    """

    value: str

    def __str__(
        self,
    ) -> str:
        """
        Devuelve la representación textual del
        decimal.

        Returns:
            str:
                Valor decimal.
        """

        return self.value

    def __repr__(
        self,
    ) -> str:
        """
        Devuelve la representación utilizada
        dentro de colecciones.

        Returns:
            str:
                Valor decimal.
        """

        return self.value
