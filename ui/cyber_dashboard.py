"""
UTP SecureSim — Pantalla 3: Panel Moderno de Ciberseguridad
============================================================
Dashboard oscuro con buses animados, consola de logs en tiempo real
y ciclo completo de ataque/mitigación de rootkit.
Requiere: pip install PyQt6

Uso:
    python cyber_dashboard.py
"""

import sys
import random
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QListWidget, QListWidgetItem,
    QComboBox, QProgressBar, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPen, QBrush

# ---------------------------------------------------------------------------
# PALETA DASHBOARD OSCURO
# ---------------------------------------------------------------------------
C_ROOT      = "#0D1117"
C_CARD      = "#161B22"
C_BORDER    = "#21262D"
C_TEXT      = "#F0F6FC"
C_MUTED     = "#8B949E"
C_BLUE      = "#58A6FF"
C_GREEN     = "#3FB950"
C_AMBER     = "#D29922"
C_RED       = "#F85149"
C_PURPLE    = "#BC8CFF"
C_MONO      = "Courier New"

FONT_MAIN  = QFont("Segoe UI", 10)
FONT_MONO  = QFont("Courier New", 9)
FONT_BOLD  = QFont("Segoe UI", 10)
FONT_BOLD.setBold(True)
FONT_SMALL = QFont("Segoe UI", 9)
FONT_BIG   = QFont("Segoe UI", 18)
FONT_BIG.setBold(True)

# ---------------------------------------------------------------------------
# TIPOS DE ROOTKIT
# ---------------------------------------------------------------------------
ROOTKIT_TYPES = [
    "Bootkitty — UEFI Bootloader Hook",
    "FinFisher — SPI Flash Rootkit",
    "CosmicStrand — Firmware Implant",
    "BlackLotus — Secure Boot Bypass",
]

# ---------------------------------------------------------------------------
# LOGS DE ATAQUE Y MITIGACIÓN
# ---------------------------------------------------------------------------
ATTACK_LOGS = [
    ("ATAQUE", "WARN", f"Escritura no autorizada en SPI Flash 0x00080000"),
    ("ATAQUE", "CRIT", f"Rootkit detectado: hook en vector de interrupción 0x13"),
    ("ATAQUE", "CRIT", f"Modificación de db signature database — entrada rogue insertada"),
    ("ATAQUE", "WARN", f"Bus de control SPI: paquete malformado interceptado"),
    ("ATAQUE", "CRIT", f"UEFI Vol.0 comprometido — hash SHA-256 no coincide"),
    ("ATAQUE", "WARN", f"Acceso anómalo a memoria en 0xFFFF800012C00000"),
    ("ATAQUE", "CRIT", f"Intento de escalada de privilegios en Ring-0"),
    ("ATAQUE", "WARN", f"PCR[7] del TPM ha cambiado de valor inesperadamente"),
]

MITIGATION_LOGS = [
    ("DEFENSA", "OK",   "Secure Boot reafirmado — verificando db/dbx..."),
    ("DEFENSA", "OK",   "Firma SHA-256 del bootloader verificada correctamente"),
    ("DEFENSA", "OK",   "TPM PCR[0-7] restaurados desde medición de referencia"),
    ("DEFENSA", "OK",   "UEFI Vol.0 restaurado desde backup TPM-sellado"),
    ("DEFENSA", "OK",   "Entrada rogue eliminada de db signature database"),
    ("DEFENSA", "OK",   "Sistema limpio. Integridad de firmware confirmada"),
]

# ===========================================================================
# MÓDULO INTERNO DE QA: MOTOR DE ASERCIÓN (Fase 3)
# ===========================================================================
class SecurityAssertionEngine:
    @staticmethod
    def verify_dashboard_integrity(is_injected: bool, btn_inject_enabled: bool, btn_mitigate_enabled: bool) -> bool:
        """
        Verifica matemáticamente en tiempo real que el estado booleano de integridad
        coincida con el estado operacional de los botones en el Dashboard.
        """
        try:
            if is_injected:
                # Si está infectado, Mitigar DEBE estar activo e Inyectar DEBE estar bloqueado
                assert btn_mitigate_enabled == True, "[QA CRITICAL] ¡Bypass detectado! Sistema infectado pero mitigación inhabilitada."
                assert btn_inject_enabled == False, "[QA CRITICAL] Error lógico: Permite inyectar otro rootkit sobre uno activo."
            else:
                # Si está mitigado/limpio, Mitigar DEBE bloquearse e Inyectar volver a habilitarse
                assert btn_mitigate_enabled == False, "[QA WARNING] Falso Positivo: El botón de mitigación sigue activo en sistema limpio."
                assert btn_inject_enabled == True, "[QA SUCCESS] Estado estable restablecido."
            
            print(f"[QA AUDIT - {datetime.now().strftime('%H:%M:%S')}] Aserción Correcta. UI alineada milimétricamente.")
            return True
        except AssertionError as e:
            print(f"[QA AUDIT - CRITICAL ERROR] {str(e)}")
            return False

# ---------------------------------------------------------------------------
# WIDGET: Animación de bus de datos
# ---------------------------------------------------------------------------
class BusWidget(QWidget):
    """
    Dibuja un bus de datos con un 'paquete' que se mueve de izquierda a derecha.
    En modo ataque: el paquete es rojo y se mueve más rápido.
    """
    def __init__(self, name: str, speed_label: str, color_normal: str,
                 parent=None):
        super().__init__(parent)
        self.bus_name      = name
        self.speed_label   = speed_label
        self.color_normal  = QColor(color_normal)
        self.color_attack  = QColor(C_RED)
        self.is_attack     = False
        self.pkt_pos       = 0.0     # 0.0 – 1.0
        self.pkt_speed     = 0.018   # fracción por tick
        self.pkt_width     = 0.14
        self.setFixedHeight(28)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_attack(self, state: bool):
        self.is_attack = state
        self.pkt_speed = 0.045 if state else 0.018

    def tick(self):
        self.pkt_pos = (self.pkt_pos + self.pkt_speed) % 1.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        # Fondo del track
        track_rect = QRect(0, (h - 12) // 2, w, 12)
        painter.setBrush(QBrush(QColor("#0D1117")))
        painter.setPen(QPen(QColor(C_BORDER), 1))
        painter.drawRoundedRect(track_rect, 3, 3)

        # Paquete
        color = self.color_attack if self.is_attack else self.color_normal
        # Darken the color for the trail
        trail_color = QColor(color)
        trail_color.setAlpha(60)

        pkt_x     = int(self.pkt_pos * w)
        pkt_w     = max(20, int(self.pkt_width * w))

        # Trail (desvanecimiento hacia atrás)
        trail_x = pkt_x - pkt_w
        if trail_x > 0:
            painter.setBrush(QBrush(trail_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                QRect(trail_x, (h - 8) // 2, pkt_w, 8), 2, 2
            )

        # Paquete principal
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        draw_x = pkt_x % w
        painter.drawRoundedRect(
            QRect(draw_x, (h - 8) // 2, pkt_w, 8), 2, 2
        )

        painter.end()


# ---------------------------------------------------------------------------
# WIDGET: Fila de bus con etiqueta y velocidad
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

        self.speed_lbl = QLabel(speed)
        self.speed_lbl.setFont(FONT_MONO)
        self.speed_lbl.setStyleSheet(f"color: {C_BLUE}; background: transparent;")
        self.speed_lbl.setFixedWidth(130)
        self.speed_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.speed_lbl)

        self.alert_dot = QLabel("●")
        self.alert_dot.setFont(QFont("Segoe UI", 10))
        self.alert_dot.setStyleSheet(f"color: {C_GREEN}; background: transparent;")
        self.alert_dot.setFixedWidth(16)
        layout.addWidget(self.alert_dot)

    def set_attack(self, state: bool, speed_text: str):
        self.bus.set_attack(state)
        color = C_RED if state else C_BLUE
        self.speed_lbl.setStyleSheet(f"color: {color}; background: transparent;")
        self.speed_lbl.setText(speed_text)
        dot_color = C_RED if state else C_GREEN
        self.alert_dot.setStyleSheet(f"color: {dot_color}; background: transparent;")

    def tick(self):
        self.bus.tick()


# ---------------------------------------------------------------------------
# WIDGET: Tarjeta de métrica
# ---------------------------------------------------------------------------
class StatCard(QWidget):
    def __init__(self, label: str, value: str, value_color: str = C_TEXT, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            background: {C_CARD};
            border: 1px solid {C_BORDER};
            border-radius: 8px;
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        self.lbl = QLabel(label)
        self.lbl.setFont(FONT_SMALL)
        self.lbl.setStyleSheet(f"color: {C_MUTED}; background: transparent; border: none;")
        layout.addWidget(self.lbl)

        self.val = QLabel(value)
        self.val.setFont(FONT_BIG)
        self.val.setStyleSheet(f"color: {value_color}; background: transparent; border: none;")
        layout.addWidget(self.val)

    def set_value(self, text: str, color: str):
        self.val.setText(text)
        self.val.setStyleSheet(f"color: {color}; background: transparent; border: none;")


# ---------------------------------------------------------------------------
# PANEL DE CIBERSEGURIDAD
# ---------------------------------------------------------------------------
class CyberDashboard(QWidget):
    mitigation_activated = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self._injected    = False
        self._log_index   = 0
        self._alert_count = 0
        self._blink_state = False

        # Timers
        self._bus_timer  = QTimer(self)
        self._bus_timer.timeout.connect(self._tick_buses)
        self._bus_timer.start(60)

        self._log_timer  = QTimer(self)
        self._log_timer.timeout.connect(self._add_attack_log)

        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink_badge)
        self._blink_timer.start(600)

        self._build_ui()
        self._add_boot_log()

    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.setStyleSheet(f"background: {C_ROOT};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_topbar())

        body = QHBoxLayout()
        body.setContentsMargins(12, 10, 12, 10)
        body.setSpacing(10)
        body.addLayout(self._make_main_column(), 1)
        body.addWidget(self._make_sidebar(), 0)

        body_widget = QWidget()
        body_widget.setStyleSheet(f"background: {C_ROOT};")
        body_widget.setLayout(body)
        root.addWidget(body_widget, 1)

        root.addWidget(self._make_footer())

    def _make_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"background: {C_CARD}; border-bottom: 1px solid {C_BORDER};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        logo = QLabel("⬡ UTP SecureSim")
        logo.setFont(QFont("Segoe UI", 12))
        logo.setStyleSheet(f"color: {C_BLUE}; background: transparent; font-weight: bold;")
        layout.addWidget(logo)

        self.system_badge = QLabel("SISTEMA SEGURO")
        self.system_badge.setFont(FONT_SMALL)
        self.system_badge.setStyleSheet(self._badge_style(C_GREEN, "#1F3A1F"))
        layout.addWidget(self.system_badge)

        sep = QLabel("|")
        sep.setStyleSheet(f"color: #30363D; background: transparent;")
        layout.addWidget(sep)

        sub = QLabel("Fase 3 — Panel de Ciberseguridad")
        sub.setFont(FONT_SMALL)
        sub.setStyleSheet(f"color: {C_BLUE}; background: transparent;")
        layout.addWidget(sub)

        layout.addStretch()

        scr = QLabel("SCREEN 3 — Cybersecurity Dashboard")
        scr.setFont(FONT_SMALL)
        scr.setStyleSheet(f"color: #30363D; background: transparent;")
        layout.addWidget(scr)

        return bar

    def _make_main_column(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(10)

        # Fila de stat cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)
        self.stat_system   = StatCard("Estado del Sistema", "SEGURO",    C_GREEN)
        self.stat_threat   = StatCard("Nivel de Amenaza",   "0%",        C_GREEN)
        self.stat_sb       = StatCard("Secure Boot",        "ACTIVO",    C_GREEN)
        self.stat_uefi     = StatCard("Integridad UEFI",    "100%",      C_GREEN)
        for card in [self.stat_system, self.stat_threat, self.stat_sb, self.stat_uefi]:
            stats_row.addWidget(card)
        col.addLayout(stats_row)

        # Panel de buses
        col.addWidget(self._make_bus_panel())

        # Consola de logs
        col.addWidget(self._make_log_panel(), 1)

        return col

    def _make_bus_panel(self) -> QWidget:
        panel = self._card_widget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        title = QLabel("MONITOREO DE BUSES DE DATOS — Actividad en tiempo real")
        title.setFont(QFont("Segoe UI", 9))
        title.setStyleSheet(f"color: {C_MUTED}; background: transparent; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(title)

        self.bus_rows = {
            "data":  BusRow("Bus de Datos",    "64-bit / Normal",  "#1F4A8A"),
            "addr":  BusRow("Bus de Dirección","48-bit / Normal",  "#1A4A1A"),
            "ctrl":  BusRow("Bus de Control",  "SPI / Normal",     "#3A2A00"),
            "spi":   BusRow("SPI Flash (BIOS)","33MHz / Idle",     "#1A2A3A"),
        }
        for row in self.bus_rows.values():
            layout.addWidget(row)

        return panel

    def _make_log_panel(self) -> QWidget:
        panel = self._card_widget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(30)
        header.setStyleSheet(f"background: {C_CARD}; border-bottom: 1px solid {C_BORDER}; border-radius: 0px;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 0, 12, 0)

        self.log_dot = QLabel("●")
        self.log_dot.setFont(QFont("Segoe UI", 10))
        self.log_dot.setStyleSheet(f"color: {C_GREEN}; background: transparent;")
        h_layout.addWidget(self.log_dot)

        log_title = QLabel("CONSOLA DE LOGS — Auditoría de Arranque")
        log_title.setFont(QFont("Segoe UI", 9))
        log_title.setStyleSheet(f"color: {C_MUTED}; background: transparent; font-weight: bold; letter-spacing: 0.8px;")
        h_layout.addWidget(log_title)

        h_layout.addStretch()

        btn_clear = QPushButton("Limpiar")
        btn_clear.setFont(FONT_SMALL)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {C_BORDER};
                color: {C_MUTED};
                padding: 2px 8px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: {C_BLUE};
                color: {C_BLUE};
            }}
        """)
        btn_clear.clicked.connect(self._clear_logs)
        h_layout.addWidget(btn_clear)
        layout.addWidget(header)

        self.log_list = QListWidget()
        self.log_list.setFont(FONT_MONO)
        self.log_list.setStyleSheet(f"""
            QListWidget {{
                background: {C_ROOT};
                border: none;
                padding: 4px 8px;
            }}
            QListWidget::item {{
                padding: 1px 0;
                color: {C_MUTED};
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {C_ROOT};
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #333;
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.log_list, 1)
        return panel

    def _make_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"background: transparent;")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Panel de ataque
        layout.addWidget(self._make_attack_panel())
        # Medidor de amenaza
        layout.addWidget(self._make_threat_meter())
        # Indicadores de estado
        layout.addWidget(self._make_status_indicators())

        layout.addStretch()
        return sidebar

    def _make_attack_panel(self) -> QWidget:
        panel = self._card_widget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        title = QLabel("PANEL DE ATAQUE / DEFENSA")
        title.setFont(QFont("Segoe UI", 9))
        title.setStyleSheet(f"color: {C_MUTED}; background: transparent; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(title)

        self.rk_combo = QComboBox()
        self.rk_combo.addItems(ROOTKIT_TYPES)
        self.rk_combo.setFont(FONT_SMALL)
        self.rk_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C_ROOT};
                border: 1px solid {C_BORDER};
                color: {C_MUTED};
                padding: 5px 8px;
                border-radius: 6px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background: {C_CARD};
                color: {C_TEXT};
                selection-background-color: {C_BORDER};
            }}
        """)
        layout.addWidget(self.rk_combo)

        self.btn_inject = QPushButton("⚡  Inyectar Rootkit")
        self.btn_inject.setFont(FONT_BOLD)
        self.btn_inject.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_inject.setStyleSheet(self._attack_btn_style(C_RED, "#3A1F1F"))
        self.btn_inject.clicked.connect(self._inject_rootkit)
        layout.addWidget(self.btn_inject)

        self.btn_mitigate = QPushButton("🛡  Activar Mitigación")
        self.btn_mitigate.setFont(FONT_BOLD)
        self.btn_mitigate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mitigate.setStyleSheet(self._attack_btn_style(C_GREEN, "#1F3A1F"))
        self.btn_mitigate.setEnabled(False)
        self.btn_mitigate.clicked.connect(self._mitigate_rootkit)
        layout.addWidget(self.btn_mitigate)

        return panel

    def _make_threat_meter(self) -> QWidget:
        panel = self._card_widget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        title = QLabel("NIVEL DE AMENAZA")
        title.setFont(QFont("Segoe UI", 9))
        title.setStyleSheet(f"color: {C_MUTED}; background: transparent; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(title)

        self.threat_bar = QProgressBar()
        self.threat_bar.setRange(0, 100)
        self.threat_bar.setValue(0)
        self.threat_bar.setFixedHeight(12)
        self.threat_bar.setTextVisible(False)
        self._set_threat_bar_color(C_GREEN)
        layout.addWidget(self.threat_bar)

        scale = QHBoxLayout()
        for txt, color in [("BAJO", C_GREEN), ("MEDIO", C_AMBER), ("CRÍTICO", C_RED)]:
            lbl = QLabel(txt)
            lbl.setFont(QFont("Courier New", 8))
            lbl.setStyleSheet(f"color: {color}; background: transparent;")
            if txt == "MEDIO":
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            elif txt == "CRÍTICO":
                lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            scale.addWidget(lbl)
        layout.addLayout(scale)
        return panel

    def _make_status_indicators(self) -> QWidget:
        panel = self._card_widget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        self.indicators = {}
        items = [
            ("sb",   "Secure Boot",    "ACTIVO"),
            ("tpm",  "TPM 2.0",        "OK"),
            ("uefi", "UEFI Integridad","ÍNTEGRO"),
        ]
        for key, label, status in items:
            row = QHBoxLayout()
            dot = QLabel("●")
            dot.setFont(QFont("Segoe UI", 12))
            dot.setStyleSheet(f"color: {C_GREEN}; background: transparent;")
            dot.setFixedWidth(18)
            row.addWidget(dot)

            lbl = QLabel(label)
            lbl.setFont(FONT_SMALL)
            lbl.setStyleSheet(f"color: {C_TEXT}; background: transparent;")
            row.addWidget(lbl)

            row.addStretch()

            sub = QLabel(status)
            sub.setFont(FONT_SMALL)
            sub.setStyleSheet(f"color: {C_MUTED}; background: transparent;")
            row.addWidget(sub)

            self.indicators[key] = {"dot": dot, "lbl": lbl, "sub": sub}

            row_widget = QWidget()
            row_widget.setStyleSheet("background: transparent;")
            row_widget.setLayout(row)
            row_widget.setFixedHeight(26)
            layout.addWidget(row_widget)

        return panel

    def _make_footer(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(28)
        bar.setStyleSheet(f"background: {C_CARD}; border-top: 1px solid {C_BORDER};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(20)

        self.footer_cpu  = QLabel("CPU: 23%")
        self.footer_ram  = QLabel("RAM: 4.2 GB")
        self.footer_spi  = QLabel("SPI: Idle")
        self.footer_alert = QLabel("")

        for lbl in [self.footer_cpu, self.footer_ram, self.footer_spi, self.footer_alert]:
            lbl.setFont(FONT_SMALL)
            lbl.setStyleSheet(f"color: {C_MUTED}; background: transparent;")
            layout.addWidget(lbl)

        layout.addStretch()

        ver = QLabel("UTP-CSE SecureSim v1.0 — Fase 1 Prototipo")
        ver.setFont(FONT_SMALL)
        ver.setStyleSheet(f"color: #30363D; background: transparent;")
        layout.addWidget(ver)
        return bar

    # ------------------------------------------------------------------
    # HELPERS DE ESTILO
    # ------------------------------------------------------------------
    def _card_widget(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"""
            background: {C_CARD};
            border: 1px solid {C_BORDER};
            border-radius: 8px;
        """)
        return w

    @staticmethod
    def _badge_style(color: str, bg: str) -> str:
        return (f"background: {bg}; color: {color}; border: 1px solid {color};"
                f" border-radius: 10px; padding: 1px 10px; font-size: 10px;")

    @staticmethod
    def _attack_btn_style(color: str, bg: str) -> str:
        return f"""
            QPushButton {{
                background: {bg};
                border: 1px solid {color};
                color: {color};
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover:enabled {{
                background: {color};
                color: #fff;
            }}
            QPushButton:disabled {{
                opacity: 0.4;
                color: #555;
                border-color: #333;
                background: #111;
            }}
        """

    def _set_threat_bar_color(self, color: str):
        self.threat_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {C_ROOT};
                border-radius: 5px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 5px;
            }}
        """)

    # ------------------------------------------------------------------
    # LÓGICA DE ATAQUE / MITIGACIÓN
    # ------------------------------------------------------------------
    def _inject_rootkit(self):
        if self._injected:
            return
        self._injected = True
        rk = self.rk_combo.currentText()
        self._log_index = 0
        self._alert_count = 0

        self.btn_inject.setEnabled(False)
        self.btn_mitigate.setEnabled(True)

        # Badge y stats
        self.system_badge.setText("SISTEMA COMPROMETIDO")
        self.system_badge.setStyleSheet(self._badge_style(C_RED, "#3A1F1F"))
        self.stat_system.set_value("CRÍTICO", C_RED)
        self.stat_sb.set_value("VULNERADO", C_RED)
        self.stat_uefi.set_value("12%", C_RED)

        # Indicadores
        self._set_indicator("sb",   C_RED,   "BYPASS")
        self._set_indicator("tpm",  C_RED,   "ANOMALÍA")
        self._set_indicator("uefi", C_RED,   "COMPROMETIDO")

        # Buses en modo ataque
        self.bus_rows["data"].set_attack(True,  "64-bit / ANOMALÍA")
        self.bus_rows["addr"].set_attack(True,  "48-bit / ANOMALÍA")
        self.bus_rows["ctrl"].set_attack(True,  "SPI / ATAQUE")
        self.bus_rows["spi"].set_attack(True,   "33MHz / ESCRITURA")

        # Footer
        self.footer_spi.setText("SPI: ESCRIBIENDO")
        self.footer_spi.setStyleSheet(f"color: {C_RED}; background: transparent;")
        self.footer_alert.setText(f"Alertas activas: {self._alert_count}")
        self.footer_alert.setStyleSheet(f"color: {C_RED}; background: transparent;")

        # Threat meter
        self._animate_threat(87, C_RED)

        # Log inicial
        self._add_log("ATAQUE", "INFO", f"Inyectando: {rk}", C_AMBER)
        self._log_timer.start(950)

        SecurityAssertionEngine.verify_dashboard_integrity(
            self._injected, self.btn_inject.isEnabled(), self.btn_mitigate.isEnabled()
        )

    def _mitigate_rootkit(self):
        if not self._injected:
            return
        self._injected = False
        self._log_timer.stop()
        self._log_index = 0

        self.btn_inject.setEnabled(True)
        self.btn_mitigate.setEnabled(False)

        self.system_badge.setText("MITIGADO")
        self.system_badge.setStyleSheet(self._badge_style(C_GREEN, "#1F3A1F"))
        self.stat_system.set_value("SEGURO",  C_GREEN)
        self.stat_sb.set_value("ACTIVO",      C_GREEN)
        self.stat_uefi.set_value("100%",      C_GREEN)
        self.stat_threat.set_value("0%",      C_GREEN)

        self._set_indicator("sb",   C_GREEN, "ACTIVO")
        self._set_indicator("tpm",  C_GREEN, "OK")
        self._set_indicator("uefi", C_GREEN, "ÍNTEGRO")

        self.bus_rows["data"].set_attack(False, "64-bit / Normal")
        self.bus_rows["addr"].set_attack(False, "48-bit / Normal")
        self.bus_rows["ctrl"].set_attack(False, "SPI / Normal")
        self.bus_rows["spi"].set_attack(False,  "33MHz / Idle")

        self.footer_spi.setText("SPI: Idle")
        self.footer_spi.setStyleSheet(f"color: {C_GREEN}; background: transparent;")
        self.footer_alert.setText("")
        self._alert_count = 0

        self._animate_threat(0, C_GREEN)

        for _, lvl, msg in MITIGATION_LOGS:
            self._add_log("DEFENSA", lvl, msg, C_GREEN)

        self.mitigation_activated.emit()

        SecurityAssertionEngine.verify_dashboard_integrity(
            self._injected, self.btn_inject.isEnabled(), self.btn_mitigate.isEnabled()
        )

    def _set_indicator(self, key: str, color: str, status: str):
        ind = self.indicators[key]
        ind["dot"].setStyleSheet(f"color: {color}; background: transparent;")
        ind["sub"].setText(status)
        ind["sub"].setStyleSheet(f"color: {color}; background: transparent;")

    def _animate_threat(self, target: int, color: str):
        current = self.threat_bar.value()
        step = 3 if target > current else -3

        def _tick():
            val = self.threat_bar.value()
            new_val = val + step
            if (step > 0 and new_val >= target) or (step < 0 and new_val <= target):
                new_val = target
                t.stop()
            self.threat_bar.setValue(new_val)
            self.stat_threat.set_value(f"{new_val}%", color)
            self._set_threat_bar_color(color)

        t = QTimer(self)
        t.timeout.connect(_tick)
        t.start(25)

    # ------------------------------------------------------------------
    # LOGS
    # ------------------------------------------------------------------
    def _add_boot_log(self):
        boot = [
            ("OK",   "Sistema iniciado. UEFI v2.31 cargado correctamente."),
            ("OK",   "TPM 2.0 inicializado. PCR[0-7] medidos."),
            ("OK",   "Secure Boot activo. Verificando db/dbx..."),
            ("OK",   "Bootloader firmado verificado. Hash SHA-256: A3F9...C21B"),
        ]
        for lvl, msg in boot:
            self._add_log("SISTEMA", lvl, msg, C_GREEN)

    def _add_attack_log(self):
        if self._log_index >= len(ATTACK_LOGS):
            return
        tag, lvl, msg = ATTACK_LOGS[self._log_index]
        color = C_RED if lvl == "CRIT" else C_AMBER
        self._add_log(tag, lvl, msg, color)
        self._log_index += 1
        self._alert_count += 1
        self.footer_alert.setText(f"Alertas activas: {self._alert_count}")

    def _add_log(self, tag: str, level: str, msg: str, color: str):
        ts  = datetime.now().strftime("%H:%M:%S")
        lvl_colors = {"OK": C_GREEN, "WARN": C_AMBER, "CRIT": C_RED, "INFO": C_BLUE}
        lvl_c = lvl_colors.get(level, C_MUTED)

        item = QListWidgetItem(f"  {ts}  [{level:<5}]  {msg}")
        item.setForeground(QColor(color))
        item.setFont(FONT_MONO)
        self.log_list.addItem(item)
        self.log_list.scrollToBottom()

    def _clear_logs(self):
        self.log_list.clear()

    def _set_indicator_from_bios(self, enabled: bool):
        """Recibe el estado de Secure Boot desde la pantalla BIOS Setup."""
        if enabled:
            self._set_indicator("sb", C_GREEN, "ACTIVO")
            self.stat_sb.set_value("ACTIVO", C_GREEN)
            self._add_log("BIOS", "OK", "Secure Boot activado desde BIOS Setup.", C_GREEN)
        else:
            self._set_indicator("sb", C_RED, "DESACTIVADO")
            self.stat_sb.set_value("INACTIVO", C_RED)
            self._add_log("BIOS", "WARN", "ADVERTENCIA: Secure Boot desactivado desde BIOS Setup.", C_AMBER)

    # ------------------------------------------------------------------
    # TIMERS
    # ------------------------------------------------------------------
    def _tick_buses(self):
        for row in self.bus_rows.values():
            row.tick()

    def _blink_badge(self):
        if self._injected:
            self._blink_state = not self._blink_state
            color = C_RED if self._blink_state else "#800000"
            self.log_dot.setStyleSheet(f"color: {color}; background: transparent;")
        else:
            self.log_dot.setStyleSheet(f"color: {C_GREEN}; background: transparent;")


# ---------------------------------------------------------------------------
# VENTANA PRINCIPAL (para prueba standalone)
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UTP SecureSim — Cybersecurity Dashboard")
        self.setMinimumSize(1000, 640)
        self.resize(1200, 760)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(C_ROOT))
        self.setPalette(palette)

        self.dashboard = CyberDashboard()
        self.setCentralWidget(self.dashboard)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
