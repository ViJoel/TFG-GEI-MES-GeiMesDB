# ====================
# === TRANSPARENCY ===
# ====================
TRANSPARENT = "transparent"

# =================
# === GRAYSCALE ===
# =================
BLACK = "#000000"
GRAY_950 = "#121314"
GRAY_900 = "#1B1D1E"
GRAY_850 = "#1F2123"
GRAY_800 = "#242628"
GRAY_750 = "#282B2D"
GRAY_700 = "#2D3033"
GRAY_650 = "#313437"
GRAY_600 = "#35383C"
GRAY_550 = "#404348"
GRAY_500 = "#4A4D52"
GRAY_450 = "#5A5D62"
GRAY_400 = "#6B6E73"
GRAY_350 = "#7A7D81"
GRAY_300 = "#8A8D91"
GRAY_250 = "#A1A3A6"
GRAY_200 = "#B8B8B8"
GRAY_150 = "#D5D5D5"
GRAY_100 = "#F2F2F2"
GRAY_50 = "#F8F8F8"
WHITE = "#FFFFFF"

# =============
# === GREEN ===
# =============
GREEN = "#8BC34A"
GREEN_HOVER = "#9CCC65"
GREEN_PRESSED = "#7CB342"
GREEN_DISABLED = "#5E7F39"

# ===================
# === LIGHT GREEN ===
# ===================
LIGHT_GREEN = "#A5D66A"
LIGHT_GREEN_HOVER = "#B5DE84"
LIGHT_GREEN_PRESSED = "#95C85A"
LIGHT_GREEN_DISABLED = "#6F8F4D"

# ==============
# === ORANGE ===
# ==============
ORANGE = "#F28C38"
ORANGE_HOVER = "#F59E50"
ORANGE_PRESSED = "#E67E22"
ORANGE_DISABLED = "#9A6738"

# ===========
# === RED ===
# ===========
RED = "#D64545"
RED_HOVER = "#E05353"
RED_PRESSED = "#C03A3A"
RED_DISABLED = "#7D4141"

# ============
# === BLUE ===
# ============
BLUE = "#4C8DDA"
BLUE_HOVER = "#5B9BE7"
BLUE_PRESSED = "#3D7BC5"
BLUE_DISABLED = "#4C678A"

# ============
# === CYAN ===
# ============
CYAN = "#26C6DA"
CYAN_HOVER = "#4DD0E1"
CYAN_PRESSED = "#00ACC1"
CYAN_DISABLED = "#2A7D88"

# ==============
# === PURPLE ===
# ==============
PURPLE = "#AB47BC"
PURPLE_HOVER = "#BA68C8"
PURPLE_PRESSED = "#8E24AA"
PURPLE_DISABLED = "#73407D"

# ==============
# === YELLOW ===
# ==============
YELLOW = "#FDD835"
YELLOW_HOVER = "#FFEE58"
YELLOW_PRESSED = "#FBC02D"
YELLOW_DISABLED = "#A3913A"


# ============
# === PINK ===
# ============
PINK = "#EC407A"
PINK_HOVER = "#F06292"
PINK_PRESSED = "#D81B60"
PINK_DISABLED = "#8E4560"

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
        "button_primary_background_color_hover": GREEN_HOVER,
        "button_primary_background_color_pressed": GREEN_PRESSED,
        "button_primary_background_color_disabled": TRANSPARENT,
        "button_primary_border_color": GREEN,
        "button_primary_border_color_hover": GREEN_HOVER,
        "button_primary_border_color_pressed": GREEN_PRESSED,
        "button_primary_border_color_disabled": GREEN_DISABLED,
        "button_primary_color": GREEN,
        "button_primary_color_hover": GRAY_800,
        "button_primary_color_pressed": GRAY_800,
        "button_primary_color_disabled": GREEN_DISABLED,
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
    }
)

# ========================
# === CONNECTIONS LIST ===
# ========================
THEME.update(
    {
        "connection_item_connected_background_color": "#1f5f2c",
        "connection_item_connected_background_color_hover": "#29783a",
        "connection_item_connected_selected_background_color": "#34984a",
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

# ===============
# === DIALOGS ===
# ===============
THEME.update(
    {
        "dialog_background_color": GRAY_800,
        "dialog_border_color": GRAY_700,
        "dialog_label_background_color": TRANSPARENT,
    }
)

# ===============
# === SIDEBAR ===
# ===============
THEME.update(
    {
        "sidebar_background_color": GRAY_900,
        "sidebar_border_color": GREEN,
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

# ===============
# === CONSOLE ===
# ===============
THEME.update(
    {
        "console_background_color": GRAY_950,
        "console_border_color": THEME["primary"],
        "console_color": THEME["text"],
        "console_success_color": THEME["success"],
        "console_error_color": THEME["danger"],
    }
)
