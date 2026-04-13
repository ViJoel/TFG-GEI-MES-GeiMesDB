import sys
from PySide6 import QtWidgets

from ui import MainWidget

if __name__ == "__main__":
    # 1. Creamos la instancia de la aplicación.
    # sys.argv permite que Qt reconozca parámetros de consola (como el tema o escalado).
    # Aunque pases una lista vacía [], es obligatorio para que los widgets existan.
    app = QtWidgets.QApplication(sys.argv)

    # 2. Instanciamos nuestra clase principal.
    # Aquí es donde se construye todo tu "DBeaver" a machete.
    window = MainWidget()

    # 3. Mostramos la interfaz ocupando toda la pantalla disponible.
    # A diferencia de .show(), esto aprovecha el espacio desde el arranque.
    window.showMaximized()

    # 4. Arrancamos el bucle de eventos (Event Loop).
    # .exec() bloquea el script para que la ventana no se cierre al instante.
    # sys.exit asegura que Python se cierre limpiamente cuando cerremos la ventana.
    sys.exit(app.exec())
