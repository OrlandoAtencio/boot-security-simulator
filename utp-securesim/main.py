"""
UTP SecureSim — Aplicación Principal
=====================================
Integra las 3 pantallas en un QStackedWidget con navegación entre ellas.
Requiere: pip install PyQt6

Uso:
    python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt

from post_screen import PostScreen
from bios_setup import BiosSetupScreen
from cyber_dashboard import CyberDashboard


class SimulatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UTP SecureSim — Simulador de Seguridad en el Arranque")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0A0A0A"))
        self.setPalette(palette)

        # Stack de pantallas
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Crear las 3 pantallas
        self.post    = PostScreen()
        self.bios    = BiosSetupScreen()
        self.dash    = CyberDashboard()

        self.stack.addWidget(self.post)   # índice 0
        self.stack.addWidget(self.bios)   # índice 1
        self.stack.addWidget(self.dash)   # índice 2

        # Conectar señales de navegación
        self.post.go_to_bios.connect(lambda: self.stack.setCurrentIndex(1))
        self.post.post_complete.connect(lambda: self.stack.setCurrentIndex(2))
        self.bios.go_back.connect(lambda: self.stack.setCurrentIndex(0))
        self.bios.sb_changed.connect(self.dash._set_indicator_from_bios)

        # Arrancar en la pantalla POST
        self.stack.setCurrentIndex(0)

    def keyPressEvent(self, event):
        # Navegación global con teclas de función
        if event.key() == Qt.Key.Key_F1:
            self.stack.setCurrentIndex(0)
        elif event.key() == Qt.Key.Key_F2:
            self.stack.setCurrentIndex(1)
        elif event.key() == Qt.Key.Key_F3:
            self.stack.setCurrentIndex(2)
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = SimulatorApp()
    win.show()
    sys.exit(app.exec())
