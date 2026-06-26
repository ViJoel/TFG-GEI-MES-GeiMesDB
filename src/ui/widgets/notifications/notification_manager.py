import logging

from PySide6.QtWidgets import QMainWindow

from ui.widgets.notifications.notification import Notification

logger = logging.getLogger(__name__)


class NotificationManager:

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el manejador de notificaciones.
        """

        self.main_window: QMainWindow | None = None
        self.notifications: list[Notification] = []

        self.margin = 16
        self.spacing = 10

    # ==================
    # === UI HELPERS ===
    # ==================

    def _reposition(
        self,
    ) -> None:
        """
        Recalcula la posición de todas las
        notificaciones visibles.

        Las notificaciones se alinean en la
        esquina superior derecha de la ventana
        principal, manteniendo el margen y la
        separación configurados entre ellas.

        El orden de posicionamiento sigue el
        contenido de ``self.notifications``.

        Este método se invoca cada vez que una
        notificación se añade o se elimina.
        """

        if self.main_window is None:
            return

        top_left = self.main_window.mapToGlobal(self.main_window.rect().topLeft())

        top_right_x = top_left.x() + self.main_window.width()
        y = top_left.y() + self.margin

        for notif in self.notifications:
            notif.adjustSize()

            x = top_right_x - notif.width() - self.margin
            notif.move(x, y)

            y += notif.height() + self.spacing

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    def _remove(self, notif: Notification) -> None:
        """
        Elimina una notificación gestionada
        por el manager.

        La notificación se elimina de la
        colección interna, se oculta, se
        programa su destrucción y se
        reposicionan las restantes.

        Args:
            notif (Notification):
                Notificación que debe eliminarse.
        """

        if notif in self.notifications:
            self.notifications.remove(notif)

        notif.hide()
        notif.deleteLater()

        self._reposition()

    # ==================
    # === PUBLIC API ===
    # ==================

    def show_notification(
        self,
        notification: Notification,
    ) -> None:
        """
        Muestra una nueva notificación y la
        registra para que sea gestionada por
        el manager.

        Args:
            notification (Notification):
                Notificación que debe mostrarse.
        """

        if self.main_window is None:
            logger.warning("NotificationManager has no registered main window.")
            return

        notification.close_requested.connect(lambda n=notification: self._remove(n))

        notification.adjustSize()

        self.notifications.append(notification)

        self._reposition()

        notification.show()

        notification.start_timer()

    def set_main_window(
        self,
        main_window: QMainWindow,
    ) -> None:
        """
        Registra la ventana principal de la
        aplicación.

        Esta ventana se utiliza como referencia
        para posicionar las notificaciones y como
        widget padre de las mismas.

        Args:
            main_window (QMainWindow):
                Ventana principal de la aplicación.
        """

        self.main_window = main_window

    def reposition(self) -> None:
        """
        Expone la función de reposicionamiento.
        """
        self._reposition()
