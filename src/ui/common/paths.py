import os

from common.paths import RESOURCE_ROOT

# Recursos
RESOURCES_DIR = os.path.join(RESOURCE_ROOT, "ui", "resources")

# Imágenes
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
APP_LOGO = os.path.join(IMAGES_DIR, "geimesdb_logo.png")
POSTGRESQL_LOGO = os.path.join(IMAGES_DIR, "postgresql_logo.png")
MYSQL_LOGO = os.path.join(IMAGES_DIR, "mysql_logo.png")
SQLITE_LOGO = os.path.join(IMAGES_DIR, "sqlite_logo.png")
ORACLE_LOGO = os.path.join(IMAGES_DIR, "oracle_logo.png")
SETTINGS_ICON = os.path.join(IMAGES_DIR, "settings.png")


# Estilos
STYLES_DIR = os.path.join(RESOURCE_ROOT, "ui", "styles")

BASE_QSS = os.path.join(STYLES_DIR, "base.qss")
BUTTONS_QSS = os.path.join(STYLES_DIR, "buttons.qss")
CONFIRMATION_DIALOG_QSS = os.path.join(STYLES_DIR, "confirmation_dialog.qss")
CONNECTION_FORM_QSS = os.path.join(STYLES_DIR, "connection_form.qss")
CONNECTIONS_LIST_QSS = os.path.join(STYLES_DIR, "connections_list.qss")
CONNECTIONS_LIST_BUTTONS_QSS = os.path.join(STYLES_DIR, "connections_list_buttons.qss")
FONTS_QSS = os.path.join(STYLES_DIR, "fonts.qss")
HOME_QSS = os.path.join(STYLES_DIR, "home.qss")
NOTIFICATIONS_QSS = os.path.join(STYLES_DIR, "notifications.qss")
SIDEBAR_QSS = os.path.join(STYLES_DIR, "sidebar.qss")
SQL_EDITOR_QSS = os.path.join(STYLES_DIR, "sql_editor.qss")
RESULTS_VIEW_QSS = os.path.join(STYLES_DIR, "results_view.qss")
WORKSPACE_QSS = os.path.join(STYLES_DIR, "workspace.qss")


STYLE_FILES = [
    BASE_QSS,
    BUTTONS_QSS,
    CONFIRMATION_DIALOG_QSS,
    CONNECTION_FORM_QSS,
    CONNECTIONS_LIST_QSS,
    CONNECTIONS_LIST_BUTTONS_QSS,
    FONTS_QSS,
    HOME_QSS,
    NOTIFICATIONS_QSS,
    SIDEBAR_QSS,
    SQL_EDITOR_QSS,
    RESULTS_VIEW_QSS,
    WORKSPACE_QSS,
]

ARROW_DOWN_ICON = os.path.join(IMAGES_DIR, "arrow_down.png")
