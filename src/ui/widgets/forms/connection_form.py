import logging

from PySide6.QtCore import QRegularExpression, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from model.entities.connection import Connection
from model.entities.driver import Driver
from service.connections.service import create_connection
from ui.utils.layouts import hbox, vbox
from ui.widgets.notifications.notification import Notification
from ui.widgets.notifications.notifications_type import NotificationType
from ui.widgets.sidebar.connections_list import ConnectionsList

# Crear sub-logger
logger = logging.getLogger(__name__)


class ConnectionForm(QWidget):

    # Señales
    connection_saved = Signal()

    # ============
    # === INIT ===
    # ============

    def __init__(self):
        super().__init__()

        self._setup_ui()
        self._connect_signals()

    # ================
    # === UI SETUP ===
    # ================

    def _setup_ui(self) -> None:
        # Layout vertical principal
        main_layout = vbox()
        self.setLayout(main_layout)

        # Título del formulario
        self._set_form_title(main_layout, "Connection form")

        # Inputs del formulario
        self._set_form_inputs(main_layout)

        # Botones del formulario
        self._build_action_buttons(main_layout)

        # Aplicar estado inicial del formulario
        self._update_fields_visibility()

    def _set_form_title(self, parent_layout, title_text: str) -> None:
        """
        Establece el título del formulario.

        Args:
            title_text (str): Texto que aparecerá en el título.
        """

        # Crear el label
        title_label = QLabel()

        # Establecer el texto
        title_label.setText(title_text)

        # Añadir al layout principal
        parent_layout.addWidget(title_label)

    def _set_form_inputs(self, parent_layout) -> None:
        """
        Función para establecer los inputs del formulario.
        """

        # Layout vertical
        inputs_layout = vbox()

        # Establecer inputs
        self._build_name_field(inputs_layout)  # Nombre
        self._build_driver_field(inputs_layout)  # Driver
        self._build_host_field(inputs_layout)  # Host
        self._build_port_field(inputs_layout)  # Puerto
        self._build_database_field(inputs_layout)  # Base de datos
        self._build_username_field(inputs_layout)  # Nombre de usuario
        self._build_password_field(inputs_layout)  # Contraseña
        self._build_path_field(inputs_layout)  # Ruta al archivo .db para SQLite

        # Añadir el layout de inputs al layout principal
        parent_layout.addLayout(inputs_layout)

        # Campos para conexiones en red
        self.network_fields = [
            self.host_field,
            self.port_field,
            self.database_field,
            self.username_field,
            self.password_field,
        ]

        # Campos exclusivos de SQLite
        self.sqlite_fields = [
            self.path_field,
        ]

    # ======================
    # === FIELD BUILDERS ===
    # ======================

    def _build_name_field(self, parent_layout) -> None:
        self.name_input = self._create_input("My personal DB")

        self.name_field = self._build_field("Name", self.name_input)

        parent_layout.addWidget(self.name_field)

    def _build_driver_field(self, parent_layout) -> None:
        self.driver_input = QComboBox()

        # Añadir drivers del Enum
        for driver in Driver:
            self.driver_input.addItem(driver.value)

        self.driver_field = self._build_field(
            "Driver",
            self.driver_input,
        )

        parent_layout.addWidget(self.driver_field)

    def _build_host_field(self, parent_layout) -> None:
        self.host_input = self._create_input("255.255.255.255")

        self.host_field = self._build_field(
            "Host",
            self.host_input,
        )

        parent_layout.addWidget(self.host_field)

    def _build_port_field(self, parent_layout) -> None:
        self.port_input = self._create_input("12345")

        self._set_port_regex()

        self.port_field = self._build_field(
            "Port",
            self.port_input,
        )

        parent_layout.addWidget(self.port_field)

    def _build_database_field(self, parent_layout) -> None:
        self.database_input = self._create_input("my_database")

        self.database_field = self._build_field(
            "Database",
            self.database_input,
        )

        parent_layout.addWidget(self.database_field)

    def _build_username_field(self, parent_layout) -> None:
        self.username_input = self._create_input("admin")

        self.username_field = self._build_field(
            "Username",
            self.username_input,
        )

        parent_layout.addWidget(self.username_field)

    def _build_password_field(self, parent_layout) -> None:
        self.password_input = self._create_input("admin")

        # Configurar para que oculte los caracteres de la contraseña
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_field = self._build_field(
            "Password",
            self.password_input,
        )

        parent_layout.addWidget(self.password_field)

    def _build_path_field(self, parent_layout) -> None:
        self.path_input = self._create_input("/path/to/the/file.db")
        self.browse_button = QPushButton("Browse...")

        file_selection_widget = QWidget()

        file_selection_layout = hbox()
        file_selection_widget.setLayout(file_selection_layout)

        file_selection_layout.addWidget(self.path_input)
        file_selection_layout.addWidget(self.browse_button)

        self.path_field = self._build_field(
            "Path to the file",
            file_selection_widget,
        )

        parent_layout.addWidget(self.path_field)

    def _build_action_buttons(self, parent_layout) -> None:
        """
        Construye los botones de acción del formulario.
        """

        # Widget contenedor
        buttons_widget = QWidget()

        # Layout horizontal
        buttons_layout = hbox()
        buttons_widget.setLayout(buttons_layout)

        # Botones
        self.test_connection_button = QPushButton("Test connection")
        self.save_button = QPushButton("Save")

        # Añadir widgets
        buttons_layout.addWidget(self.test_connection_button)

        # Empuja el siguiente botón al extremo derecho
        buttons_layout.addStretch()

        buttons_layout.addWidget(self.save_button)

        # Añadir al layout padre
        parent_layout.addWidget(buttons_widget)

    # ===============
    # === HELPERS ===
    # ===============

    def _create_input_label(self, label_text: str) -> QLabel:
        """
        Función reutilizable para crear los labels de los inputs
        del formulario.

        Args:
            label_text (str): Texto que aparecerá en el label.

        Returns:
            QLabel: Widget que se crea.
        """

        label = QLabel()
        label.setText(label_text)
        return label

    def _create_input(self, placeholder: str) -> QLineEdit:
        """
        Función reutilizable para crear los inputs del formulario.

        Args:
            placeholder (str): Texto guía que aparece de fondo
                                cuando no hay nada escrito.

        Returns:
            QLineEdit: Widget que se crea.
        """

        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        return input_field

    def _build_field(self, label_text, widget) -> QWidget:
        """
        Construye un campo estándar del formulario compuesto por:
        - Contenedor vertical.
        - Label.
        - Widget principal.

        Args:
            label_text (str): Texto que aparecerá en el label.
            widget: Widget principal del campo.

        Returns:
            QWidget: Contenedor completo del campo.
        """

        field_widget = QWidget()

        field_layout = vbox()
        field_widget.setLayout(field_layout)

        # Label principal
        field_label = self._create_input_label(label_text)

        # Añadir widgets
        field_layout.addWidget(field_label)
        field_layout.addWidget(widget)

        return field_widget

    # =============
    # === REGEX ===
    # =============

    def _set_port_regex(self):
        # Expresión regular que valide: "solo números (\d) entre 0 y 5 veces ({0,5})"
        regex = QRegularExpression(r"^\d{0,5}$")
        validator = QRegularExpressionValidator(regex, self.port_input)
        self.port_input.setValidator(validator)

    # ===============
    # === SIGNALS ===
    # ===============

    def _connect_signals(self) -> None:
        self.browse_button.clicked.connect(self._select_file)

        self.driver_input.currentTextChanged.connect(self._update_fields_visibility)

        self.save_button.clicked.connect(
            self._save_button_clicked,
        )

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _select_file(self) -> None:
        # Abrir el selector de archivos
        # El segundo parámetro es el título de la ventana y el cuarto es el filtro de archivos
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar base de datos",
            "",
            "Archivos de Base de Datos (*.db);;Todos los archivos (*)",
        )

        # Si el usuario seleccionó un archivo (no canceló la ventana), lo ponemos en el input
        if file_path:
            self.path_input.setText(file_path)

    def _save_button_clicked(self) -> None:

        # Extraer datos del formulario
        selected_driver = Driver(self.driver_input.currentText())

        connection = Connection(
            name=self.name_input.text(),
            driver=selected_driver,
        )
        if selected_driver == Driver.SQLITE:
            connection.path = self.path_input.text()
        else:
            connection.host = self.host_input.text()
            connection.port = int(self.port_input.text())
            connection.database = self.database_input.text()
            connection.username = self.username_input.text()
            connection.password = self.password_input.text()

        # Guardar conexión
        try:
            create_connection(connection)

            # Crear log
            logger.info(f"Conexión guardada con éxito: {connection}")

            # Mostrar notificación
            notification = Notification(
                NotificationType.SUCCESS,
                "Connection saved",
                parent=self.window(),
            )
            notification.show()

            # Emitir señal
            self.connection_saved.emit()

        # Notificar si falla al guardar
        except Exception as e:
            # Crear log
            logger.error(f"Error al guardar conexión: {connection}. Excepción: {e}")

            # Mostrar notificación
            notification = Notification(
                NotificationType.ERROR,
                "Error saving",
                parent=self.window(),
            )
            notification.show()

    # ================
    # === UI STATE ===
    # ================

    def _update_fields_visibility(self) -> None:
        """
        Muestra u oculta campos dependiendo
        del driver seleccionado.
        """

        selected_driver = self.driver_input.currentText()

        is_sqlite = selected_driver == Driver.SQLITE.value

        # Campos de red
        for field in self.network_fields:
            field.setVisible(not is_sqlite)

        # Campos SQLite
        for field in self.sqlite_fields:
            field.setVisible(is_sqlite)
