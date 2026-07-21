from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QWidget,
)

from entities.file import File
from entities.sql_scope import SqlScope
from ui.utils.layouts import (
    vbox,
)
from ui.widgets.workspace.sql_editor.files_list import FilesList
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor
from ui.widgets.workspace.sql_editor.toolbar import Toolbar


class SqlEditorArea(QWidget):
    """
    Área de trabajo del editor SQL.

    Gestiona los archivos abiertos, sus editores asociados
    y la coordinación entre la barra de herramientas, la
    lista de archivos y el editor activo.
    """

    # =================
    # === VARIABLES ===
    # =================

    execute_requested = Signal(
        list,
        object,
    )

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el área del editor SQL.
        """

        super().__init__()

        self.setObjectName("sql_editor_area")

        self.files: list[File] = []

        self._setup_ui()
        self._connect_signals()
        self._setup_shortcuts()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """

        layout = vbox(sp=8)
        self.setLayout(layout)

        self.toolbar = Toolbar()
        layout.addWidget(self.toolbar)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(True)

        self.files_list = FilesList()
        self.files_list.setMinimumWidth(0)
        self.splitter.addWidget(self.files_list)

        self.editors = QStackedWidget()
        self.splitter.addWidget(self.editors)

        # 1. Todo el espacio sobrante de la ventana va para el editor (índice 1)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        # 2. Tamaño inicial en píxeles reales
        self.splitter.setSizes([200, 800])

        layout.addWidget(
            self.splitter,
            1,
        )

    def _setup_shortcuts(
        self,
    ) -> None:
        """
        Configura atajos de teclado globales que funcionan
        incluso si no hay editores abiertos.
        """

        # Ctrl + N: Nuevo editor
        shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_new.setContext(Qt.ShortcutContext.WindowShortcut)
        shortcut_new.activated.connect(self._on_new_file_requested)

        # Ctrl + W: Cerrar editor actual
        shortcut_close = QShortcut(QKeySequence("Ctrl+W"), self)
        shortcut_close.setContext(Qt.ShortcutContext.WindowShortcut)
        shortcut_close.activated.connect(self._on_close_current_file_requested)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(
        self,
    ) -> None:
        """
        Conecta señales de widgets
        con sus handlers correspondientes.
        """

        self.toolbar.undo_requested.connect(self._undo_current)

        self.toolbar.redo_requested.connect(self._redo_current)

        self.toolbar.execute_selection_requested.connect(self._execute_selection)

        self.toolbar.execute_query_requested.connect(self._execute_query)

        self.toolbar.execute_script_requested.connect(self._execute_script)

        self.toolbar.new_file_requested.connect(self._on_new_file_requested)

        self.files_list.file_selected.connect(
            self._show_editor,
        )

        self.files_list.file_close_requested.connect(self._remove_file_and_editor)

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _undo_current(
        self,
    ) -> None:
        """
        Deshace la última modificación del editor activo.
        """

        if editor := self._get_current_editor():
            editor.undo()

    def _redo_current(
        self,
    ) -> None:
        """
        Rehace la última modificación deshecha
        en el editor activo.
        """

        if editor := self._get_current_editor():
            editor.redo()

    def _execute_selection(
        self,
    ) -> None:
        """
        Ejecuta el texto seleccionado en el editor activo.
        """

        if editor := self._get_current_editor():
            editor.execute(SqlScope.SELECTED_TEXT)

    def _execute_query(
        self,
    ) -> None:
        """
        Ejecuta la consulta situada bajo el cursor
        del editor activo.
        """

        if editor := self._get_current_editor():
            editor.execute(SqlScope.ACTUAL_QUERY)

    def _execute_script(
        self,
    ) -> None:
        """
        Ejecuta el contenido completo del editor activo.
        """

        if editor := self._get_current_editor():
            editor.execute(SqlScope.FULL_SCRIPT)

    def _on_new_file_requested(
        self,
    ) -> None:
        """
        Crea un nuevo archivo y su editor asociado.
        """

        self._add_file_and_editor(file=File())

    def _on_close_current_file_requested(
        self,
    ) -> None:
        """
        Cierra el archivo correspondiente al editor activo.
        """

        if editor := self._get_current_editor():
            self._remove_file_and_editor(editor.file)

    # ===================
    # === PRIVATE API ===
    # ===================

    def _add_file_and_editor(
        self,
        file: File,
    ) -> None:
        """
        Añade un archivo al área de trabajo y crea
        su editor asociado.

        Args:
            file (File):
                Archivo que debe abrirse.
        """

        editor = SqlEditor(file=file)
        editor.execute_requested.connect(self.execute_requested)
        editor.file_modified.connect(self.files_list.refresh_file)

        self.files.append(file)

        self.files_list.add_file(file)

        self.editors.addWidget(editor)
        self.editors.setCurrentWidget(editor)

    def _remove_file_and_editor(
        self,
        file: File,
    ) -> None:
        """
        Elimina un archivo abierto junto con su editor
        asociado.

        Args:
            file (File):
                Archivo que debe cerrarse.
        """

        editor = self._get_editor(file)

        if editor is None:
            return

        was_current = editor is self._get_current_editor()

        self.files_list.remove_file(file)

        self.editors.removeWidget(editor)
        editor.deleteLater()

        self.files.remove(file)

        if was_current:
            self.files_list.select_first_file()

    def _get_editor(
        self,
        file: File,
    ) -> SqlEditor | None:
        """
        Obtiene el editor asociado a un archivo.

        Args:
            file (File):
                Archivo cuyo editor se desea obtener.

        Returns:
            SqlEditor | None:
                Editor asociado al archivo o `None`
                si no existe.
        """

        for i in range(self.editors.count()):

            editor = self.editors.widget(i)

            if editor.file is file:
                return editor

        return None

    def _show_editor(
        self,
        file: File,
    ) -> None:
        """
        Muestra el editor asociado al archivo indicado.

        Args:
            file (File):
                Archivo cuyo editor debe mostrarse.
        """

        editor = self._get_editor(file)

        if editor is not None:
            self.editors.setCurrentWidget(editor)

    def _get_current_editor(
        self,
    ) -> SqlEditor | None:
        """
        Devuelve el editor actualmente activo.

        Returns:
            SqlEditor | None:
                Editor activo o `None` si no existe ninguno.
        """

        return self.editors.currentWidget()

    # ==================
    # === PUBLIC API ===
    # ==================

    def set_query_text(
        self,
        text: str,
    ) -> None:
        """
        Inserta el texto SQL proporcionado dentro del editor
        en la posición actual del cursor.

        Args:
            text (str):
                Texto a insertar.
        """

        self._get_current_editor().insert_query_at_cursor(text)
