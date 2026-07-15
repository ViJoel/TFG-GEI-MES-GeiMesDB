import re

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
)

from modules.sql_highlighting.rules import SQL_RULES
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

        # Reglas protegidas
        self._create_string_rules()
        self._create_comment_rules()

        # Resto de reglas
        self._create_keyword_rules()
        self._create_type_rules()
        self._create_function_rules()
        self._create_literal_rules()
        self._create_symbol_rules()
        self._create_parameter_rules()
        self._create_variable_rules()
        self._create_identifier_rules()

    # ===================
    # === RULES SETUP ===
    # ===================

    def _create_format(
        self,
        color_key: str,
        bold: bool = False,
    ) -> QTextCharFormat:
        """
        Crea un formato de texto a partir de un color
        definido en el tema.

        Args:
            color_key (str):
                Clave del color en el tema.

            bold (bool, optional):
                Indica si el texto debe mostrarse en
                negrita.

        Returns:
            QTextCharFormat:
                Formato configurado.
        """

        fmt = QTextCharFormat()

        fmt.setForeground(
            QColor(
                ThemeManager.get_color(
                    color_key,
                ),
            )
        )

        if bold:
            fmt.setFontWeight(
                QFont.Weight.Bold,
            )

        return fmt

    def _add_rule(
        self,
        pattern: str,
        fmt: QTextCharFormat,
        *,
        protected: bool = False,
    ) -> None:
        """
        Registra una regla de resaltado.

        Args:
            pattern (str):
                Expresión regular de la regla.

            fmt (QTextCharFormat):
                Formato asociado.

            protected (bool, optional):
                Indica si la regla pertenece al grupo
                protegido.
        """

        rule = (
            QRegularExpression(
                pattern,
                QRegularExpression.PatternOption.CaseInsensitiveOption,
            ),
            fmt,
        )

        if protected:
            self.protected_rules.append(rule)
        else:
            self.rules.append(rule)

    @staticmethod
    def _build_word_pattern(
        words: set[str],
    ) -> str:
        """
        Construye una expresión regular para
        palabras completas.

        Args:
            words (set[str]):
                Palabras que forman parte de la regla.

        Returns:
            str:
                Patrón regex generado.
        """

        return rf"\b({'|'.join(words)})\b"

    @staticmethod
    def _build_symbol_pattern(
        symbols: set[str],
    ) -> str:
        """
        Construye una expresión regular para
        operadores y símbolos SQL.

        Args:
            symbols (set[str]):
                Símbolos que forman parte de la regla.

        Returns:
            str:
                Patrón regex generado.
        """

        escaped = sorted(
            (re.escape(symbol) for symbol in symbols),
            key=len,
            reverse=True,
        )

        return f"({'|'.join(escaped)})"

    def _create_string_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para cadenas.
        """

        self._add_rule(
            r"'[^']*'",
            self._create_format(
                "sql_string_simple_quoted_color",
            ),
            protected=True,
        )

    def _create_comment_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para comentarios.
        """

        fmt = self._create_format(
            "sql_comment_color",
        )

        self._add_rule(
            r"--[^\n]*",
            fmt,
            protected=True,
        )

    def _create_keyword_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para palabras reservadas.
        """

        self._add_rule(
            self._build_word_pattern(
                SQL_RULES["keywords"],
            ),
            self._create_format(
                "sql_keyword_color",
                True,
            ),
        )

    def _create_type_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para tipos de datos.
        """

        self._add_rule(
            self._build_word_pattern(
                SQL_RULES["types"],
            ),
            self._create_format(
                "sql_type_color",
            ),
        )

    def _create_function_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para funciones SQL.
        """

        self._add_rule(
            rf"\b({'|'.join(SQL_RULES['functions'])})\b(?=\s*\()",
            self._create_format(
                "sql_function_color",
            ),
        )

    def _create_literal_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para literales.
        """

        self._add_rule(
            r"\b\d+(\.\d+)?\b",
            self._create_format(
                "sql_number_color",
            ),
        )

        self._add_rule(
            self._build_word_pattern(
                SQL_RULES["boolean"],
            ),
            self._create_format(
                "sql_boolean_color",
            ),
        )

        self._add_rule(
            self._build_word_pattern(
                SQL_RULES["null"],
            ),
            self._create_format(
                "sql_null_color",
            ),
        )

    def _create_symbol_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para símbolos SQL.
        """

        self._add_rule(
            self._build_symbol_pattern(
                SQL_RULES["symbols"],
            ),
            self._create_format(
                "sql_symbol_color",
            ),
        )

    def _create_parameter_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para parámetros.
        """

        fmt = self._create_format(
            "sql_parameter_color",
        )

        self._add_rule(
            r":[A-Za-z_]\w*",
            fmt,
        )

        self._add_rule(
            r"\$\d+",
            fmt,
        )

        self._add_rule(
            r"\?",
            fmt,
        )

    def _create_variable_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para variables.
        """

        fmt = self._create_format(
            "sql_variable_color",
        )

        self._add_rule(
            r"@@[A-Za-z_]\w*",
            fmt,
        )

        self._add_rule(
            r"@[A-Za-z_]\w*",
            fmt,
        )

    def _create_identifier_rules(
        self,
    ) -> None:
        """
        Registra las reglas de resaltado para identificadores delimitados.
        """

        fmt = self._create_format(
            "sql_identifier_color",
        )

        self._add_rule(
            r'"[^"]*"',
            fmt,
            protected=True,
        )

        self._add_rule(
            r"`[^`]*`",
            fmt,
            protected=True,
        )

        self._add_rule(
            r"\[[^\]]+\]",
            fmt,
            protected=True,
        )

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
            "sql_comment_color",
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
