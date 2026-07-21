from PySide6.QtCore import (
    QSize,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
)

from entities.file import File
from ui.widgets.workspace.sql_editor.files_list_item import FilesListItem


class FilesList(QListWidget):
    """
    Lista de archivos abiertos que permite seleccionar,
    cerrar y actualizar su representación visual.
    """

    # =================
    # === VARIABLES ===
    # =================

    file_selected = Signal(File)
    file_close_requested = Signal(File)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa la lista de archivos abiertos.
        """

        super().__init__()

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal del widget.
        """

        self.setObjectName("files_list")

        self.setSpacing(2)

        # Velocidad del scroll vertical.
        self.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel,
        )
        self.verticalScrollBar().setSingleStep(10)

        # Velocidad del scroll horizontal.
        self.setHorizontalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel,
        )
        self.horizontalScrollBar().setSingleStep(10)

        # Elimina el foco de teclado.
        # Usado para eliminar el rectángulo
        # de selección que viene por defecto.
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Permitir expansión vertical y horizontal.
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        # Ancho mínimo
        self.setMinimumWidth(200)

    # ================
    # === UI STATE ===
    # ================

    def _update_items_selection_state(self):
        """
        Actualiza el estado de selección
        de los items de la lista.
        """

        for i in range(self.count()):

            item = self.item(i)

            widget: FilesListItem = self.itemWidget(item)

            widget.set_selected(item == self.currentItem())

    def _sync_selection_state(
        self,
    ) -> None:
        """
        Sincroniza el estado visual de los elementos.
        """

        self._update_items_selection_state()

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

        self.currentItemChanged.connect(
            self._on_current_item_changed,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _on_current_item_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        """
        Notifica el cambio del archivo actualmente seleccionado.

        Args:
            current (QListWidgetItem | None):
                Elemento actualmente seleccionado.
            previous (QListWidgetItem | None):
                Elemento previamente seleccionado.
        """

        if current is None:
            return

        current_widget: FilesListItem = self.itemWidget(current)
        previous_widget: FilesListItem = self.itemWidget(previous)

        current_widget.set_selected(True)
        previous_widget.set_selected(False)

        self._sync_selection_state()

        self.file_selected.emit(current_widget.file)

    def _on_item_close_requested(
        self,
        item: FilesListItem,
    ) -> None:
        """
        Propaga la solicitud de cierre de un archivo.

        Args:
            item (FilesListItem):
                Elemento cuya clausura ha sido solicitada.
        """

        self.file_close_requested.emit(item.file)

    # ===================
    # === PRIVATE API ===
    # ===================

    def _sort_list(
        self,
    ) -> None:
        """
        Ordena los elementos de la lista alfabéticamente
        por el texto del atributo file_name_label de sus
        widgets internos.
        """

        # 1. Desconectar la señal temporalmente para evitar
        # que el ordenamiento dispare eventos innecesarios
        # mientras movemos los items.
        self.currentItemChanged.disconnect(self._on_current_item_changed)

        # 2. Recolectar todos los items junto con el texto
        # de su widget interno.
        items_data = []

        for i in range(self.count()):

            item = self.item(i)
            widget: FilesListItem = self.itemWidget(item)

            if widget and hasattr(widget, "file_name_label"):
                # Extrae el texto del QLabel
                # (.lower() para no distinguir mayúsculas).
                text_to_sort = widget.file_name_label.text().lower()
                items_data.append((text_to_sort, item, widget))

        # 3. Ordenar la lista de tuplas por el texto extraído.
        items_data.sort(key=lambda x: x[0])

        # 4. Reorganizar los elementos en el QListWidget.
        # Desanclamos los widgets y los items sin destruirlos,
        # para luego reinsertarlos.
        for _, item, widget in items_data:

            # Tomamos el item de su posición actual.
            row = self.row(item)
            self.takeItem(row)

            # Lo añadimos al final (que ahora irá construyendo
            # el nuevo orden).
            self.addItem(item)

            # Volvemos a asignar el widget personalizado al
            # item insertado.
            self.setItemWidget(item, widget)

        # 5. Volver a conectar la señal.
        self.currentItemChanged.connect(self._on_current_item_changed)

    # ==================
    # === PUBLIC API ===
    # ==================

    def select_first_file(
        self,
    ) -> None:
        """
        Selecciona el primer archivo de la lista, si existe.
        """

        if self.count() > 0:
            self.setCurrentRow(0)

    def add_file(
        self,
        file: File,
    ) -> None:
        """
        Añade un archivo a la lista y crea su representación visual.

        Args:
            file (File):
                Archivo que debe añadirse.
        """

        widget = FilesListItem(file)
        widget.close_requested.connect(self._on_item_close_requested)

        item = QListWidgetItem()
        item.setSizeHint(QSize(0, widget.sizeHint().height()))

        self.addItem(item)
        self.setItemWidget(
            item,
            widget,
        )

        self.setCurrentItem(item)

    def remove_file(
        self,
        file: File,
    ) -> None:
        """
        Elimina un archivo de la lista.

        Args:
            file (File):
                Archivo que debe eliminarse.
        """

        for row in range(self.count()):

            item = self.item(row)

            widget: FilesListItem = self.itemWidget(item)

            if widget.file is file:

                self.takeItem(row)
                del item
                return

    def refresh_file(
        self,
        file: File,
    ) -> None:
        """
        Actualiza la representación visual de un archivo.

        Args:
            file (File):
                Archivo cuya representación debe actualizarse.
        """

        for row in range(self.count()):

            item = self.item(row)

            widget: FilesListItem = self.itemWidget(item)

            if widget.file is file:

                widget.refresh()

                return
