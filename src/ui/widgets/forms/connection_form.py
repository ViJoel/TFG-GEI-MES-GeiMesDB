from PySide6.QtCore import (
    QRegularExpression,
    Qt,
    Signal,
)
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from entities.connection import Connection
from entities.driver import Driver
from entities.message_type import MessageType
from log.app_logger import get_logger
from modules.connections.service import (
    create_connection,
    update_connection,
)
from modules.sessions.service import test_connection
from ui.app.app_actions import notify
from ui.app.app_context import AppContext
from ui.app.worker_error import WorkerError
from ui.translations.translation_manager import TranslationManager
from ui.utils.layouts import (
    hbox,
    vbox,
)

logger = get_logger(__name__)


class ConnectionForm(QWidget):
    """
    Formulario encargado de crear y editar
    conexiones de bases de datos.

    Responsabilidades:
    - Gestionar la entrada de datos de conexión.
    - Adaptar la interfaz al driver seleccionado.
    - Validar la información introducida.
    - Comprobar la conectividad con la base de datos.
    - Persistir conexiones nuevas o existentes.
    - Emitir eventos relacionados con la navegación
      y el guardado.
    """

    # =================
    # === VARIABLES ===
    # =================

    connection_saved = Signal()
    cancel_requested = Signal()

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el formulario de conexiones.
        """

        super().__init__()

        self.setObjectName("connection_form")

        # Conexión actualmente cargada en edición.
        self.current_connection: Connection | None = None

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(
        self,
    ) -> None:
        """
        Construye la interfaz principal
        del formulario.
        """

        self.setFixedWidth(480)

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        main_layout = vbox(
            ml=32,
            mt=24,
            mr=32,
            mb=24,
            sp=16,
        )
        self.setLayout(main_layout)

        self._build_form_title(main_layout)

        self._build_form_fields(main_layout)

        main_layout.addStretch()

        self._build_action_buttons(main_layout)

        self._retranslate_ui()

        self.setFixedHeight(self.sizeHint().height())

        # Aplicar estado visual inicial.
        self._update_fields_visibility()

    def _retranslate_ui(
        self,
    ) -> None:
        """
        Actualiza todos los textos traducibles del widget.

        Los textos se generan en el momento de la llamada
        utilizando el traductor activo de Qt, permitiendo
        refrescar la interfaz después de cambiar el idioma
        de la aplicación.
        """

        # Título.

        self.title_label.setText(
            self.tr("Connection form"),
        )

        # Labels del formulario.

        self._name_field_label.setText(
            self.tr("Name"),
        )

        self.name_input.setPlaceholderText(
            self.tr("My personal DB"),
        )

        self._driver_field_label.setText(
            self.tr("Driver"),
        )

        self._host_field_label.setText(
            self.tr("Host"),
        )

        self._port_field_label.setText(
            self.tr("Port"),
        )

        self._database_field_label.setText(
            self.tr("Database"),
        )

        self._username_field_label.setText(
            self.tr("Username"),
        )

        self._password_field_label.setText(
            self.tr("Password"),
        )

        self.path_input_label.setText(
            self.tr("Path to the file"),
        )

        self.path_input.setPlaceholderText(
            self.tr("/path/to/the/file.db"),
        )

        # Botón de buscar del path input.

        self.browse_button.setText(
            self.tr("Browse"),
        )

        # Botones de acción.

        self.test_connection_button.setText(
            self.tr("Test connection"),
        )

        self.cancel_button.setText(
            self.tr("Cancel"),
        )

        self.save_button.setText(
            self.tr("Save"),
        )

    def _build_form_title(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el título principal
        del formulario.

        Args:
            parent_layout:
                Layout padre que contendrá el widget.
        """

        self.title_label = QLabel()

        self.title_label.setObjectName("connection_form_title")

        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        parent_layout.addWidget(self.title_label)

    def _build_form_fields(
        self,
        parent_layout,
    ) -> None:
        """
        Construye y registra todos los
        campos editables del formulario.

        Args:
            parent_layout:
                Layout padre que contendrá el widget.
        """

        inputs_layout = vbox(sp=16)
        inputs_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._build_name_field(inputs_layout)
        self._build_driver_field(inputs_layout)

        layout_1 = hbox(sp=8)
        inputs_layout.addLayout(layout_1)

        self._build_host_field(layout_1)
        self._build_port_field(layout_1)

        self._build_database_field(inputs_layout)

        layout_2 = hbox(sp=8)
        inputs_layout.addLayout(layout_2)

        self._build_username_field(layout_2)
        self._build_password_field(layout_2)

        self._build_path_field(inputs_layout)

        parent_layout.addLayout(inputs_layout)

        # Campos visibles únicamente para
        # drivers basados en red.
        self.network_fields = [
            self.host_field,
            self.port_field,
            self.database_field,
            self.username_field,
            self.password_field,
        ]

        # Campos exclusivos de SQLite.
        self.sqlite_fields = [
            self.path_field,
        ]

    # ================
    # === UI STATE ===
    # ================

    def _update_fields_visibility(
        self,
    ) -> None:
        """
        Actualiza la visibilidad de los campos
        según el driver seleccionado.

        SQLite utiliza archivo local,
        mientras que el resto de drivers
        requieren configuración de red.
        """

        selected_driver = self.driver_input.currentText()

        is_sqlite = selected_driver == Driver.SQLITE.value

        # Campos de conexiones remotas.
        for field in self.network_fields:
            field.setVisible(not is_sqlite)

        # Campos exclusivos de SQLite.
        for field in self.sqlite_fields:
            field.setVisible(is_sqlite)

    # ==================
    # === UI HELPERS ===
    # ==================

    def _create_input_label(
        self,
    ) -> QLabel:
        """
        Crea un label reutilizable para
        los campos del formulario.

        Returns:
            QLabel:
                Label configurado.
        """

        label = QLabel()
        label.setObjectName("connection_form_input_label")

        return label

    def _create_input(
        self,
        placeholder: str,
    ) -> QLineEdit:
        """
        Crea un input reutilizable para
        el formulario.

        Args:
            placeholder (str):
                Texto guía mostrado cuando
                el campo está vacío.

        Returns:
            QLineEdit:
                Input configurado.
        """

        input_field = QLineEdit()
        input_field.setObjectName("connection_form_input")
        input_field.setPlaceholderText(placeholder)

        return input_field

    def _build_field(
        self,
        widget: QWidget,
    ) -> tuple[QWidget, QLabel]:
        """
        Construye un campo estándar compuesto por:
        - Contenedor vertical.
        - Etiqueta descriptiva,
        - Widget principal,

        Args:
            widget (QWidget):
                Widget principal del campo.

        Returns:
            tuple[QWidget, QLabel]:
                Contenedor completo del campo y label
                del campo (necesario para traducción).
        """

        field_widget = QWidget()
        field_widget.setObjectName("connection_form_field")

        field_layout = vbox(sp=4)
        field_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        field_widget.setLayout(field_layout)

        field_label = self._create_input_label()

        field_layout.addWidget(field_label)
        field_layout.addWidget(widget)

        return field_widget, field_label

    def _create_button(
        self,
        property_name: str,
        property_value: str,
    ) -> QPushButton:
        """
        Crea un botón del formulario.

        Args:
            property_name (str):
                Nombre de la propiedad QSS.

            property_value (str):
                Valor de la propiedad QSS.

        Returns:
            QPushButton: Botón creado.
        """

        button = QPushButton()

        button.setObjectName("connection_form_button")

        button.setProperty(
            property_name,
            property_value,
        )

        return button

    # ======================
    # === FIELD BUILDERS ===
    # ======================

    def _build_name_field(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el campo de nombre
        de conexión.
        """

        self.name_input = self._create_input("My personal DB")

        self.name_field, self._name_field_label = self._build_field(
            self.name_input,
        )

        parent_layout.addWidget(self.name_field)

    def _build_driver_field(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el selector de driver
        de base de datos.
        """

        self.driver_input = QComboBox()
        self.driver_input.setObjectName("connection_form_input")

        # Registrar drivers disponibles.
        for driver in Driver:
            self.driver_input.addItem(driver.value)

        self.driver_field, self._driver_field_label = self._build_field(
            self.driver_input,
        )

        parent_layout.addWidget(self.driver_field)

    def _build_host_field(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el campo de host.
        """

        self.host_input = self._create_input("255.255.255.255")

        self.host_field, self._host_field_label = self._build_field(
            self.host_input,
        )

        parent_layout.addWidget(self.host_field)

    def _build_port_field(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el campo de puerto.
        """

        self.port_input = self._create_input("12345")

        self._set_port_regex()

        self.port_field, self._port_field_label = self._build_field(
            self.port_input,
        )

        parent_layout.addWidget(self.port_field)

    def _build_database_field(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el campo de nombre
        de base de datos.
        """

        self.database_input = self._create_input("my_database")

        self.database_field, self._database_field_label = self._build_field(
            self.database_input,
        )

        parent_layout.addWidget(self.database_field)

    def _build_username_field(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el campo de usuario.
        """

        self.username_input = self._create_input("admin")

        self.username_field, self._username_field_label = self._build_field(
            self.username_input,
        )

        parent_layout.addWidget(self.username_field)

    def _build_password_field(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el campo de contraseña.
        """

        self.password_input = self._create_input("admin")

        # Ocultar caracteres sensibles.
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_field, self._password_field_label = self._build_field(
            self.password_input,
        )

        parent_layout.addWidget(self.password_field)

    def _build_path_field(
        self,
        parent_layout,
    ) -> None:
        """
        Construye el selector de archivo
        para conexiones SQLite.
        """

        field_widget = QWidget()
        field_widget.setObjectName("connection_form_field")

        field_layout = vbox(sp=4)
        field_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        field_widget.setLayout(field_layout)

        sub_layout = hbox(sp=4)
        field_layout.addLayout(sub_layout)

        self.path_input_label = self._create_input_label()
        sub_layout.addWidget(self.path_input_label)

        sub_layout.addStretch()

        self.browse_button = QPushButton()
        self.browse_button.setProperty(
            "type",
            "accent",
        )
        sub_layout.addWidget(self.browse_button)

        self.path_input = self._create_input("/path/to/the/file.db")

        field_layout.addWidget(self.path_input)

        self.path_field = field_widget

        parent_layout.addWidget(self.path_field)

    def _build_action_buttons(
        self,
        parent_layout,
    ) -> None:
        """
        Construye los botones de acción del formulario.
        """

        buttons_widget = QWidget()
        buttons_widget.setObjectName("connection_form_buttons")

        buttons_layout = hbox()
        buttons_layout.setSpacing(8)

        buttons_widget.setLayout(buttons_layout)

        # Botones
        self.test_connection_button = self._create_button(
            "type",
            "secondary",
        )

        self.cancel_button = self._create_button(
            "type",
            "danger",
        )

        self.save_button = self._create_button(
            "type",
            "primary",
        )

        buttons_layout.addStretch()

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.test_connection_button)
        buttons_layout.addWidget(self.save_button)

        parent_layout.addWidget(buttons_widget)

    # =============
    # === REGEX ===
    # =============

    def _set_port_regex(
        self,
    ) -> None:
        """
        Restringe el campo de puerto
        a valores numéricos válidos
        [0 - 99999].
        """

        regex = QRegularExpression(r"^\d{0,5}$")
        validator = QRegularExpressionValidator(regex, self.port_input)
        self.port_input.setValidator(validator)

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

        self.browse_button.clicked.connect(
            self._select_file,
        )

        self.driver_input.currentTextChanged.connect(
            self._update_fields_visibility,
        )

        self.save_button.clicked.connect(
            self._save_button_clicked,
        )

        self.test_connection_button.clicked.connect(
            self._test_connection_button_clicked,
        )

        self.cancel_button.clicked.connect(
            self._cancel_button_clicked,
        )

        TranslationManager.events().language_changed.connect(
            self._retranslate_ui,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def clear_form(
        self,
    ) -> None:
        """
        Limpia el formulario y restablece
        su estado inicial.
        """

        self.current_connection = None

        self.name_input.clear()
        self.host_input.clear()
        self.port_input.clear()
        self.database_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.path_input.clear()

        self.driver_input.setCurrentIndex(0)

        self._update_fields_visibility()

    def load_connection(
        self,
        connection: Connection,
    ) -> None:
        """
        Carga una conexión existente
        dentro del formulario.

        Args:
            connection (Connection):
                Conexión persistida a editar.
        """

        logger.info(
            f"Loading connection '{connection.name}' (ID: {connection.id}) into form..."
        )

        self.current_connection = connection

        self.name_input.setText(connection.name)
        self.driver_input.setCurrentText(connection.driver.value)

        if connection.driver == Driver.SQLITE:
            self.path_input.setText(connection.path or "")
        else:
            self.host_input.setText(connection.host or "")
            self.port_input.setText(str(connection.port or ""))
            self.database_input.setText(connection.database or "")
            self.username_input.setText(connection.username or "")
            self.password_input.setText(connection.password or "")

        self._update_fields_visibility()

        logger.success(
            f"Connection '{connection.name}' (ID: {connection.id}) loaded into form."
        )

    def _select_file(
        self,
    ) -> None:
        """
        Abre un selector de archivos para
        elegir una base de datos SQLite.
        """

        logger.info("Opening SQLite file selector...")

        # Abrir el selector de archivos
        # El segundo parámetro es el título de la ventana
        # y el cuarto es el filtro de archivos
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select database"),
            "",
            self.tr("Database Files (*.db);;All Files (*)"),
        )

        if file_path:
            logger.success(f"SQLite database file selected: {file_path}")
            self.path_input.setText(file_path)

    def _save_button_clicked(
        self,
    ) -> None:
        """
        Persiste la conexión actual
        del formulario.

        Si existe una conexión previamente
        cargada, se ejecuta una actualización.
        En caso contrario, se crea una nueva
        conexión persistida.
        """

        connection = self._build_connection_from_form()

        logger.info(f"Saving connection '{connection.name}'...")

        try:

            # UPDATE
            if self.current_connection is not None:
                update_connection(connection)

                notify(
                    MessageType.SUCCESS,
                    self.tr("Connection updated."),
                )

            # CREATE
            else:
                create_connection(connection)

                notify(
                    MessageType.SUCCESS,
                    self.tr("Connection saved."),
                )

            logger.success(f"Connection saved '{connection.name}'...")

            self.connection_saved.emit()

            self.clear_form()

        except Exception as e:

            logger.error(
                f"Failed to save connection '{connection.name}'.\nException: {e}"
            )

            notify(
                MessageType.ERROR,
                self.tr("Error saving."),
            )

    def _test_connection_button_clicked(
        self,
    ) -> None:
        """
        Ejecuta un test de conectividad
        utilizando los datos actuales
        del formulario.
        """

        connection = self._build_connection_from_form()

        notify(
            MessageType.WARNING,
            self.tr("Testing connection..."),
        )

        AppContext.get_task_manager().run(
            test_connection,
            connection,
            on_success=lambda _: self._on_test_connection_success,
            on_error=self._on_test_connection_error,
        )

    def _build_connection_from_form(
        self,
    ) -> Connection:
        """
        Construye una entidad `Connection`
        utilizando el estado actual
        del formulario.

        Returns:
            Connection:
                Entidad construida a partir
                de los valores actuales de la UI.
        """

        selected_driver = Driver(self.driver_input.currentText())

        # Reutilizar entidad existente
        # durante edición.
        connection = (
            self.current_connection
            if self.current_connection is not None
            else Connection()
        )

        connection.name = self.name_input.text()
        connection.driver = selected_driver

        if selected_driver == Driver.SQLITE:
            connection.host = None
            connection.port = None
            connection.database = None
            connection.username = None
            connection.password = None
            connection.path = self.path_input.text()

        else:
            connection.host = self.host_input.text()
            connection.port = int(self.port_input.text())
            connection.database = self.database_input.text()
            connection.username = self.username_input.text()
            connection.password = self.password_input.text()
            connection.path = None

        return connection

    def _cancel_button_clicked(
        self,
    ) -> None:
        """
        Cancela la edición actual y solicita
        volver a la pantalla anterior.
        """

        logger.info("Connection form cancelled.")

        self.clear_form()
        self.cancel_requested.emit()

    # =====================
    # === EVENT HELPERS ===
    # =====================

    def _on_test_connection_success(
        self,
        success: bool,
    ) -> None:

        if success:

            notify(
                MessageType.SUCCESS,
                self.tr("Connection successful."),
            )

        else:

            notify(
                MessageType.ERROR,
                self.tr("Connection failed."),
            )

    def _on_test_connection_error(
        self,
        error: WorkerError,
    ) -> None:

        logger.error(error.traceback)

        notify(
            MessageType.ERROR,
            self.tr("Invalid connection data."),
        )
