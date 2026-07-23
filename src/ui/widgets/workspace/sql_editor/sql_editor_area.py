from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFileDialog,
    QInputDialog,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QWidget,
)

from entities.file import File
from entities.message_type import MessageType
from entities.sql_scope import SqlScope
from modules.files import service as files_service
from ui.app.app_actions import notify
from ui.utils.layouts import vbox
from ui.widgets.dialogs.confirmation_dialog import ConfirmationDialog
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

        # Ctrl + N: Nuevo editor.
        shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_new.setContext(Qt.ShortcutContext.WindowShortcut)
        shortcut_new.activated.connect(self._on_new_file_requested)

        # Ctrl + W: Cerrar editor actual.
        shortcut_close = QShortcut(QKeySequence("Ctrl+W"), self)
        shortcut_close.setContext(Qt.ShortcutContext.WindowShortcut)
        shortcut_close.activated.connect(self._on_close_current_file_requested)

        # Ctrl + O: Abrir archivo desde disco.
        shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut_open.setContext(Qt.ShortcutContext.WindowShortcut)
        shortcut_open.activated.connect(self._on_open_file_requested)

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

        self.toolbar.open_file_requested.connect(
            self._on_open_file_requested,
        )

        self.toolbar.save_file_requested.connect(
            self._on_save_file_requested,
        )

        self.toolbar.rename_file_requested.connect(
            self._on_rename_file_requested,
        )

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

    def _on_open_file_requested(
        self,
    ) -> None:
        """
        Abre un archivo existente desde disco.
        """

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "SQL Files (*.sql);;Text Files (*.txt);;All Files (*)",
        )

        if not path:
            return

        file = files_service.open_file(
            Path(path),
        )

        if file is None:
            notify(
                message_type=MessageType.ERROR,
                message="File not opened.\nSee logs for details.",
            )
            return

        for opened_file in self.files:
            if opened_file.path == file.path:
                self._show_editor(opened_file)
                return

        self._add_file_and_editor(file)

    def _on_save_file_requested(
        self,
        file: File | None = None,
    ) -> None:
        """
        Guarda un archivo en disco.

        Si no se proporciona un archivo concreto, guarda el archivo
        asociado al editor actualmente activo.

        Si el archivo todavía no tiene una ruta asociada, muestra el
        diálogo de guardado para que el usuario seleccione la ubicación
        y el nombre del archivo antes de guardar.

        Args:
            file (File | None):
                Archivo que debe guardarse. Si es `None`, se utiliza
                el archivo del editor activo.
        """

        if file is not None:
            editor = self._get_editor(file)
        else:
            editor = self._get_current_editor()

        if editor is None:
            return

        file = editor.file

        if file.path is None:

            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save file",
                "",
                "SQL Files (*.sql);;Text Files (*.txt);;All Files (*)",
            )

            if not path:
                return

            file.change_path(
                Path(path),
            )

        else:
            if not file.has_changes:
                notify(
                    message_type=MessageType.WARNING,
                    message="There is no changes to save.",
                )
                return

        if files_service.save_file(file):
            self.files_list.refresh_file(file)
            notify(
                message_type=MessageType.SUCCESS,
                message="File changes saved.",
            )
        else:
            notify(
                message_type=MessageType.ERROR,
                message="File changes not saved.\nSee logs for details.",
            )

    def _on_rename_file_requested(
        self,
        file_from_editor: File | None = None,
    ) -> None:
        """
        Renombra el archivo actualmente activo.

        Args:
            file_from_editor (File | None):
                Archivo que debe renombrarse.
                Este argumetto se usa para que funcione el atajo
                de teclado que se activa desde el editor sql.
        """

        if file_from_editor is not None:
            editor = self._get_editor(file_from_editor)
        else:
            editor = self._get_current_editor()

        if editor is None:
            return

        file = editor.file

        # Instanciamos el diálogo
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Rename file")
        dialog.setLabelText("New file name:")
        dialog.setTextValue(file.name)

        # Quitamos los bordes y la barra de título nativa del sistema operativo.
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        # Márgenes internos y espaciado entre widgets.
        if dialog.layout():
            dialog.layout().setContentsMargins(
                20, 20, 20, 20
            )  # (izquierda, arriba, derecha, abajo)
            dialog.layout().setSpacing(12)  # espacio vertical entre elementos.

        # Aplicar estilos y centrar cuando ya
        # se haya renderizado el tamaño final.
        def _setup_dialog():
            self._apply_rename_file_dialog_button_styles(dialog)
            self._center_rename_file_dialog_on_parent(
                dialog=dialog,
                parent=self,
            )

        # QTimer.singleShot con 0ms ejecuta la función en el
        # siguiente ciclo de eventos, justo cuando el diálogo
        # ya terminó de construir sus widgets internos.
        QTimer.singleShot(
            0,
            lambda: _setup_dialog,
        )

        # Ejecutar el diálogo.
        if not dialog.exec():
            return

        new_name = dialog.textValue().strip()

        if not new_name:
            return

        file.rename(new_name)

        self.files_list.refresh_file(file)

    # =====================
    # === EVENT HELPERS ===
    # =====================

    @staticmethod
    def _apply_rename_file_dialog_button_styles(
        dialog: QInputDialog,
    ) -> None:
        """
        Aplica las propiedades QSS a los botones
        una vez dibujado el diálogo.

        Args:
            dialog (QInputDialog):
                Diálogo para renombrar el archivo.
        """

        for btn in dialog.findChildren(QPushButton):

            parent = btn.parent()

            if isinstance(parent, QDialogButtonBox):

                # 1. Quitamos la letra subrayada/acelerador de teclado.
                btn.setText(btn.text().replace("&", ""))

                # 2. Asignamos la propiedad QSS según el rol
                role = parent.buttonRole(btn)

                if role == QDialogButtonBox.ButtonRole.AcceptRole:
                    btn.setProperty(
                        "type",
                        "primary",
                    )

                elif role == QDialogButtonBox.ButtonRole.RejectRole:
                    btn.setProperty(
                        "type",
                        "danger",
                    )

                # 3. Refrescamos el estilo
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    @staticmethod
    def _center_rename_file_dialog_on_parent(
        dialog: QInputDialog,
        parent: QWidget,
    ) -> None:
        """
        Calcula y aplica la posición centrada
        del diálogo respecto a su padre.

        Args:
            dialog (QInputDialog):
                Diálogo para renombrar el archivo.

            parent (QWidget):
                Widget padre del diálogo.
        """

        if parent and dialog.isVisible():

            # Obtenemos la geometría de la ventana principal.
            parent_geo = parent.geometry()

            # Calculamos las coordenadas x, y centradas.
            x = parent_geo.x() + (parent_geo.width() - dialog.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - dialog.height()) // 2

            dialog.move(x, y)

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
        editor.save_changes.connect(self._on_save_file_requested)
        editor.rename_file.connect(self._on_rename_file_requested)

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

        if file.has_changes:
            dialog = ConfirmationDialog(
                title="Close file",
                message=(
                    "⚠️ <b>Discard unsaved changes?</b> ⚠️<br><br>"
                    f"The file <code>{file.name}</code> has unsaved changes.<br>"
                    "If you continue, you will lose these changes and this action cannot be undone."
                ),
                parent=self,
            )

            # Si el usuario cancela o cierra el diálogo, se interrumpe el flujo
            if not dialog.exec():
                return

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

    # ==================
    # === PUBLIC API ===
    # ==================

    def get_unsaved_changes_count(
        self,
    ) -> int:
        """
        Devuelve el número de archivos abiertos que tienen
        cambios sin guardar/procesar.

        Returns:
            int:
                Cantidad de archivos con cambios pendientes.
        """

        return sum(1 for file in self.files if file.has_changes and file.existsOnDisk)
