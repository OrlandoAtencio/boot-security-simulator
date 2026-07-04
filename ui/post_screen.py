"""
UTP SecureSim — Pantalla 1: POST (Power-On Self-Test)
=====================================================
Pantalla retro de terminal negra que simula el arranque del hardware.
Requiere: pip install PyQt6

Uso:
    python post_screen.py
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor
from core.post_engine import PostEngine

# ---------------------------------------------------------------------------
# PALETA DE COLORES
# ---------------------------------------------------------------------------
C_BG        = "#0A0A0A"
C_TEXT      = "#C8C8C8"
C_OK        = "#6DBF6D"
C_WARN      = "#E8C460"
C_ERROR     = "#E05555"
C_HEADER    = "#7EC8E3"
C_DIM       = "#555555"
C_WHITE     = "#FFFFFF"
C_BAR_BG    = "#1A3A1A"
C_BAR_FILL  = "#3DB83D"
C_BTN_BDR   = "#333333"
C_TITLEBAR  = "#111111"
C_CONTROLS  = "#0E0E0E"

# ---------------------------------------------------------------------------
# SECUENCIAS DE LÍNEAS POST
# ---------------------------------------------------------------------------
NORMAL_LINES = [
    {"delay": 0,    "type": "header", "text": "American Megatrends BIOS v2.31.1 — UTP SecureSim Board"},
    {"delay": 80,   "type": "dim",    "text": "Copyright (C) 2025 UTP-CSE Lab. All Rights Reserved."},
    {"delay": 120,  "type": "dim",    "text": "─" * 62},
    {"delay": 200,  "type": "normal", "text": "CPU: Intel Core i7-12700K @ 3.60GHz"},
    {"delay": 260,  "type": "normal", "text": "    Cores: 12  Threads: 20  Cache L3: 25MB"},
    {"delay": 310,  "type": "normal", "text": "    Microcode: 0x0024  APIC ID: 00h"},
    {"delay": 370,  "type": "ok",     "text": "    [  OK  ] CPU Self-Test.....................PASS"},
    {"delay": 460,  "type": "normal", "text": "RAM Memory Test:"},
    {"delay": 510,  "type": "bar",    "text": "  Slot A1 (DDR5-4800)", "max": 8192, "val": 8192, "unit": "MB"},
    {"delay": 720,  "type": "bar",    "text": "  Slot A2 (DDR5-4800)", "max": 8192, "val": 8192, "unit": "MB"},
    {"delay": 930,  "type": "bar",    "text": "  Slot B1 (DDR5-4800)", "max": 8192, "val": 4096, "unit": "MB"},
    {"delay": 1120, "type": "ok",     "text": "    [  OK  ] Memory Test...................PASS  (20480 MB OK)"},
    {"delay": 1220, "type": "normal", "text": "Initializing Chipset:"},
    {"delay": 1270, "type": "ok",     "text": "    [  OK  ] PCH: Intel Z690 Express.........PASS"},
    {"delay": 1320, "type": "ok",     "text": "    [  OK  ] DMI 4.0 Link....................PASS  x16 @ 16GT/s"},
    {"delay": 1370, "type": "ok",     "text": "    [  OK  ] PCIe 5.0 Controller.............PASS"},
    {"delay": 1440, "type": "normal", "text": "Storage Devices:"},
    {"delay": 1490, "type": "ok",     "text": "    [  OK  ] NVMe: Samsung 980 PRO 1TB.......PASS"},
    {"delay": 1540, "type": "ok",     "text": "    [  OK  ] SATA: WD Blue 2TB (SATA-III)....PASS"},
    {"delay": 1630, "type": "normal", "text": "Secure Boot Verification:"},
    {"delay": 1690, "type": "ok",     "text": "    [  OK  ] TPM 2.0 Detected................PASS"},
    {"delay": 1740, "type": "ok",     "text": "    [  OK  ] Secure Boot: ENABLED............PASS"},
    {"delay": 1790, "type": "ok",     "text": "    [  OK  ] Platform Key (PK) Verified......PASS"},
    {"delay": 1840, "type": "ok",     "text": "    [  OK  ] db/dbx Signature DB.............PASS"},
    {"delay": 1910, "type": "dim",    "text": "─" * 62},
    {"delay": 1960, "type": "white",  "text": "POST Complete. No errors detected."},
    {"delay": 2010, "type": "white",  "text": "Booting from: NVMe SSD..."},
    {"delay": 2110, "type": "dim",    "text": " "},
    {"delay": 2160, "type": "normal", "text": "Press DEL to enter Setup. Press F2 for Boot Menu."},
]

ROOTKIT_LINES = [
    {"delay": 0,    "type": "header", "text": "American Megatrends BIOS v2.31.1 — UTP SecureSim Board"},
    {"delay": 80,   "type": "dim",    "text": "Copyright (C) 2025 UTP-CSE Lab. All Rights Reserved."},
    {"delay": 120,  "type": "dim",    "text": "─" * 62},
    {"delay": 200,  "type": "normal", "text": "CPU: Intel Core i7-12700K @ 3.60GHz"},
    {"delay": 370,  "type": "ok",     "text": "    [  OK  ] CPU Self-Test.....................PASS"},
    {"delay": 460,  "type": "normal", "text": "RAM Memory Test:"},
    {"delay": 510,  "type": "bar",    "text": "  Slot A1 (DDR5-4800)", "max": 8192, "val": 8192, "unit": "MB"},
    {"delay": 720,  "type": "bar",    "text": "  Slot A2 (DDR5-4800)", "max": 8192, "val": 8192, "unit": "MB"},
    {"delay": 900,  "type": "warn",   "text": "    [ WARN ] Slot B1 — Anomalía en mapa de memoria detectada"},
    {"delay": 1060, "type": "normal", "text": "Initializing Chipset:"},
    {"delay": 1110, "type": "ok",     "text": "    [  OK  ] PCH: Intel Z690 Express.........PASS"},
    {"delay": 1210, "type": "warn",   "text": "    [ WARN ] DMI Trace: paquete no autorizado interceptado"},
    {"delay": 1330, "type": "normal", "text": "Secure Boot Verification:"},
    {"delay": 1410, "type": "error",  "text": "    [ FAIL ] Firma digital corrompida en UEFI Vol.0"},
    {"delay": 1470, "type": "error",  "text": "    [ FAIL ] Platform Key (PK) — Hash mismatch: 0xDEAD"},
    {"delay": 1530, "type": "error",  "text": "    [ FAIL ] db Signature DB — Entrada no autorizada hallada"},
    {"delay": 1590, "type": "error",  "text": "    [ FAIL ] ROOTKIT DETECTED: módulo en 0xFFFF800012C00000"},
    {"delay": 1660, "type": "dim",    "text": "─" * 62},
    {"delay": 1710, "type": "error",  "text": "!! SECURE BOOT VIOLATION — System Halted !!"},
    {"delay": 1770, "type": "warn",   "text": "   Causa: Código no firmado en SPI Flash Region 0x00080000"},
    {"delay": 1830, "type": "warn",   "text": "   Acción: Boot bloqueado. Revise integridad del firmware."},
]

COLOR_MAP = {
    "header": C_HEADER,
    "ok":     C_OK,
    "warn":   C_WARN,
    "error":  C_ERROR,
    "white":  C_WHITE,
    "dim":    C_DIM,
    "normal": C_TEXT,
    "bar":    C_TEXT,
}


# ---------------------------------------------------------------------------
# WIDGET: Barra de progreso RAM estilo terminal
# ---------------------------------------------------------------------------
class RamBar(QWidget):
    def __init__(self, label: str, value: int, maximum: int, unit: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(22)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        font_mono = QFont("Courier New", 10)

        lbl = QLabel(label)
        lbl.setFont(font_mono)
        lbl.setStyleSheet(f"color: {C_DIM}; background: transparent;")
        lbl.setFixedWidth(180)
        layout.addWidget(lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, maximum)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(9)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: {C_BAR_BG};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {C_BAR_FILL};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.bar)

        val_lbl = QLabel(f"{value} {unit}")
        val_lbl.setFont(font_mono)
        val_lbl.setStyleSheet(f"color: {C_OK}; background: transparent;")
        val_lbl.setFixedWidth(72)
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(val_lbl)

        # Animar la barra tras un breve retraso
        QTimer.singleShot(200, lambda: self._animate_to(value))

    def _animate_to(self, target: int):
        self._target = target
        self._current = 0
        self._step = max(1, target // 30)
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(20)

    def _tick(self):
        self._current = min(self._current + self._step, self._target)
        self.bar.setValue(self._current)
        if self._current >= self._target:
            self._timer.stop()


# ---------------------------------------------------------------------------
# PANTALLA PRINCIPAL POST
# ---------------------------------------------------------------------------
class PostScreen(QWidget):
    # Señal emitida cuando el usuario presiona DEL (→ ir a BIOS)
    go_to_bios = pyqtSignal()
    # Señal emitida cuando el POST termina normalmente (→ ir al Dashboard)
    post_complete = pyqtSignal()

    def __init__(self, parent=None):
        def __init__(self, parent=None):
    super().__init__(parent)
    self._injected = False
    self._timers: list[QTimer] = []

    self.log_output = QTextEdit()
    self.log_output.setReadOnly(True)

    self._build_ui()

    self.engine = PostEngine()
    self.engine.status_updated.connect(self.update_log_display)

    self.run_post()  # primera corrida al construir la pantalla

def update_log_display(self, mensaje: str, estado: str) -> None:
    color = "green" if estado == "OK" else "red"
    self.log_output.append(f'<span style="color: {color};">{mensaje}</span>')

def iniciar_arranque(self):
    """Corre el motor REAL de verificación (no solo la animación)."""
    self.log_output.clear()
    return self.engine.run_post_sequence(force_rootkit=self._injected)

def showEvent(self, event):
    # Ya no dispara la corrida por su cuenta para evitar duplicar
    # la ejecución del motor; run_post() ya se encarga de todo.
    super().showEvent(event)

    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.setStyleSheet(f"background: {C_BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Barra de título
        root.addWidget(self._make_titlebar())

        # Área de scroll (terminal)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: none; background: {C_BG}; }}
            QScrollBar:vertical {{
                background: {C_BG}; width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #333; border-radius: 3px;
            }}
        """)

        self.terminal_widget = QWidget()
        self.terminal_widget.setStyleSheet(f"background: {C_BG};")
        self.terminal_layout = QVBoxLayout(self.terminal_widget)
        self.terminal_layout.setContentsMargins(22, 18, 22, 18)
        self.terminal_layout.setSpacing(0)
        self.terminal_layout.addStretch()

        self.scroll_area.setWidget(self.terminal_widget)
        root.addWidget(self.scroll_area, 1)

        # Barra de controles
        root.addWidget(self._make_controls())

    def _make_titlebar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(32)
        bar.setStyleSheet(f"background: {C_TITLEBAR}; border-bottom: 1px solid #222;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        for color in ["#E05555", "#E8C460", "#6DBF6D"]:
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(f"background: {color}; border-radius: 5px;")
            layout.addWidget(dot)

        lbl = QLabel("SCREEN 1 — POST (Power-On Self-Test)")
        lbl.setFont(QFont("Courier New", 9))
        lbl.setStyleSheet(f"color: #444; background: transparent;")
        layout.addWidget(lbl)

        layout.addStretch()

        ver = QLabel("UTP SecureBoot Simulator v1.0")
        ver.setFont(QFont("Courier New", 9))
        ver.setStyleSheet(f"color: #2A2A2A; background: transparent;")
        layout.addWidget(ver)

        return bar

    def _make_controls(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(42)
        bar.setStyleSheet(f"background: {C_CONTROLS}; border-top: 1px solid #1C1C1C;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(22, 0, 22, 0)
        layout.setSpacing(8)

        self.btn_restart = QPushButton("▶  Reiniciar POST")
        self.btn_restart.setFont(QFont("Courier New", 10))
        self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restart.setStyleSheet(self._btn_style(C_BTN_BDR, "#888"))
        self.btn_restart.clicked.connect(self.run_post)
        layout.addWidget(self.btn_restart)

        layout.addStretch()

        self.btn_inject = QPushButton("⚠  Inyectar Rootkit")
        self.btn_inject.setFont(QFont("Courier New", 10))
        self.btn_inject.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_inject.setStyleSheet(self._btn_style(C_BTN_BDR, "#888"))
        self.btn_inject.clicked.connect(self._toggle_inject)
        layout.addWidget(self.btn_inject)

        hint = QLabel("DEL=Setup  F2=Boot Menu  F12=Network")
        hint.setFont(QFont("Courier New", 9))
        hint.setStyleSheet(f"color: #333; background: transparent; margin-left: 16px;")
        layout.addWidget(hint)

        return bar

    @staticmethod
    def _btn_style(border_color: str, text_color: str) -> str:
        return f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {border_color};
                color: {text_color};
                padding: 4px 12px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border-color: {C_OK};
                color: {C_OK};
            }}
        """

    # ------------------------------------------------------------------
    # LÓGICA DEL POST
    # ------------------------------------------------------------------
def run_post(self):
    """Limpia la terminal, corre el motor real y reproduce la animación."""
    for t in self._timers:
        t.stop()
    self._timers.clear()

    while self.terminal_layout.count() > 1:
        item = self.terminal_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()

    # 1. Corremos el motor REAL primero (fuente de verdad de seguridad)
    resultado_ok = self.iniciar_arranque()

    # 2. La animación visual usa el mismo resultado para decidir qué mostrar
    lines = ROOTKIT_LINES if not resultado_ok else NORMAL_LINES

    for i, entry in enumerate(lines):
        delay = entry["delay"]
        timer = QTimer(self)
        timer.setSingleShot(True)

        if entry["type"] == "bar":
            timer.timeout.connect(
                lambda e=entry: self._add_bar(e["text"], e["val"], e["max"], e["unit"])
            )
        else:
            timer.timeout.connect(
                lambda e=entry: self._add_line(e["text"], COLOR_MAP.get(e["type"], C_TEXT))
            )

        timer.start(delay)
        self._timers.append(timer)

    # 3. post_complete solo se emite si el motor confirmó integridad
    if resultado_ok:
        last_delay = NORMAL_LINES[-1]["delay"] + 800
        finish_timer = QTimer(self)
        finish_timer.setSingleShot(True)
        finish_timer.timeout.connect(self.post_complete.emit)
        finish_timer.start(last_delay)
        self._timers.append(finish_timer)

    def _add_line(self, text: str, color: str):
        lbl = QLabel(text)
        lbl.setFont(QFont("Courier New", 11))
        lbl.setStyleSheet(f"color: {color}; background: transparent;")
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        # Insertar antes del stretch final
        self.terminal_layout.insertWidget(self.terminal_layout.count() - 1, lbl)
        self._scroll_to_bottom()

    def _add_bar(self, label: str, value: int, maximum: int, unit: str):
        bar_widget = RamBar(label, value, maximum, unit)
        bar_widget.setStyleSheet(f"background: {C_BG};")
        self.terminal_layout.insertWidget(self.terminal_layout.count() - 1, bar_widget)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        QTimer.singleShot(10, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def _toggle_inject(self):
        self._injected = not self._injected
        if self._injected:
            self.btn_inject.setText("✓  Rootkit Activo")
            self.btn_inject.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {C_ERROR};
                    color: {C_ERROR};
                    padding: 4px 12px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background: {C_ERROR};
                    color: #fff;
                }}
            """)
        else:
            self.btn_inject.setText("⚠  Inyectar Rootkit")
            self.btn_inject.setStyleSheet(self._btn_style(C_BTN_BDR, "#888"))
        self.run_post()

    # Capturar tecla DEL para simular ir al Setup
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.go_to_bios.emit()
        super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# VENTANA PRINCIPAL (para prueba standalone)
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UTP SecureSim — POST Screen")
        self.setMinimumSize(900, 600)
        self.resize(1100, 680)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(C_BG))
        self.setPalette(palette)

        self.post = PostScreen()
        self.post.go_to_bios.connect(lambda: print("[SIGNAL] → Ir a BIOS Setup"))
        self.post.post_complete.connect(lambda: print("[SIGNAL] → POST completo, ir a Dashboard"))
        self.setCentralWidget(self.post)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
