"""
UTP SecureSim — Aplicación Principal FASE 4
============================================
Integra las 3 pantallas con transiciones fluidas, manejo de estados
globales y sistema de alertas gráficas.
Requiere: pip install PyQt6

Uso:
    python main_fase4.py
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget,
    QMessageBox, QLabel, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

from post_screen import PostScreen
from bios_setup import BiosSetupScreen
from cyber_dashboard import CyberDashboard

# ---------------------------------------------------------------------------
# PALETA GLOBAL
# ---------------------------------------------------------------------------
C_BG   = "#0A0A0A"
C_RED  = "#F85149"
C_GREEN= "#3FB950"
C_BLUE = "#58A6FF"


# ---------------------------------------------------------------------------
# DIÁLOGO DE ALERTA PERSONALIZADO (QMessageBox estilo retro/tech)
# ---------------------------------------------------------------------------
class AlertDialog(QMessageBox):
    """
    Ventana emergente de alerta personalizada con estilo tecnológico.
    Niveles: 'info', 'warning', 'critical'
    """
    STYLES = {
        "info": {
            "border": C_BLUE,
            "bg":     "#0D1829",
            "title":  C_BLUE,
            "icon":   QMessageBox.Icon.Information,
        },
        "warning": {
            "border": "#D29922",
            "bg":     "#1A1500",
            "title":  "#D29922",
            "icon":   QMessageBox.Icon.Warning,
        },
        "critical": {
            "border": C_RED,
            "bg":     "#1A0000",
            "title":  C_RED,
            "icon":   QMessageBox.Icon.Critical,
        },
    }

    def __init__(self, parent, level: str, title: str, message: str):
        super().__init__(parent)
        style = self.STYLES.get(level, self.STYLES["info"])

        self.setWindowTitle(title)
        self.setText(f"<b style='color:{style['title']};font-size:13px'>{title}</b>")
        self.setInformativeText(f"<span style='color:#C8C8C8;font-size:11px'>{message}</span>")
        self.setIcon(style["icon"])
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

        self.setStyleSheet(f"""
            QMessageBox {{
                background-color: {style['bg']};
                border: 2px solid {style['border']};
                border-radius: 8px;
            }}
            QMessageBox QLabel {{
                color: #C8C8C8;
                font-family: 'Courier New';
                font-size: 11px;
                background: transparent;
            }}
            QPushButton {{
                background: transparent;
                border: 1px solid {style['border']};
                color: {style['border']};
                font-family: 'Courier New';
                font-size: 11px;
                padding: 5px 20px;
                border-radius: 4px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {style['border']};
                color: #000;
            }}
        """)
        self.setFont(QFont("Courier New", 10))


# ---------------------------------------------------------------------------
# PANEL FLOTANTE DE NOTIFICACIÓN (no bloquea la UI)
# ---------------------------------------------------------------------------
class ToastNotification(QWidget):
    """
    Notificación flotante que aparece en la esquina inferior derecha
    y desaparece automáticamente después de 3 segundos.
    """
    def __init__(self, parent, message: str, level: str = "info"):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.Tool |
                         Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        colors = {
            "info":     (C_BLUE,    "#0D1829"),
            "warning":  ("#D29922", "#1A1500"),
            "critical": (C_RED,     "#1A0000"),
            "ok":       (C_GREEN,   "#001A00"),
        }
        border, bg = colors.get(level, colors["info"])

        self.setStyleSheet(f"""
            QWidget {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)

        lbl = QLabel(message)
        lbl.setFont(QFont("Courier New", 10))
        lbl.setStyleSheet(f"color: {border}; background: transparent; border: none;")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        self.setFixedWidth(380)
        self.adjustSize()

        # Auto-cerrar después de 3 segundos
        QTimer.singleShot(3000, self.close)

    def show_at_bottom_right(self, parent_rect):
        x = parent_rect.right() - self.width() - 20
        y = parent_rect.bottom() - self.height() - 40
        self.move(x, y)
        self.show()


# ---------------------------------------------------------------------------
# VENTANA PRINCIPAL FASE 4
# ---------------------------------------------------------------------------
class SimulatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UTP SecureSim — Simulador de Seguridad en el Arranque")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(C_BG))
        self.setPalette(palette)

        # Estado global del simulador
        self._secure_boot_enabled = True
        self._rootkit_active       = False
        self._current_screen       = 0

        # Stack de pantallas
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Crear las 3 pantallas
        self.post  = PostScreen()
        self.bios  = BiosSetupScreen()
        self.dash  = CyberDashboard()

        self.stack.addWidget(self.post)   # índice 0
        self.stack.addWidget(self.bios)   # índice 1
        self.stack.addWidget(self.dash)   # índice 2

        # ------------------------------------------------------------------
        # CONECTAR SEÑALES — flujo de navegación
        # ------------------------------------------------------------------

        # POST → BIOS (DEL)
        self.post.go_to_bios.connect(self._go_to_bios)

        # POST → Dashboard (POST completo)
        self.post.post_complete.connect(self._go_to_dashboard)

        # BIOS → POST (F10 / ESC)
        self.bios.go_back.connect(self._go_to_post)

        # BIOS: cambio de Secure Boot → sincronizar Dashboard
        self.bios.sb_changed.connect(self._on_secure_boot_changed)

        # Arrancar en POST
        self._navigate_to(0)

    # ------------------------------------------------------------------
    # NAVEGACIÓN CON TRANSICIÓN
    # ------------------------------------------------------------------
    def _navigate_to(self, index: int):
        self._current_screen = index
        self.stack.setCurrentIndex(index)
        screen_names = ["POST", "BIOS Setup", "Dashboard"]
        self.setWindowTitle(
            f"UTP SecureSim — {screen_names[index]} | "
            f"Secure Boot: {'ON' if self._secure_boot_enabled else 'OFF'}"
        )

    def _go_to_post(self):
        self._navigate_to(0)
        self._show_toast("Regresando al POST...", "info")

    def _go_to_bios(self):
        self._navigate_to(1)
        self._show_toast("Entrando al BIOS Setup — DEL detectado", "info")

    def _go_to_dashboard(self):
        self._navigate_to(2)
        if not self._secure_boot_enabled:
            # Alerta crítica si Secure Boot está desactivado
            QTimer.singleShot(500, self._alert_sb_disabled)

    # ------------------------------------------------------------------
    # MANEJADORES DE ESTADO GLOBAL
    # ------------------------------------------------------------------
    def _on_secure_boot_changed(self, enabled: bool):
        self._secure_boot_enabled = enabled
        self.dash._set_indicator_from_bios(enabled)

        if enabled:
            self._show_toast("✓ Secure Boot ACTIVADO — sistema protegido", "ok")
        else:
            # Alerta de advertencia
            self._show_alert(
                level="warning",
                title="Secure Boot Desactivado",
                message=(
                    "ADVERTENCIA: Secure Boot ha sido desactivado desde el BIOS Setup.\n\n"
                    "El sistema cargará cualquier código de arranque sin verificación "
                    "criptográfica. Rootkits de firmware pueden operar sin restricción.\n\n"
                    "Reactive Secure Boot para proteger el sistema."
                )
            )

    # ------------------------------------------------------------------
    # ALERTAS GRÁFICAS
    # ------------------------------------------------------------------
    def _alert_sb_disabled(self):
        """Alerta crítica cuando se llega al Dashboard con Secure Boot apagado."""
        self._show_alert(
            level="critical",
            title="⚠ SISTEMA VULNERABLE",
            message=(
                "Secure Boot está DESACTIVADO.\n\n"
                "El sistema es vulnerable a ataques de rootkit de firmware.\n"
                "Cualquier código no firmado puede ejecutarse durante el arranque.\n\n"
                "Regrese al BIOS Setup y active Secure Boot para proteger el sistema."
            )
        )

    def show_rootkit_alert(self, rootkit_name: str):
        """Alerta crítica cuando se inyecta un rootkit."""
        self._show_alert(
            level="critical",
            title="🚨 ROOTKIT DETECTADO",
            message=(
                f"Rootkit activo: {rootkit_name}\n\n"
                "Se ha detectado código malicioso en el firmware UEFI:\n"
                "• SPI Flash Region comprometida\n"
                "• Hash SHA-256 no coincide\n"
                "• Firma digital inválida en db\n\n"
                "Active la mitigación para restaurar el sistema."
            )
        )

    def show_mitigation_alert(self):
        """Alerta de éxito cuando se mitiga el rootkit."""
        self._show_alert(
            level="info",
            title="✓ SISTEMA RESTAURADO",
            message=(
                "Mitigación completada exitosamente:\n\n"
                "• Secure Boot reafirmado\n"
                "• UEFI restaurado desde backup TPM\n"
                "• db/dbx signature database limpia\n"
                "• Hash SHA-256 verificado: OK\n\n"
                "El sistema está nuevamente protegido."
            )
        )

    def _show_alert(self, level: str, title: str, message: str):
        """Muestra un QMessageBox personalizado."""
        dialog = AlertDialog(self, level, title, message)
        dialog.exec()

    def _show_toast(self, message: str, level: str = "info"):
        """Muestra una notificación flotante no bloqueante."""
        toast = ToastNotification(self, message, level)
        toast.show_at_bottom_right(self.geometry())

    # ------------------------------------------------------------------
    # NAVEGACIÓN GLOBAL CON TECLAS DE FUNCIÓN
    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_F1:
            self._navigate_to(0)
        elif key == Qt.Key.Key_F2:
            self._navigate_to(1)
        elif key == Qt.Key.Key_F3:
            self._navigate_to(2)
        elif key == Qt.Key.Key_F5:
            # F5 = reiniciar simulación completa
            self._restart_simulation()
        super().keyPressEvent(event)

    def _restart_simulation(self):
        """Reinicia toda la simulación desde cero."""
        self._secure_boot_enabled = True
        self._rootkit_active = False
        self.post.run_post()
        self._navigate_to(0)
        self._show_toast("Simulación reiniciada desde cero", "info")


# ---------------------------------------------------------------------------
# PUNTO DE ENTRADA
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = SimulatorApp()
    win.show()
    sys.exit(app.exec())
