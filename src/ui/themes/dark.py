from ui.common.paths import (
    ARROW_DOWN_ICON,
    ARROW_LINE_DOWN,
    ARROW_LINE_UP,
)
from ui.themes.color_pallete import *

# ===============
# === GENERAL ===
# ===============
THEME = {
    # Theme
    "theme_type": "dark",
    "fallback_color": WHITE,
    # Primary
    "primary": GREEN,
    "primary_hover": GREEN_HOVER,
    "primary_pressed": GREEN_PRESSED,
    "primary_disabled": GREEN_DISABLED,
    # Secondary
    "secondary": ORANGE,
    "secondary_hover": ORANGE_HOVER,
    "secondary_pressed": ORANGE_PRESSED,
    "secondary_disabled": ORANGE_DISABLED,
    # Danger
    "danger": RED,
    "danger_hover": RED_HOVER,
    "danger_pressed": RED_PRESSED,
    "danger_disabled": RED_DISABLED,
    # Warning
    "warning": YELLOW,
    "warning_hover": YELLOW_HOVER,
    "warning_pressed": YELLOW_PRESSED,
    "warning_disabled": YELLOW_DISABLED,
    # Success
    "success": LIGHT_GREEN,
    "success_hover": LIGHT_GREEN_HOVER,
    "success_pressed": LIGHT_GREEN_PRESSED,
    "success_disabled": LIGHT_GREEN_DISABLED,
    # Error
    "error": LIGHT_RED,
    "error_hover": LIGHT_RED_HOVER,
    "error_pressed": LIGHT_RED_PRESSED,
    "error_disabled": LIGHT_RED_DISABLED,
    # Info
    "info": CYAN,
    "info_hover": CYAN_HOVER,
    "info_pressed": CYAN_PRESSED,
    "info_disabled": CYAN_DISABLED,
    # Accent
    "accent": BLUE,
    "accent_hover": BLUE_HOVER,
    "accent_pressed": BLUE_PRESSED,
    "accent_disabled": BLUE_DISABLED,
    # Text
    "text": GRAY_100,
    "text_hover": WHITE,
    "text_pressed": GRAY_200,
    "text_disabled": GRAY_400,
}

# ===========
# === APP ===
# ===========
THEME.update(
    {
        "app_background_color": GRAY_900,
        "app_color": GRAY_100,
        # Tipografía
        "app_font_family": "'Segoe UI'",
        "app_font_size": "12px",
    }
)

# ===============
# === BUTTONS ===
# ===============
THEME.update(
    {
        # Default
        "button_background_color": GRAY_800,
        "button_background_color_hover": GRAY_700,
        "button_background_color_pressed": GRAY_600,
        "button_background_color_disabled": GRAY_800,
        "button_border_color": "#404040",
        "button_border_color_hover": "#404040",
        "button_border_color_pressed": "#404040",
        "button_border_color_disabled": "#404040",
        "button_color": GRAY_100,
        "button_color_hover": GRAY_100,
        "button_color_pressed": GRAY_100,
        "button_color_disabled": GRAY_100,
        # Primary
        "button_primary_background_color": TRANSPARENT,
        "button_primary_background_color_hover": THEME["primary_hover"],
        "button_primary_background_color_pressed": THEME["primary_pressed"],
        "button_primary_background_color_disabled": TRANSPARENT,
        "button_primary_border_color": THEME["primary"],
        "button_primary_border_color_hover": THEME["primary_hover"],
        "button_primary_border_color_pressed": THEME["primary_pressed"],
        "button_primary_border_color_disabled": THEME["primary_disabled"],
        "button_primary_color": THEME["primary"],
        "button_primary_color_hover": GRAY_800,
        "button_primary_color_pressed": GRAY_800,
        "button_primary_color_disabled": THEME["primary_disabled"],
        # Secondary
        "button_secondary_background_color": TRANSPARENT,
        "button_secondary_background_color_hover": THEME["secondary_hover"],
        "button_secondary_background_color_pressed": THEME["secondary_pressed"],
        "button_secondary_background_color_disabled": TRANSPARENT,
        "button_secondary_border_color": THEME["secondary"],
        "button_secondary_border_color_hover": THEME["secondary_hover"],
        "button_secondary_border_color_pressed": THEME["secondary_pressed"],
        "button_secondary_border_color_disabled": THEME["secondary_disabled"],
        "button_secondary_color": THEME["secondary"],
        "button_secondary_color_hover": GRAY_800,
        "button_secondary_color_pressed": GRAY_800,
        "button_secondary_color_disabled": THEME["secondary_disabled"],
        # Danger
        "button_danger_background_color": TRANSPARENT,
        "button_danger_background_color_hover": THEME["danger_hover"],
        "button_danger_background_color_pressed": THEME["danger_pressed"],
        "button_danger_background_color_disabled": TRANSPARENT,
        "button_danger_border_color": THEME["danger"],
        "button_danger_border_color_hover": THEME["danger_hover"],
        "button_danger_border_color_pressed": THEME["danger_pressed"],
        "button_danger_border_color_disabled": THEME["danger_disabled"],
        "button_danger_color": THEME["danger"],
        "button_danger_color_hover": GRAY_800,
        "button_danger_color_pressed": GRAY_800,
        "button_danger_color_disabled": THEME["danger_disabled"],
        # Accent
        "button_accent_background_color": TRANSPARENT,
        "button_accent_background_color_hover": THEME["accent_hover"],
        "button_accent_background_color_pressed": THEME["accent_pressed"],
        "button_accent_background_color_disabled": TRANSPARENT,
        "button_accent_border_color": THEME["accent"],
        "button_accent_border_color_hover": THEME["accent_hover"],
        "button_accent_border_color_pressed": THEME["accent_pressed"],
        "button_accent_border_color_disabled": THEME["accent_disabled"],
        "button_accent_color": THEME["accent"],
        "button_accent_color_hover": GRAY_800,
        "button_accent_color_pressed": GRAY_800,
        "button_accent_color_disabled": THEME["accent_disabled"],
    }
)

# =======================
# === CONNECTION FORM ===
# =======================
THEME.update(
    {
        # Formulario
        "connection_form_background_color": GRAY_950,
        "connection_form_border_color": THEME["primary"],
        # Título
        "connection_form_title_background_color": TRANSPARENT,
        # Labels
        "connection_form_input_label_color": THEME["text"],
        # Inputs
        "connection_form_input_background_color": GRAY_900,
        "connection_form_input_background_color_hover": GRAY_800,
        "connection_form_input_background_color_focus": GRAY_900,
        "connection_form_input_border_color": GRAY_800,
        "connection_form_input_border_color_hover": GRAY_700,
        "connection_form_input_border_color_focus": THEME["primary"],
        "connection_form_input_color": THEME["text"],
        "connection_form_input_color_hover": THEME["text_hover"],
        "connection_form_input_color_focus": THEME["primary"],
        "connection_form_arrow_icon": ARROW_DOWN_ICON.replace("\\", "/"),
    }
)

# ========================
# === CONNECTIONS LIST ===
# ========================
THEME.update(
    {
        "connection_item_connected_background_color": DARK_GREEN,
        "connection_item_connected_background_color_hover": DARK_GREEN_HOVER,
        "connection_item_connected_selected_background_color": DARK_GREEN_PRESSED,
        "connection_item_disconnected_background_color": TRANSPARENT,
        "connection_item_disconnected_background_color_hover": GRAY_700,
        "connection_item_disconnected_selected_background_color": GRAY_600,
        "connections_list_background_color": GRAY_800,
        "connections_list_border_color": GRAY_700,
    }
)

# ================================
# === CONNECTIONS LIST BUTTONS ===
# ================================
THEME.update(
    {
        # Add connection
        "button_add_connection_background_color": GRAY_800,
        "button_add_connection_background_color_hover": GREEN_HOVER,
        "button_add_connection_background_color_pressed": GREEN_PRESSED,
        "button_add_connection_background_color_disabled": GRAY_800,
        "button_add_connection_border_color": GREEN,
        "button_add_connection_border_color_hover": GREEN_HOVER,
        "button_add_connection_border_color_pressed": GREEN_PRESSED,
        "button_add_connection_border_color_disabled": GREEN_DISABLED,
        "button_add_connection_color": GREEN,
        "button_add_connection_color_hover": GRAY_800,
        "button_add_connection_color_pressed": GRAY_800,
        "button_add_connection_color_disabled": GREEN_DISABLED,
        # Edit connection
        "button_edit_connection_background_color": GRAY_800,
        "button_edit_connection_background_color_hover": ORANGE_HOVER,
        "button_edit_connection_background_color_pressed": ORANGE_PRESSED,
        "button_edit_connection_background_color_disabled": GRAY_800,
        "button_edit_connection_border_color": ORANGE,
        "button_edit_connection_border_color_hover": ORANGE_HOVER,
        "button_edit_connection_border_color_pressed": ORANGE_PRESSED,
        "button_edit_connection_border_color_disabled": ORANGE_DISABLED,
        "button_edit_connection_color": ORANGE,
        "button_edit_connection_color_hover": GRAY_800,
        "button_edit_connection_color_pressed": GRAY_800,
        "button_edit_connection_color_disabled": ORANGE_DISABLED,
        # Delete connection
        "button_delete_connection_background_color": GRAY_800,
        "button_delete_connection_background_color_hover": RED_HOVER,
        "button_delete_connection_background_color_pressed": RED_PRESSED,
        "button_delete_connection_background_color_disabled": GRAY_800,
        "button_delete_connection_border_color": RED,
        "button_delete_connection_border_color_hover": RED_HOVER,
        "button_delete_connection_border_color_pressed": RED_PRESSED,
        "button_delete_connection_border_color_disabled": RED_DISABLED,
        "button_delete_connection_color": RED,
        "button_delete_connection_color_hover": GRAY_800,
        "button_delete_connection_color_pressed": GRAY_800,
        "button_delete_connection_color_disabled": RED_DISABLED,
        # Connect
        "button_connect_background_color": GRAY_800,
        "button_connect_background_color_hover": BLUE_HOVER,
        "button_connect_background_color_pressed": BLUE_PRESSED,
        "button_connect_background_color_disabled": GRAY_800,
        "button_connect_border_color": BLUE,
        "button_connect_border_color_hover": BLUE_HOVER,
        "button_connect_border_color_pressed": BLUE_PRESSED,
        "button_connect_border_color_disabled": BLUE_DISABLED,
        "button_connect_color": BLUE,
        "button_connect_color_hover": GRAY_800,
        "button_connect_color_pressed": GRAY_800,
        "button_connect_color_disabled": BLUE_DISABLED,
        # Disconnect
        "button_disconnect_background_color": GRAY_800,
        "button_disconnect_background_color_hover": BLUE_HOVER,
        "button_disconnect_background_color_pressed": BLUE_PRESSED,
        "button_disconnect_background_color_disabled": GRAY_800,
        "button_disconnect_border_color": BLUE,
        "button_disconnect_border_color_hover": BLUE_HOVER,
        "button_disconnect_border_color_pressed": BLUE_PRESSED,
        "button_disconnect_border_color_disabled": BLUE_DISABLED,
        "button_disconnect_color": BLUE,
        "button_disconnect_color_hover": GRAY_800,
        "button_disconnect_color_pressed": GRAY_800,
        "button_disconnect_color_disabled": BLUE_DISABLED,
    }
)

# ==================================
# === CONNECTION QUERIES HISTORY ===
# ==================================
THEME.update(
    {
        # Contenedor de los inputs
        "connection_queries_history_inputs_background_color": GRAY_950,
        "connection_queries_history_inputs_border_color": THEME["primary"],
        # Inputs
        "connection_queries_history_date_input_background_color": GRAY_900,
        "connection_queries_history_date_input_background_color_hover": GRAY_800,
        "connection_queries_history_date_input_background_color_focus": GRAY_900,
        "connection_queries_history_date_input_border_color": GRAY_800,
        "connection_queries_history_date_input_border_color_hover": GRAY_700,
        "connection_queries_history_date_input_border_color_focus": THEME["primary"],
        "connection_queries_history_date_input_color": THEME["text"],
        "connection_queries_history_date_input_color_hover": THEME["text_hover"],
        "connection_queries_history_date_input_color_focus": THEME["primary"],
        # Tipografía de los inputs
        "connection_queries_history_date_input_font_family": "'Consolas'",
        "connection_queries_history_date_input_font_size": "12px",
        # Icono dropdown
        "connection_queries_history_date_input_arrow_icon": ARROW_DOWN_ICON.replace(
            "\\", "/"
        ),
        # Calendario desplegable
        "connection_queries_history_date_input_calendar_background_color": GRAY_950,
        "connection_queries_history_date_input_calendar_border_color": THEME["primary"],
        # Calendario desplegable: Inputs de año y mes
        "connection_queries_history_date_input_calendar_year_and_month_inputs_color": THEME[
            "text"
        ],
        "connection_queries_history_date_input_calendar_year_and_month_inputs_color_hover": THEME[
            "primary"
        ],
        "connection_queries_history_date_input_calendar_year_and_month_inputs_color_pressed": THEME[
            "primary"
        ],
        "connection_queries_history_date_input_calendar_year_input_arrow_up": ARROW_LINE_UP,
        "connection_queries_history_date_input_calendar_year_input_arrow_down": ARROW_LINE_DOWN,
        # Calendario desplegable: Menu del input de los meses
        "connection_queries_history_date_input_calendar_year_input_menu_background_color": GRAY_950,
        "connection_queries_history_date_input_calendar_year_input_menu_border_color": THEME[
            "primary"
        ],
        "connection_queries_history_date_input_calendar_year_input_menu_item_color": THEME[
            "text"
        ],
        "connection_queries_history_date_input_calendar_year_input_menu_item_background_color_hover": GREEN_DISABLED_RGBA_50,
        "connection_queries_history_date_input_calendar_year_input_menu_item_color_hover": THEME[
            "primary"
        ],
        "connection_queries_history_date_input_calendar_year_input_menu_separator_color": THEME[
            "primary"
        ],
        # Calendario desplegable: Botones de las flechas
        "connection_queries_history_date_input_calendar_arrow_button_background_color_hover": GREEN_DISABLED_RGBA_50,
        "connection_queries_history_date_input_calendar_arrow_button_background_color_pressed": GREEN_RGBA_50,
        # Calendario desplegable: Celdas de los días
        "connection_queries_history_date_input_calendar_cell_background_color_hover": GREEN_DISABLED_RGBA_50,
        "connection_queries_history_date_input_calendar_cell_background_color_selected": GREEN_RGBA_50,
        # Calendario desplegable: Tipografía
        "connection_queries_history_date_input_calendar_font_size": "14px",
    }
)

# ===============
# === CONSOLE ===
# ===============
THEME.update(
    {
        "console_background_color": GRAY_950,
        "console_border_color": THEME["primary"],
        "console_default_color": THEME["text"],
        "console_info_color": THEME["info"],
        "console_success_color": THEME["success"],
        "console_error_color": THEME["error"],
        "console_warning_color": THEME["warning"],
        "console_disabled_color": THEME["text_disabled"],
        # Tipografía
        "console_font_family": "'Consolas'",
        "console_font_size": "14px",
    }
)

# ===============
# === DIALOGS ===
# ===============
THEME.update(
    {
        "dialog_background_color": GRAY_800,
        "dialog_border_color": GRAY_700,
        "dialog_text_background_color": TRANSPARENT,
    }
)

# ==================
# === FILES LIST ===
# ==================
THEME.update(
    {
        "files_list_background_color": GRAY_950,
        "files_list_border_color": THEME["primary"],
    }
)

# =======================
# === FILES LIST ITEM ===
# =======================
THEME.update(
    {
        "files_list_item_background_color": "rgba(139, 195, 74, 0.10)",
        "files_list_item_background_color_hover": "rgba(139, 195, 74, 0.20)",
        "files_list_item_background_color_selected": "rgba(139, 195, 74, 0.30)",
        "files_list_item_color": THEME["secondary"],
        # Botón
        "files_list_item_close_button_background_color_hover": "rgba(197, 225, 165, 0.25)",
        "files_list_item_close_button_background_color_pressed": "rgba(197, 225, 165, 0.50)",
    }
)

# =================
# === HOME PAGE ===
# =================
THEME.update(
    {
        "home_page_background_color": GRAY_950,
        "home_page_border_color": THEME["primary"],
        "home_page_title_color": THEME["primary"],
        "home_page_slogan_color": THEME["secondary"],
    }
)

# =======================
# === NAVIGATION TREE ===
# =======================
THEME.update(
    {
        # Panel
        "navigation_tree_background_color": GRAY_950,
        "navigation_tree_border_color": THEME["primary"],
        # Barra de búsqueda
        "navigation_tree_search_bar_background_color": GRAY_900,
        "navigation_tree_search_bar_border_color": GRAY_800,
        "navigation_tree_search_bar_color": THEME["text"],
        "navigation_tree_search_bar_background_color_hover": GRAY_800,
        "navigation_tree_search_bar_border_color_hover": GRAY_700,
        "navigation_tree_search_bar_color_hover": THEME["text_hover"],
        "navigation_tree_search_bar_background_color_focus": GRAY_900,
        "navigation_tree_search_bar_border_color_focus": THEME["primary"],
        "navigation_tree_search_bar_color_focus": THEME["primary"],
        # Botón de refresco
        "navigation_tree_refresh_button_background_color": GRAY_800,
        "navigation_tree_refresh_button_border_color": THEME["accent"],
        "navigation_tree_refresh_button_color": THEME["accent"],
        "navigation_tree_refresh_button_background_color_hover": "rgba(76, 141, 218, 0.20)",
        "navigation_tree_refresh_button_background_color_pressed": "rgba(76, 141, 218, 0.10)",
        # Iconos
        "navigation_tree_icon_color": "#9e9e9e",
        "navigation_tree_column_icon_color": "#90a4ae",
        "navigation_tree_constraint_icon_color": "#1355b2",
        "navigation_tree_constraint_fk_icon_color": "#03a9f4",
        "navigation_tree_constraint_nullable_icon_color": "#e0e0e0",
        "navigation_tree_constraint_pk_icon_color": "#ffca28",
        "navigation_tree_constraint_unique_icon_color": "#fe5d51",
        "navigation_tree_constraint_check_icon_color": "#338337",
        "navigation_tree_folder_icon_color": "#f9a825",
        "navigation_tree_index_icon_color": "#ab47bc",
        "navigation_tree_materialized_view_icon_color": "#42a5f5",
        "navigation_tree_table_icon_color": "#42a5f5",
        "navigation_tree_view_icon_color": "#26a69a",
        # Items
        "navigation_tree_item_background_color_hover": GRAY_800,
        "navigation_tree_item_background_color_selected": GRAY_600,
        "navigation_tree_item_background_color_selected_active": GREEN_RGBA_25,
        "navigation_tree_item_background_color_selected_not_active": GRAY_700,
    }
)

# ====================================
# === NAVIGATION TREE CONTEXT MENU ===
# ====================================
THEME.update(
    {
        "navigation_tree_context_menu_background_color": "#252526",
        "navigation_tree_context_menu_border_color": THEME["primary"],
        "navigation_tree_context_menu_color": "#d4d4d4",
        "navigation_tree_context_menu_item_selected_background_color": "rgba(139, 195, 74, 0.10)",
        "navigation_tree_context_menu_item_selected_color": THEME["secondary"],
        "navigation_tree_context_menu_separator_color": "#3f3f46",
    }
)

# =====================
# === NOTIFICATIONS ===
# =====================
THEME.update(
    {
        # Default
        "notification_background_color": GRAY_100,
        "notification_border_color": GRAY_300,
        "notification_color": GRAY_900,
        # Success
        "notification_success_background_color": THEME["success"],
        "notification_success_border_color": DARK_GREEN,
        "notification_success_color": DARK_GREEN,
        # Error
        "notification_error_background_color": THEME["error"],
        "notification_error_border_color": DARK_RED,
        "notification_error_color": DARK_RED,
        # Info
        "notification_info_background_color": LIGHT_CYAN,
        "notification_info_border_color": DARK_CYAN,
        "notification_info_color": DARK_CYAN,
        # Warning
        "notification_warning_background_color": LIGHT_YELLOW,
        "notification_warning_border_color": DARK_YELLOW,
        "notification_warning_color": DARK_YELLOW,
    }
)

# ==========================
# === RENAME FILE DIALOG ===
# ==========================
THEME.update(
    {
        # Dialog
        "rename_file_dialog_background_color": GRAY_950,
        "rename_file_dialog_border_color": GRAY_800,
        "rename_file_dialog_color": THEME["text"],
        # Input
        "rename_file_dialog_input_background_color": GRAY_900,
        "rename_file_dialog_input_background_color_hover": GRAY_800,
        "rename_file_dialog_input_border_color": GRAY_800,
        "rename_file_dialog_input_border_color_hover": GRAY_700,
        "rename_file_dialog_input_color": THEME["text"],
        "rename_file_dialog_input_color_hover": THEME["text_hover"],
    }
)

# ==================
# === SCROLLBARS ===
# ==================
THEME.update(
    {
        "scrollbar_background_color": GRAY_950,
        "scrollbar_handle_color": THEME["primary"],
        "scrollbar_handle_color_hover": THEME["primary_hover"],
        "scrollbar_handle_color_pressed": THEME["primary_pressed"],
    }
)

# ===============================
# === SESSION QUERIES HISTORY ===
# ===============================
THEME.update(
    {
        "session_queries_history_background_color": GRAY_950,
        "session_queries_history_border_color": GREEN,
    }
)

# ====================================
# === SESSION QUERIES HISTORY ITEM ===
# ====================================
THEME.update(
    {
        "session_queries_history_item_background_color": TRANSPARENT,
        "session_queries_history_item_background_hover_color": GRAY_900,
        "session_queries_history_item_background_selected_color": GRAY_800,
        "session_queries_history_item_date_color": THEME["text_disabled"],
        "session_queries_history_item_query_color": THEME["text"],
    }
)

# ===============
# === SIDEBAR ===
# ===============
THEME.update(
    {
        "sidebar_background_color": GRAY_950,
        "sidebar_border_color": THEME["primary"],
    }
)

# =================
# === SPLITTERS ===
# =================
THEME.update(
    {
        "splitter_background_color": TRANSPARENT,
        "splitter_background_color_hover": THEME["accent"],
        "splitter_background_color_pressed": THEME["accent_hover"],
    }
)

# =====================
# === SQL COMPLETER ===
# =====================
THEME.update(
    {
        "sql_completer_background_color": GRAY_950,
        "sql_completer_border_color": THEME["primary"],
        "sql_completer_selection_background_color": GREEN_RGBA_75,
        "sql_completer_selection_color": GRAY_950,
    }
)

# ==================
# === SQL EDITOR ===
# ==================
THEME.update(
    {
        # Editor
        "sql_editor_background_color": GRAY_950,
        "sql_editor_border_color": THEME["primary"],
        "sql_editor_border_color_focused": THEME["accent"],
        "sql_editor_color": THEME["text"],
        # Tipografía
        "sql_editor_font_family": "'JetBrains Mono'",
        "sql_editor_font_size": "14px",
        # Línea actual
        "sql_editor_current_line_background_color": GRAY_900,
        # Área de números de línea
        "sql_editor_line_number_background_color": GRAY_900,
        "sql_editor_line_number_color": GRAY_350,
        "sql_editor_current_line_number_color": THEME["primary"],
    }
)

# ============================
# === SQL SYNTAX HIGHLIGHT ===
# ============================
THEME.update(
    {
        "sql_boolean_color": LIGHT_CYAN,
        "sql_column_color": LIGHT_BLUE,
        "sql_comment_color": GRAY_400,
        "sql_constant_color": LIGHT_CYAN,
        "sql_constraint_color": RED_SOFT,
        "sql_function_color": LIGHT_BLUE,
        "sql_identifier_color": GRAY_150,
        "sql_index_color": LIGHT_PURPLE,
        "sql_keyword_color": LIGHT_GREEN,
        "sql_null_color": LIGHT_CYAN,
        "sql_number_color": "#7AD69A",
        "sql_parameter_color": LIGHT_YELLOW,
        "sql_string_color": LIGHT_RED,
        "sql_symbol_color": "#DEC3E8",
        "sql_table_color": LIGHT_ORANGE,
        "sql_type_color": LIGHT_ORANGE,
        "sql_variable_color": LIGHT_YELLOW,
        "sql_view_color": ORANGE,
    }
)

# =============
# === TABLE ===
# =============
THEME.update(
    {
        # Tabla
        "table_background_color": GRAY_950,
        "table_border_color": THEME["primary"],
        "table_color": THEME["text"],
        # Cabecera
        "table_header_background_color": TRANSPARENT,
        # Celdas de la cabecera
        "table_header_cell_background_color": THEME["primary"],
        "table_header_cell_color": GRAY_800,
        # Celdas de la tabla
        "table_cell_background_color_hover": ORANGE_DISABLED_RGBA_25,
        "table_cell_selected_background_color": ORANGE_RGBA_25,
        "table_cell_selected_color": THEME["text"],
        "table_cell_modified_background_color": THEME["accent"],
        "table_cell_modified_color": GRAY_800,
        # Alternancia de filas
        "table_row_alternate_background_color": GRAY_900,
        "table_grid_color": TRANSPARENT,
        # Texto de las celdas en función del tipo de dato
        "table_null_color": "#808080",
        "table_default_color": "#D4D4D4",
        "table_boolean_color": "#569CD6",
        "table_datetime_color": "#DCDCAA",
        "table_dict_color": "#C586C0",
        "table_number_color": "#B5CEA8",
        "table_string_color": "#CE9178",
    }
)

# ===============
# === TOOLBAR ===
# ===============
THEME.update(
    {
        # Default
        "toolbar_background_color": GREEN_RGBA_25,
        "toolbar_border_color": THEME["primary"],
        "toolbar_color": THEME["text"],
        # Separador
        "toolbar_separator": GRAY_900,
    }
)

# ======================
# === TOOLBAR BUTTON ===
# ======================
THEME.update(
    {
        # Botones
        "toolbar_button_background_color": "transparent",
        "toolbar_button_background_color_hover": GRAY_950,
        "toolbar_button_background_color_pressed": GRAY_800,
        "toolbar_button_color": THEME["text"],
        "toolbar_button_color_hover": WHITE,
        "toolbar_button_color_pressed": WHITE,
        # Iconos
        "toolbar_button_execute_selection_icon_color": THEME["primary"],
        "toolbar_button_execute_query_icon_color": THEME["primary"],
        "toolbar_button_execute_script_icon_color": THEME["primary"],
        "toolbar_button_undo_icon_color": THEME["secondary"],
        "toolbar_button_redo_icon_color": THEME["secondary"],
        "toolbar_button_new_file_icon_color": LIGHT_BLUE,
        "toolbar_button_open_file_icon_color": YELLOW,
        "toolbar_button_rename_file_icon_color": LIGHT_RED,
        "toolbar_button_save_file_icon_color": GRAY_200,
    }
)

# ===============
# === TOOLTIP ===
# ===============
THEME.update(
    {
        "tooltip_background_color": GRAY_950,
        "tooltip_border_color": THEME["primary"],
        "tooltip_color": THEME["text"],
        # Tipografía
        "tooltip_font_family": "'Consolas'",
        "tooltip_font_size": "12px",
    }
)
