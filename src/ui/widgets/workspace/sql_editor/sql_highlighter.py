import re

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
)

from modules.sql.highlighting.rules import SQL_HIGHLIGHT_RULES
from ui.themes.theme_manager import ThemeManager


class SqlHighlighter(QSyntaxHighlighter):
    """
    Resaltador de sintaxis SQL básica.

    Aplica formato visual a elementos comunes
    del lenguaje SQL.
    """

    # =================
    # === VARIABLES ===
    # =================

    MULTILINE_COMMENT = 1

    # ============
    # === INIT ===
    # ============
    def __init__(
        self,
        document,
    ) -> None:
        """
        Inicializa el resaltador y registra todas las
        reglas de resaltado SQL.

        Args:
            document:
                Documento asociado al editor.
        """

        super().__init__(document)

        self.protected_rules = []
        self.rules = []

        self._register_rules()

    # ===================
    # === RULES SETUP ===
    # ===================

    def _create_format(
        self,
        rule: dict,
    ) -> QTextCharFormat:
        """
        Crea un formato de texto a partir de la
        configuración de una regla de resaltado.

        Args:
            rule (dict):
                Configuración de la regla.

        Returns:
            QTextCharFormat:
                Formato configurado.
        """

        fmt = QTextCharFormat()

        # Obtener color
        fmt.setForeground(
            QColor(
                ThemeManager.get_color(
                    rule.get("color", "text"),
                ),
            )
        )

        # Obtener negrita
        if rule.get("bold", False):
            fmt.setFontWeight(
                QFont.Weight.Bold,
            )

        return fmt

    def _add_rule(
        self,
        rule: dict,
    ) -> None:
        """
        Registra una regla de resaltado.

        Args:
            rule (dict):
                Datos de la regla a aplicar.
        """

        fmt = self._create_format(rule)
        protected = rule.get("protected", False)

        for pattern in rule.get("patterns", []):

            regex_rule = (
                QRegularExpression(
                    pattern,
                    QRegularExpression.PatternOption.CaseInsensitiveOption,
                ),
                fmt,
            )

            if protected:
                self.protected_rules.append(regex_rule)
            else:
                self.rules.append(regex_rule)

    def _register_rules(
        self,
    ) -> None:
        """
        Registra todas las reglas de resaltado.
        """

        for rule in SQL_HIGHLIGHT_RULES.values():
            self._add_rule(rule)

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def highlightBlock(
        self,
        text: str,
    ) -> None:
        """
        Aplica todas las reglas de resaltado al
        bloque de texto recibido por Qt respetando
        las regiones protegidas.

        Args:
            text (str):
                Bloque de texto a procesar.
        """

        protected_ranges: list[tuple[int, int]] = []

        self._highlight_multiline_comments(
            text,
            protected_ranges,
        )

        self._highlight_protected_rules(
            text,
            protected_ranges,
        )

        self._highlight_standard_rules(
            text,
            protected_ranges,
        )

    # ============================
    # === QT OVERRIDES HELPERS ===
    # ============================

    @staticmethod
    def _is_protected(
        start: int,
        end: int,
        protected_ranges: list[tuple[int, int]],
    ) -> bool:
        """
        Indica si un rango de texto se solapa con una
        región protegida.

        Args:
            start (int):
                Posición inicial.

            end (int):
                Posición final.

            protected_ranges (list[tuple[int, int]]):
                Rangos protegidos.

        Returns:
            bool:
                - `True` si el rango se solapa con alguna
                región protegida;
                - `False` en caso contrario.
        """

        return any(
            start < protected_end and end > protected_start
            for protected_start, protected_end in protected_ranges
        )

    # ===================
    # === PRIVATE API ===
    # ===================

    def _highlight_multiline_comments(
        self,
        text: str,
        protected_ranges: list[tuple[int, int]],
    ) -> None:
        """
        Resalta los comentarios multilínea y actualiza
        el estado del bloque.

        Args:
            text (str):
                Bloque de texto.

            protected_ranges (list[tuple[int, int]]):
                Lista donde se registran los rangos
                protegidos encontrados.
        """

        fmt = self._create_format(
            SQL_HIGHLIGHT_RULES["comments"],
        )

        # Por defecto, este bloque no continúa un comentario.
        self.setCurrentBlockState(0)

        # ¿El bloque anterior terminó dentro de un comentario?
        if self.previousBlockState() == self.MULTILINE_COMMENT:
            start = 0
        else:
            start = text.find("/*")

        while start != -1:

            # Si el comentario viene del bloque anterior,
            # puede cerrar en la posición 0.
            search_from = (
                start
                if self.previousBlockState() == self.MULTILINE_COMMENT
                else start + 2
            )

            end = text.find(
                "*/",
                search_from,
            )

            if end == -1:
                # El comentario continúa en el siguiente bloque.
                self.setCurrentBlockState(
                    self.MULTILINE_COMMENT,
                )

                length = len(text) - start

            else:
                # El comentario termina en este bloque.
                length = end - start + 2

            self.setFormat(
                start,
                length,
                fmt,
            )

            protected_ranges.append(
                (
                    start,
                    start + length,
                )
            )

            if end == -1:
                break

            start = text.find(
                "/*",
                end + 2,
            )

    def _highlight_protected_rules(
        self,
        text: str,
        protected_ranges: list[tuple[int, int]],
    ) -> None:
        """
        Aplica las reglas protegidas evitando
        solapamientos.

        Args:
            text (str):
                Bloque de texto.

            protected_ranges (list[tuple[int, int]]):
                Lista de rangos protegidos ya detectados,
                que se actualiza con las nuevas coincidencias.
        """

        for pattern, fmt in self.protected_rules:

            iterator = pattern.globalMatch(text)

            while iterator.hasNext():

                match = iterator.next()

                start = match.capturedStart()
                end = start + match.capturedLength()

                if self._is_protected(
                    start,
                    end,
                    protected_ranges,
                ):
                    continue

                protected_ranges.append(
                    (
                        start,
                        end,
                    )
                )

                self.setFormat(
                    start,
                    match.capturedLength(),
                    fmt,
                )

    def _highlight_standard_rules(
        self,
        text: str,
        protected_ranges: list[tuple[int, int]],
    ) -> None:
        """
        Aplica las reglas de resaltado estándar sobre
        las regiones no protegidas.

        Args:
            text (str):
                Bloque de texto.

            protected_ranges (list[tuple[int, int]]):
                Rangos protegidos detectados.
        """

        for pattern, fmt in self.rules:

            iterator = pattern.globalMatch(text)

            while iterator.hasNext():

                match = iterator.next()

                start = match.capturedStart()
                end = start + match.capturedLength()

                if self._is_protected(
                    start,
                    end,
                    protected_ranges,
                ):
                    continue

                self.setFormat(
                    start,
                    match.capturedLength(),
                    fmt,
                )
