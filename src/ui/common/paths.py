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
CONNECTIONS_LIST_QSS = os.path.join(STYLES_DIR, "connections_list.qss")
FONTS_QSS = os.path.join(STYLES_DIR, "fonts.qss")
SIDEBAR_QSS = os.path.join(STYLES_DIR, "sidebar.qss")
CONFIRMATION_DIALOG_QSS = os.path.join(STYLES_DIR, "confirmation_dialog.qss")

STYLE_FILES = [
    BASE_QSS,
    BUTTONS_QSS,
    CONNECTIONS_LIST_QSS,
    FONTS_QSS,
    SIDEBAR_QSS,
    CONFIRMATION_DIALOG_QSS,
]
