from PySide6.QtWidgets import QApplication

app = QApplication([])

print("Style:", app.style().objectName())
print("Platform:", app.platformName())
