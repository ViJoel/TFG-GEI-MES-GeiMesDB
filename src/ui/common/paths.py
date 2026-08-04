import os

from common.paths import RESOURCE_ROOT

# ================
# === RECURSOS ===
# ================

RESOURCES_DIR = os.path.join(
    RESOURCE_ROOT,
    "ui",
    "resources",
)

# ================
# === IMÁGENES ===
# ================

IMAGES_DIR = os.path.join(
    RESOURCES_DIR,
    "images",
)

APP_LOGO = os.path.join(
    IMAGES_DIR,
    "geimesdb_logo.png",
)

POSTGRESQL_LOGO = os.path.join(
    IMAGES_DIR,
    "postgresql_logo.png",
)

MYSQL_LOGO = os.path.join(
    IMAGES_DIR,
    "mysql_logo.png",
)

SQLITE_LOGO = os.path.join(
    IMAGES_DIR,
    "sqlite_logo.png",
)

ORACLE_LOGO = os.path.join(
    IMAGES_DIR,
    "oracle_logo.png",
)

SETTINGS_ICON = os.path.join(
    IMAGES_DIR,
    "settings.png",
)

ARROW_DOWN_ICON = os.path.join(
    IMAGES_DIR,
    "arrow_down.png",
)

ARROW_LINE_UP = os.path.join(
    IMAGES_DIR,
    "arrow_line_up.png",
)

ARROW_LINE_DOWN = os.path.join(
    IMAGES_DIR,
    "arrow_line_down.png",
)

# ===============
# === ESTILOS ===
# ===============

STYLES_DIR = os.path.join(RESOURCE_ROOT, "ui", "styles")

BASE_QSS = os.path.join(
    STYLES_DIR,
    "base.qss",
)

BUTTONS_QSS = os.path.join(
    STYLES_DIR,
    "buttons.qss",
)

CONFIRMATION_DIALOG_QSS = os.path.join(
    STYLES_DIR,
    "confirmation_dialog.qss",
)

CONNECTION_FORM_QSS = os.path.join(
    STYLES_DIR,
    "connection_form.qss",
)

CONNECTIONS_LIST_QSS = os.path.join(
    STYLES_DIR,
    "connections_list.qss",
)

CONNECTIONS_LIST_BUTTONS_QSS = os.path.join(
    STYLES_DIR,
    "connections_list_buttons.qss",
)

CONNECTION_QUERIES_HISTORY_QSS = os.path.join(
    STYLES_DIR,
    "connection_queries_history.qss",
)

FILES_LIST_QSS = os.path.join(
    STYLES_DIR,
    "files_list.qss",
)

FILES_LIST_ITEM_QSS = os.path.join(
    STYLES_DIR,
    "files_list_item.qss",
)

FONTS_QSS = os.path.join(
    STYLES_DIR,
    "fonts.qss",
)

HOME_QSS = os.path.join(
    STYLES_DIR,
    "home.qss",
)

NAVIGATION_TREE_QSS = os.path.join(
    STYLES_DIR,
    "navigation_tree.qss",
)

NAVIGATION_TREE_CONTEXT_MENU_QSS = os.path.join(
    STYLES_DIR,
    "navigation_tree_context_menu.qss",
)

NOTIFICATIONS_QSS = os.path.join(
    STYLES_DIR,
    "notifications.qss",
)

RENAME_FILE_DIALOG_QSS = os.path.join(
    STYLES_DIR,
    "rename_file_dialog.qss",
)

RESULTS_VIEW_QSS = os.path.join(
    STYLES_DIR,
    "results_view.qss",
)

SCROLLBAR_QSS = os.path.join(
    STYLES_DIR,
    "scrollbar.qss",
)

SESSION_QUERIES_HISTORY_QSS = os.path.join(
    STYLES_DIR,
    "session_queries_history.qss",
)

SETTINGS_MENU_QSS = os.path.join(
    STYLES_DIR,
    "settings_menu.qss",
)

SIDEBAR_QSS = os.path.join(
    STYLES_DIR,
    "sidebar.qss",
)

SQL_COMPLETER_QSS = os.path.join(
    STYLES_DIR,
    "sql_completer.qss",
)

SQL_EDITOR_QSS = os.path.join(
    STYLES_DIR,
    "sql_editor.qss",
)

TOOLBAR_QSS = os.path.join(
    STYLES_DIR,
    "toolbar.qss",
)

TOOLBAR_BUTTON_QSS = os.path.join(
    STYLES_DIR,
    "toolbar_button.qss",
)

TOOLBAR_SEPARATOR_QSS = os.path.join(
    STYLES_DIR,
    "toolbar_separator.qss",
)

TOOLTIP_QSS = os.path.join(
    STYLES_DIR,
    "tooltip.qss",
)

WORKSPACE_QSS = os.path.join(
    STYLES_DIR,
    "workspace.qss",
)

STYLE_FILES = [
    BASE_QSS,
    BUTTONS_QSS,
    CONFIRMATION_DIALOG_QSS,
    CONNECTION_FORM_QSS,
    CONNECTIONS_LIST_QSS,
    CONNECTIONS_LIST_BUTTONS_QSS,
    CONNECTION_QUERIES_HISTORY_QSS,
    FILES_LIST_QSS,
    FILES_LIST_ITEM_QSS,
    FONTS_QSS,
    HOME_QSS,
    NAVIGATION_TREE_QSS,
    NAVIGATION_TREE_CONTEXT_MENU_QSS,
    NOTIFICATIONS_QSS,
    RENAME_FILE_DIALOG_QSS,
    RESULTS_VIEW_QSS,
    SCROLLBAR_QSS,
    SESSION_QUERIES_HISTORY_QSS,
    SETTINGS_MENU_QSS,
    SIDEBAR_QSS,
    SQL_COMPLETER_QSS,
    SQL_EDITOR_QSS,
    TOOLBAR_QSS,
    TOOLBAR_BUTTON_QSS,
    TOOLBAR_SEPARATOR_QSS,
    TOOLTIP_QSS,
    WORKSPACE_QSS,
]
