"""
UTP SecureSim — TRABAJO DE LA FASE 4: MONITOREO DE BUSES DE DATOS
=================================================================
Este módulo contiene exclusivamente la interfaz gráfica reactiva y el
hilo de control asíncrono requeridos para la Fase 4 del laboratorio.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QThread
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont

# Constantes de diseño para mantener la estética del dashboard oscuro
C_BORDER    = "#21262D"
C_MUTED     = "#8B949E"
C_BLUE      = "#58A6FF"
C_GREEN     = "#3FB950"
C_AMBER     = "#D29922"
C_RED       = "#F85149"
FONT_MONO  = QFont("Courier New", 9)

# ---------------------------------------------------------------------------
# TAREA 1: ENUMERACIÓN DE ESTADOS DEL BUS
# ---------------------------------------------------------------------------
class BusState:
    NORMAL = 0
    INTENSE_READ = 1  # Actividad visual intensa (Lectura acelerada)
    INTERRUPTED = 2   # Estado de Interrupción Visual (Bloqueo o Excepción)

# ---------------------------------------------------------------------------
# RE-DISEÑO DE BUSWIDGET ASÍNCRONO Y REACTIVO
# ---------------------------------------------------------------------------
class BusWidget(QWidget):
    def __init__(self, name: str, speed_label: str, color_normal: str, parent=None):
        super().__init__(parent)
        self.bus_name      = name
        self.speed_label   = speed_label
        self.color_normal  = QColor(color_normal)
        self.color_intense = QColor(C_BLUE)     
        self.color_interrupt = QColor(C_AMBER)  
        
        self.state         = BusState.NORMAL
        self.pkt_pos       = 0.0     # Posición del paquete (0.0 a 1.0)
        self.pkt_speed     = 0.018   # Velocidad base
        self.pkt_width     = 0.14    # Ancho del paquete de datos
        self.setFixedHeight(28)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_bus_state(self, new_state: int):
        """ Tarea 1: Cambia dinámicamente el estado operacional y la velocidad """
        self.state = new_state
        if self.state == BusState.NORMAL:
            self.pkt_speed = 0.018
        elif self.state == BusState.INTENSE_READ:
            self.pkt_speed = 0.065  # Tráfico intensificado
        elif self.state == BusState.INTERRUPTED:
            self.pkt_speed = 0.000  # Tarea 3: Detiene por completo el flujo del paquete
        self.update()

    def tick(self):
        """ Actualiza la posición del paquete de datos si no está interrumpido """
        if self.state != BusState.INTERRUPTED:
            self.pkt_pos = (self.pkt_pos + self.pkt_speed) % 1.0
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Renderizado del carril de fondo (Track)
        track_rect = QRect(0, (h - 12) // 2, w, 12)
        painter.setBrush(QBrush(QColor("#0D1117")))
        painter.setPen(QPen(QColor(C_BORDER), 1))
        painter.drawRoundedRect(track_rect, 3, 3)

        # Selección de color basada en el estado actual
        if self.state == BusState.INTENSE_READ:
            color = self.color_intense
        elif self.state == BusState.INTERRUPTED:
            color = self.color_interrupt
        else:
            color = self.color_normal

        # Tarea 3: Si está interrumpido, dibuja una sección estática con patrón discontinuo
        if self.state == BusState.INTERRUPTED:
            painter.setBrush(QBrush(self.color_interrupt))
            painter.setPen(QPen(QColor(C_RED), 1, Qt.PenStyle.DashLine))
            painter.drawRoundedRect(QRect(int(0.4 * w), (h - 10) // 2, int(0.2 * w), 10), 2, 2)
        else:
            # Flujo dinámico normal/intenso con estelas (Trails) reactivas
            trail_color = QColor(color)
            trail_color.setAlpha(60)
            pkt_x = int(self.pkt_pos * w)
            pkt_w = max(20, int(self.pkt_width * w))

            trail_x = pkt_x - pkt_w
            if trail_x > 0:
                painter.setBrush(QBrush(trail_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRect(trail_x, (h - 8) // 2, pkt_w, 8), 2, 2)

            # Paquete de datos principal
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRect(pkt_x % w, (h - 8) // 2, pkt_w, 8), 2, 2)

        painter.end()

# ---------------------------------------------------------------------------
# COMPONENTE DE FILA: Une la etiqueta de texto con el Bus animado
# ---------------------------------------------------------------------------
class BusRow(QWidget):
    def __init__(self, name: str, speed: str, color: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(name)
        lbl.setFont(FONT_MONO)
        lbl.setStyleSheet(f"color: {C_MUTED}; background: transparent;")
        lbl.setFixedWidth(110)
        layout.addWidget(lbl)

        self.bus = BusWidget(name, speed, color)
        layout.addWidget(self.bus, 1)

# ---------------------------------------------------------------------------
# TAREA 2: HILO ASÍNCRONO DE CONTROL (Evita congelamientos en la UI principal)
# ---------------------------------------------------------------------------
class HardwareSyncThread(QThread):
    """ Gestiona los tiempos lógicos de los buses en segundo plano """
    step_changed = pyqtSignal(str, int)

    def run(self):
        import time
        while True:
            # Fase 1: Simula actividad intensa
            self.step_changed.emit("SPI Flash", BusState.INTENSE_READ)
            time.sleep(2.5)
            # Fase 2: Simula tráfico normal
            self.step_changed.emit("NVMe M.2", BusState.NORMAL)
            time.sleep(3.0)
            # Fase 3: Excepción e Interrupción visual
            self.step_changed.emit("HARDWARE EXCEPTION", BusState.INTERRUPTED)
            time.sleep(2.0)