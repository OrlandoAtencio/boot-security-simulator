"""
UTP SecureSim — Pantalla 3: Panel de Ciberseguridad FASE 4
===========================================================
Dashboard con manejo de estados avanzado, paneles alternos,
alertas gráficas integradas y eventos globales del sistema.
Requiere: pip install PyQt6
"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QListWidget, QListWidgetItem,
    QComboBox, QProgressBar, QSizePolicy, QStackedWidget,
    QMessageBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPen, QBrush

# ---------------------------------------------------------------------------
# PALETA
# ---------------------------------------------------------------------------
C_ROOT   = "#0D1117"
C_CARD   = "#161B22"
C_BORDER = "#21262D"
C_TEXT   = "#F0F6FC"
C_MUTED  = "#8B949E"
C_BLUE   = "#58A6FF"
C_GREEN  = "#3FB950"
C_AMBER  = "#D29922"
C_RED    = "#F85149"
C_PURPLE = "#BC8CFF"

FONT_MAIN = QFont("Segoe UI", 10)
FONT_MONO = QFont("Courier New", 9)
FONT_BOLD = QFont("Segoe UI", 10)
FONT_BOLD.setBold(True)
FONT_SM   = QFont("Segoe UI", 9)
FONT_BIG  = QFont("Segoe UI", 18)
FONT_BIG.setBold(True)

ROOTKIT_TYPES = [
    "Bootkitty — UEFI Bootloader Hook",
    "FinFisher — SPI Flash Rootkit",
    "CosmicStrand — Firmware Implant",
    "BlackLotus — Secure Boot Bypass",
]

ATTACK_LOGS = [
    ("WARN", "Escritura no autorizada en SPI Flash 0x00080000"),
    ("CRIT", "Rootkit detectado: hook en vector de interrupción 0x13"),
    ("CRIT", "Modificación de db signature database — entrada rogue"),
    ("WARN", "Bus de control SPI: paquete malformado interceptado"),
    ("CRIT", "UEFI Vol.0 comprometido — hash SHA-256 no coincide"),
    ("WARN", "Acceso anómalo en 0xFFFF800012C00000"),
    ("CRIT", "Intento de escalada de privilegios en Ring-0"),
    ("WARN", "PCR[7] del TPM cambió inesperadamente"),
]

MITIGATION_LOGS = [
    ("OK", "Secure Boot reafirmado — verificando db/dbx..."),
    ("OK", "Firma SHA-256 del bootloader verificada"),
    ("OK", "TPM PCR[0-7] restaurados desde medición de referencia"),
    ("OK", "UEFI Vol.0 restaurado desde backup TPM-sellado"),
    ("OK", "Entrada rogue eliminada de db signature database"),
    ("OK", "Sistema limpio. Integridad de firmware confirmada"),
]


# ---------------------------------------------------------------------------
# WIDGET: Bus animado
# ---------------------------------------------------------------------------
class BusWidget(QWidget):
    def __init__(self, color_normal: str, parent=None):
        super().__init__(parent)
        self.color_normal = QColor(color_normal)
        self.color_attack  = QColor(C_RED)
        self.is_attack     = False
        self.pkt_pos       = 0.0
        self.pkt_speed     = 0.018
        self.pkt_width     = 0.14
        self.setFixedHeight(28)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_attack(self, state: bool):
        self.is_attack  = state
        self.pkt_speed  = 0.045 if state else 0.018

    def tick(self):
        self.pkt_pos = (self.pkt_pos + self.pkt_speed) % 1.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        track = QRect(0, (h - 12) // 2, w, 12)
        painter.setBrush(QBrush(QColor("#0D1117")))
        painter.setPen(QPen(QColor(C_BORDER), 1))
        painter.drawRoundedRect(track, 3, 3)

        color = self.color_attack if self.is_attack else self.color_normal
        trail = QColor(color)
        trail.setAlpha(60)

        pkt_x = int(self.pkt_pos * w)
        pkt_w = max(20, int(self.pkt_width * w))

        if pkt_x - pkt_w > 0:
            painter.setBrush(QBrush(trail))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                QRect(pkt_x - pkt_w, (h - 8) // 2, pkt_w, 8), 2, 2)

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            QRect(pkt_x % w, (h - 8) // 2, pkt_w, 8), 2, 2)
        painter.end()


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

        self.bus = BusWidget(color)
        layout.addWidget(self.bus, 1)

        self.speed_lbl = QLabel(speed)
        self.speed_lbl.setFont(FONT_MONO)
        self.speed_lbl.setStyleSheet(f"color: {C_BLUE}; background: transparent;")
        self.speed_lbl.setFixedWidth(130)
        self.speed_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.speed_lbl)

        self.dot = QLabel("●")
        self.dot.setFont(QFont("Segoe UI", 10))
        self.dot.setStyleSheet(f"color: {C_GREEN}; background: transparent;")
        self.dot.setFixedWidth(16)
        layout.addWidget(self.dot)

    def set_attack(self, state: bool, speed_text: str):
        self.bus.set_attack(state)
        color = C_RED if state else C_BLUE
        self.speed_lbl.setStyleSheet(f"color: {color}; background: transparent;")
        self.speed_lbl.setText(speed_text)
        self.dot.setStyleSheet(f"color: {C_RED if state else C_GREEN}; background: transparent;")

    def tick(self):
        self.bus.tick()


class StatCard(QWidget):
    def __init__(self, label: str, value: str, value_color: str = C_TEXT, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_CARD};border:1px solid {C_BORDER};border-radius:8px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        self.lbl = QLabel(label)
        self.lbl.setFont(FONT_SM)
        self.lbl.setStyleSheet(f"color:{C_MUTED};background:transparent;border:none;")
        layout.addWidget(self.lbl)

        self.val = QLabel(value)
        self.val.setFont(FONT_BIG)
        self.val.setStyleSheet(f"color:{value_color};background:transparent;border:none;")
        layout.addWidget(self.val)

    def set_value(self, text: str, color: str):
        self.val.setText(text)
        self.val.setStyleSheet(f"color:{color};background:transparent;border:none;")


# ---------------------------------------------------------------------------
# PANEL DE DETALLES TÉCNICOS (panel alterno — Tarea 2 Fase 4)
# ---------------------------------------------------------------------------
class TechDetailsPanel(QWidget):
    """
    Panel alterno que muestra detalles técnicos del ataque o del estado
    seguro del sistema. Se activa con el botón "Ver Detalles Técnicos".
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_CARD};border:1px solid {C_BORDER};border-radius:8px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title = QLabel("DETALLES TÉCNICOS DEL SISTEMA")
        title.setFont(QFont("Segoe UI", 9))
        title.setStyleSheet(f"color:{C_MUTED};background:transparent;font-weight:bold;letter-spacing:1px;")
        layout.addWidget(title)

        self.details_list = QListWidget()
        self.details_list.setFont(FONT_MONO)
        self.details_list.setStyleSheet(f"""
            QListWidget {{ background:{C_ROOT};border:none;padding:4px; }}
            QListWidget::item {{ color:{C_MUTED};padding:2px 0;background:transparent;border:none; }}
        """)
        layout.addWidget(self.details_list)

        self.set_normal_state()

    def set_normal_state(self):
        self.details_list.clear()
        items = [
            (C_GREEN,  "UEFI Firmware:    v2.31.1 — Íntegro"),
            (C_GREEN,  "SPI Flash:        Región protegida — Sin escrituras"),
            (C_GREEN,  "Platform Key:     SHA-256: A3F9...C21B — Válida"),
            (C_GREEN,  "db Signatures:    47 entradas — Todas verificadas"),
            (C_GREEN,  "dbx Revocados:    12 entradas — Actualizados"),
            (C_GREEN,  "TPM PCR[0]:       0x4A2F...8E1D — Medición OK"),
            (C_GREEN,  "TPM PCR[7]:       0x1B3C...5F2A — Secure Boot OK"),
            (C_BLUE,   "Boot Chain:       UEFI → Shim → GRUB → Kernel"),
            (C_BLUE,   "Microcode:        0x0024 — Intel Verified"),
        ]
        for color, text in items:
            item = QListWidgetItem(text)
            item.setForeground(QColor(color))
            item.setFont(FONT_MONO)
            self.details_list.addItem(item)

    def set_attack_state(self, rootkit_name: str):
        self.details_list.clear()
        items = [
            (C_RED,    f"ROOTKIT:          {rootkit_name}"),
            (C_RED,    "SPI Flash:        ESCRITURA en 0x00080000 !!"),
            (C_RED,    "Platform Key:     Hash INVÁLIDO: 0xDEAD...BEEF"),
            (C_RED,    "db Signatures:    ENTRADA ROGUE detectada"),
            (C_AMBER,  "TPM PCR[7]:       Cambio inesperado detectado"),
            (C_AMBER,  "Boot Chain:       Modificada — Verificación FALLA"),
            (C_RED,    "UEFI Vol.0:       SHA-256 NO COINCIDE"),
            (C_AMBER,  "Ring-0:           Intento de escalada detectado"),
            (C_RED,    "ESTADO:           SISTEMA COMPROMETIDO"),
        ]
        for color, text in items:
            item = QListWidgetItem(text)
            item.setForeground(QColor(color))
            item.setFont(FONT_MONO)
            self.details_list.addItem(item)

    def set_mitigated_state(self):
        self.details_list.clear()
        items = [
            (C_GREEN,  "MITIGACIÓN:       Completada exitosamente"),
            (C_GREEN,  "SPI Flash:        Restaurada desde backup TPM"),
            (C_GREEN,  "Platform Key:     SHA-256: A3F9...C21B — Restaurada"),
            (C_GREEN,  "db Signatures:    Entrada rogue eliminada"),
            (C_GREEN,  "TPM PCR[0-7]:     Restaurados a valores de referencia"),
            (C_GREEN,  "UEFI Vol.0:       Hash verificado — Íntegro"),
            (C_GREEN,  "Boot Chain:       Restaurada y verificada"),
            (C_GREEN,  "Secure Boot:      ACTIVO y funcional"),
            (C_GREEN,  "ESTADO:           SISTEMA SEGURO"),
        ]
        for color, text in items:
            item = QListWidgetItem(text)
            item.setForeground(QColor(color))
            item.setFont(FONT_MONO)
            self.details_list.addItem(item)


# ---------------------------------------------------------------------------
# DASHBOARD FASE 4
# ---------------------------------------------------------------------------
class CyberDashboard(QWidget):
    # Señales para comunicar eventos al main
    rootkit_injected  = pyqtSignal(str)
    rootkit_mitigated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._injected    = False
        self._log_index   = 0
        self._alert_count = 0
        self._blink_state = False
        self._show_details = False

        self._bus_timer = QTimer(self)
        self._bus_timer.timeout.connect(self._tick_buses)
        self._bus_timer.start(60)

        self._log_timer = QTimer(self)
        self._log_timer.timeout.connect(self._add_attack_log)

        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink_badge)
        self._blink_timer.start(600)

        self._build_ui()
        self._add_boot_log()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.setStyleSheet(f"background:{C_ROOT};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_topbar())

        body = QHBoxLayout()
        body.setContentsMargins(12, 10, 12, 10)
        body.setSpacing(10)

        # Columna principal con QStackedWidget para alternar paneles
        self.main_stack = QStackedWidget()
        self.main_stack.addWidget(self._make_main_panel())      # índice 0 — normal
        self.main_stack.addWidget(self._make_details_panel())   # índice 1 — detalles técnicos
        body.addWidget(self.main_stack, 1)

        body.addWidget(self._make_sidebar(), 0)

        body_w = QWidget()
        body_w.setStyleSheet(f"background:{C_ROOT};")
        body_w.setLayout(body)
        root.addWidget(body_w, 1)
        root.addWidget(self._make_footer())

    def _make_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"background:{C_CARD};border-bottom:1px solid {C_BORDER};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        logo = QLabel("⬡ UTP SecureSim")
        logo.setFont(QFont("Segoe UI", 12))
        logo.setStyleSheet(f"color:{C_BLUE};background:transparent;font-weight:bold;")
        layout.addWidget(logo)

        self.system_badge = QLabel("SISTEMA SEGURO")
        self.system_badge.setFont(FONT_SM)
        self.system_badge.setStyleSheet(self._badge_style(C_GREEN, "#1F3A1F"))
        layout.addWidget(self.system_badge)

        layout.addStretch()

        # Botón alternar panel — Tarea 2 Fase 4
        self.btn_toggle_panel = QPushButton("Ver Detalles Técnicos")
        self.btn_toggle_panel.setFont(FONT_SM)
        self.btn_toggle_panel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_panel.setStyleSheet(f"""
            QPushButton {{
                background:transparent;border:1px solid {C_BORDER};
                color:{C_MUTED};padding:4px 12px;border-radius:5px;
            }}
            QPushButton:hover {{ border-color:{C_BLUE};color:{C_BLUE}; }}
        """)
        self.btn_toggle_panel.clicked.connect(self._toggle_panel)
        layout.addWidget(self.btn_toggle_panel)

        scr = QLabel("SCREEN 3 — Cybersecurity Dashboard")
        scr.setFont(FONT_SM)
        scr.setStyleSheet(f"color:#30363D;background:transparent;")
        layout.addWidget(scr)
        return bar

    def _make_main_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet(f"background:{C_ROOT};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        stats = QHBoxLayout()
        stats.setSpacing(8)
        self.stat_system = StatCard("Estado del Sistema", "SEGURO",   C_GREEN)
        self.stat_threat  = StatCard("Nivel de Amenaza",  "0%",       C_GREEN)
        self.stat_sb      = StatCard("Secure Boot",       "ACTIVO",   C_GREEN)
        self.stat_uefi    = StatCard("Integridad UEFI",   "100%",     C_GREEN)
        for c in [self.stat_system, self.stat_threat, self.stat_sb, self.stat_uefi]:
            stats.addWidget(c)
        layout.addLayout(stats)
        layout.addWidget(self._make_bus_panel())
        layout.addWidget(self._make_log_panel(), 1)
        return panel

    def _make_details_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet(f"background:{C_ROOT};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tech_details = TechDetailsPanel()
        layout.addWidget(self.tech_details)
        return panel

    def _make_bus_panel(self) -> QWidget:
        panel = self._card()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        t = QLabel("MONITOREO DE BUSES DE DATOS — Actividad en tiempo real")
        t.setFont(QFont("Segoe UI", 9))
        t.setStyleSheet(f"color:{C_MUTED};background:transparent;font-weight:bold;")
        layout.addWidget(t)

        self.bus_rows = {
            "data": BusRow("Bus de Datos",    "64-bit / Normal",  "#1F4A8A"),
            "addr": BusRow("Bus de Dirección","48-bit / Normal",  "#1A4A1A"),
            "ctrl": BusRow("Bus de Control",  "SPI / Normal",     "#3A2A00"),
            "spi":  BusRow("SPI Flash (BIOS)","33MHz / Idle",     "#1A2A3A"),
        }
        for row in self.bus_rows.values():
            layout.addWidget(row)
        return panel

    def _make_log_panel(self) -> QWidget:
        panel = self._card()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(30)
        header.setStyleSheet(f"background:{C_CARD};border-bottom:1px solid {C_BORDER};")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 0, 12, 0)

        self.log_dot = QLabel("●")
        self.log_dot.setFont(QFont("Segoe UI", 10))
        self.log_dot.setStyleSheet(f"color:{C_GREEN};background:transparent;")
        hl.addWidget(self.log_dot)

        hl.addWidget(self._muted_label("CONSOLA DE LOGS — Auditoría de Arranque", bold=True))
        hl.addStretch()

        btn_clear = QPushButton("Limpiar")
        btn_clear.setFont(FONT_SM)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(f"background:transparent;border:1px solid {C_BORDER};color:{C_MUTED};padding:2px 8px;border-radius:4px;")
        btn_clear.clicked.connect(self._clear_logs)
        hl.addWidget(btn_clear)
        layout.addWidget(header)

        self.log_list = QListWidget()
        self.log_list.setFont(FONT_MONO)
        self.log_list.setStyleSheet(f"""
            QListWidget {{ background:{C_ROOT};border:none;padding:4px 8px; }}
            QListWidget::item {{ padding:1px 0;color:{C_MUTED};background:transparent;border:none; }}
            QScrollBar:vertical {{ background:{C_ROOT};width:6px; }}
            QScrollBar::handle:vertical {{ background:#333;border-radius:3px; }}
        """)
        layout.addWidget(self.log_list, 1)
        return panel

    def _make_sidebar(self) -> QWidget:
        sb = QWidget()
        sb.setFixedWidth(280)
        sb.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(sb)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._make_attack_panel())
        layout.addWidget(self._make_threat_meter())
        layout.addWidget(self._make_status_indicators())
        layout.addStretch()
        return sb

    def _make_attack_panel(self) -> QWidget:
        panel = self._card()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        layout.addWidget(self._muted_label("PANEL DE ATAQUE / DEFENSA", bold=True))

        self.rk_combo = QComboBox()
        self.rk_combo.addItems(ROOTKIT_TYPES)
        self.rk_combo.setFont(FONT_SM)
        self.rk_combo.setStyleSheet(f"""
            QComboBox {{ background:{C_ROOT};border:1px solid {C_BORDER};color:{C_MUTED};padding:5px 8px;border-radius:6px; }}
            QComboBox QAbstractItemView {{ background:{C_CARD};color:{C_TEXT};selection-background-color:{C_BORDER}; }}
        """)
        layout.addWidget(self.rk_combo)

        self.btn_inject = QPushButton("⚡  Inyectar Rootkit")
        self.btn_inject.setFont(FONT_BOLD)
        self.btn_inject.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_inject.setStyleSheet(self._btn_style(C_RED, "#3A1F1F"))
        self.btn_inject.clicked.connect(self._inject_rootkit)
        layout.addWidget(self.btn_inject)

        self.btn_mitigate = QPushButton("🛡  Activar Mitigación")
        self.btn_mitigate.setFont(FONT_BOLD)
        self.btn_mitigate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mitigate.setStyleSheet(self._btn_style(C_GREEN, "#1F3A1F"))
        self.btn_mitigate.setEnabled(False)
        self.btn_mitigate.clicked.connect(self._mitigate_rootkit)
        layout.addWidget(self.btn_mitigate)
        return panel

    def _make_threat_meter(self) -> QWidget:
        panel = self._card()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        layout.addWidget(self._muted_label("NIVEL DE AMENAZA", bold=True))

        self.threat_bar = QProgressBar()
        self.threat_bar.setRange(0, 100)
        self.threat_bar.setValue(0)
        self.threat_bar.setFixedHeight(12)
        self.threat_bar.setTextVisible(False)
        self._set_threat_color(C_GREEN)
        layout.addWidget(self.threat_bar)

        scale = QHBoxLayout()
        for txt, color in [("BAJO", C_GREEN), ("MEDIO", C_AMBER), ("CRÍTICO", C_RED)]:
            lbl = QLabel(txt)
            lbl.setFont(QFont("Courier New", 8))
            lbl.setStyleSheet(f"color:{color};background:transparent;")
            if txt == "MEDIO":   lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            elif txt == "CRÍTICO": lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            scale.addWidget(lbl)
        layout.addLayout(scale)
        return panel

    def _make_status_indicators(self) -> QWidget:
        panel = self._card()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        self.indicators = {}
        for key, label, status in [
            ("sb",   "Secure Boot",    "ACTIVO"),
            ("tpm",  "TPM 2.0",        "OK"),
            ("uefi", "UEFI Integridad","ÍNTEGRO"),
        ]:
            row = QHBoxLayout()
            dot = QLabel("●")
            dot.setFont(QFont("Segoe UI", 12))
            dot.setStyleSheet(f"color:{C_GREEN};background:transparent;")
            dot.setFixedWidth(18)
            row.addWidget(dot)

            lbl = QLabel(label)
            lbl.setFont(FONT_SM)
            lbl.setStyleSheet(f"color:{C_TEXT};background:transparent;")
            row.addWidget(lbl)
            row.addStretch()

            sub = QLabel(status)
            sub.setFont(FONT_SM)
            sub.setStyleSheet(f"color:{C_MUTED};background:transparent;")
            row.addWidget(sub)

            self.indicators[key] = {"dot": dot, "lbl": lbl, "sub": sub}

            rw = QWidget()
            rw.setStyleSheet("background:transparent;")
            rw.setLayout(row)
            rw.setFixedHeight(26)
            layout.addWidget(rw)
        return panel

    def _make_footer(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(28)
        bar.setStyleSheet(f"background:{C_CARD};border-top:1px solid {C_BORDER};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(20)

        self.footer_cpu   = QLabel("CPU: 23%")
        self.footer_ram   = QLabel("RAM: 4.2 GB")
        self.footer_spi   = QLabel("SPI: Idle")
        self.footer_alert = QLabel("")
        for lbl in [self.footer_cpu, self.footer_ram, self.footer_spi, self.footer_alert]:
            lbl.setFont(FONT_SM)
            lbl.setStyleSheet(f"color:{C_MUTED};background:transparent;")
            layout.addWidget(lbl)

        layout.addStretch()
        ver = QLabel("UTP-CSE SecureSim v1.0 — Fase 4")
        ver.setFont(FONT_SM)
        ver.setStyleSheet(f"color:#30363D;background:transparent;")
        layout.addWidget(ver)
        return bar

    # ------------------------------------------------------------------
    # HELPERS DE ESTILO
    # ------------------------------------------------------------------
    def _card(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{C_CARD};border:1px solid {C_BORDER};border-radius:8px;")
        return w

    def _muted_label(self, text: str, bold: bool = False) -> QLabel:
        lbl = QLabel(text)
        font = QFont("Segoe UI", 9)
        if bold:
            font.setBold(True)
        lbl.setFont(font)
        lbl.setStyleSheet(f"color:{C_MUTED};background:transparent;letter-spacing:1px;")
        return lbl

    @staticmethod
    def _badge_style(color: str, bg: str) -> str:
        return (f"background:{bg};color:{color};border:1px solid {color};"
                f"border-radius:10px;padding:1px 10px;font-size:10px;")

    @staticmethod
    def _btn_style(color: str, bg: str) -> str:
        return f"""
            QPushButton {{
                background:{bg};border:1px solid {color};color:{color};
                padding:8px;border-radius:6px;font-weight:bold;font-size:11px;
            }}
            QPushButton:hover:enabled {{ background:{color};color:#fff; }}
            QPushButton:disabled {{ color:#555;border-color:#333;background:#111; }}
        """

    def _set_threat_color(self, color: str):
        self.threat_bar.setStyleSheet(f"""
            QProgressBar {{ background:{C_ROOT};border-radius:5px;border:none; }}
            QProgressBar::chunk {{ background:{color};border-radius:5px; }}
        """)

    # ------------------------------------------------------------------
    # TAREA 2 FASE 4 — Alternar paneles
    # ------------------------------------------------------------------
    def _toggle_panel(self):
        self._show_details = not self._show_details
        if self._show_details:
            self.main_stack.setCurrentIndex(1)
            self.btn_toggle_panel.setText("Ver Panel Principal")
            if self._injected:
                self.tech_details.set_attack_state(self.rk_combo.currentText())
            else:
                self.tech_details.set_normal_state()
        else:
            self.main_stack.setCurrentIndex(0)
            self.btn_toggle_panel.setText("Ver Detalles Técnicos")

    # ------------------------------------------------------------------
    # LÓGICA DE ATAQUE / MITIGACIÓN
    # ------------------------------------------------------------------
    def _inject_rootkit(self):
        if self._injected:
            return
        self._injected    = True
        self._log_index   = 0
        self._alert_count = 0
        rk = self.rk_combo.currentText()

        self.btn_inject.setEnabled(False)
        self.btn_mitigate.setEnabled(True)

        self.system_badge.setText("SISTEMA COMPROMETIDO")
        self.system_badge.setStyleSheet(self._badge_style(C_RED, "#3A1F1F"))
        self.stat_system.set_value("CRÍTICO", C_RED)
        self.stat_sb.set_value("VULNERADO",   C_RED)
        self.stat_uefi.set_value("12%",        C_RED)

        self._set_indicator("sb",   C_RED, "BYPASS")
        self._set_indicator("tpm",  C_RED, "ANOMALÍA")
        self._set_indicator("uefi", C_RED, "COMPROMETIDO")

        for key, speed in [("data","64-bit / ANOMALÍA"),("addr","48-bit / ANOMALÍA"),
                            ("ctrl","SPI / ATAQUE"),("spi","33MHz / ESCRITURA")]:
            self.bus_rows[key].set_attack(True, speed)

        self.footer_spi.setText("SPI: ESCRIBIENDO")
        self.footer_spi.setStyleSheet(f"color:{C_RED};background:transparent;")
        self.footer_alert.setText(f"Alertas: {self._alert_count}")
        self.footer_alert.setStyleSheet(f"color:{C_RED};background:transparent;")

        self._animate_threat(87, C_RED)
        self._add_log("ATAQUE", "INFO", f"Inyectando: {rk}", C_AMBER)
        self._log_timer.start(950)

        if self._show_details:
            self.tech_details.set_attack_state(rk)

        # Emitir señal al main para mostrar alerta gráfica
        self.rootkit_injected.emit(rk)

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
        self.stat_system.set_value("SEGURO", C_GREEN)
        self.stat_sb.set_value("ACTIVO",     C_GREEN)
        self.stat_uefi.set_value("100%",     C_GREEN)

        self._set_indicator("sb",   C_GREEN, "ACTIVO")
        self._set_indicator("tpm",  C_GREEN, "OK")
        self._set_indicator("uefi", C_GREEN, "ÍNTEGRO")

        for key, speed in [("data","64-bit / Normal"),("addr","48-bit / Normal"),
                            ("ctrl","SPI / Normal"),("spi","33MHz / Idle")]:
            self.bus_rows[key].set_attack(False, speed)
            self.bus_rows[key].speed_lbl.setStyleSheet(f"color:{C_BLUE};background:transparent;")

        self.footer_spi.setText("SPI: Idle")
        self.footer_spi.setStyleSheet(f"color:{C_GREEN};background:transparent;")
        self.footer_alert.setText("")
        self._alert_count = 0

        self._animate_threat(0, C_GREEN)

        for lvl, msg in MITIGATION_LOGS:
            self._add_log("DEFENSA", lvl, msg, C_GREEN)

        if self._show_details:
            self.tech_details.set_mitigated_state()

        # Emitir señal al main
        self.rootkit_mitigated.emit()

    def _set_indicator(self, key: str, color: str, status: str):
        ind = self.indicators[key]
        ind["dot"].setStyleSheet(f"color:{color};background:transparent;")
        ind["sub"].setText(status)
        ind["sub"].setStyleSheet(f"color:{color};background:transparent;")

    def _animate_threat(self, target: int, color: str):
        current = self.threat_bar.value()
        step = 3 if target > current else -3

        def _tick():
            val  = self.threat_bar.value()
            nval = val + step
            if (step > 0 and nval >= target) or (step < 0 and nval <= target):
                nval = target
                t.stop()
            self.threat_bar.setValue(nval)
            self.stat_threat.set_value(f"{nval}%", color)
            self._set_threat_color(color)

        t = QTimer(self)
        t.timeout.connect(_tick)
        t.start(25)

    # ------------------------------------------------------------------
    # LOGS
    # ------------------------------------------------------------------
    def _add_boot_log(self):
        for lvl, msg in [
            ("OK", "Sistema iniciado. UEFI v2.31 cargado correctamente."),
            ("OK", "TPM 2.0 inicializado. PCR[0-7] medidos."),
            ("OK", "Secure Boot activo. Verificando db/dbx..."),
            ("OK", "Bootloader firmado. Hash SHA-256: A3F9...C21B"),
        ]:
            self._add_log("SISTEMA", lvl, msg, C_GREEN)

    def _add_attack_log(self):
        if self._log_index >= len(ATTACK_LOGS):
            return
        lvl, msg = ATTACK_LOGS[self._log_index]
        color = C_RED if lvl == "CRIT" else C_AMBER
        self._add_log("ATAQUE", lvl, msg, color)
        self._log_index   += 1
        self._alert_count += 1
        self.footer_alert.setText(f"Alertas: {self._alert_count}")

    def _add_log(self, tag: str, level: str, msg: str, color: str):
        ts   = datetime.now().strftime("%H:%M:%S")
        item = QListWidgetItem(f"  {ts}  [{level:<5}]  {msg}")
        item.setForeground(QColor(color))
        item.setFont(FONT_MONO)
        self.log_list.addItem(item)
        self.log_list.scrollToBottom()

    def _clear_logs(self):
        self.log_list.clear()

    def _set_indicator_from_bios(self, enabled: bool):
        if enabled:
            self._set_indicator("sb", C_GREEN, "ACTIVO")
            self.stat_sb.set_value("ACTIVO", C_GREEN)
            self._add_log("BIOS", "OK", "Secure Boot activado desde BIOS Setup.", C_GREEN)
        else:
            self._set_indicator("sb", C_RED, "DESACTIVADO")
            self.stat_sb.set_value("INACTIVO", C_RED)
            self._add_log("BIOS", "WARN", "ADVERTENCIA: Secure Boot desactivado.", C_AMBER)

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
            self.log_dot.setStyleSheet(f"color:{color};background:transparent;")
        else:
            self.log_dot.setStyleSheet(f"color:{C_GREEN};background:transparent;")


# ---------------------------------------------------------------------------
# STANDALONE
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = QMainWindow()
    win.setWindowTitle("UTP SecureSim — Dashboard Fase 4")
    win.resize(1280, 760)
    dash = CyberDashboard()
    win.setCentralWidget(dash)
    win.show()
    sys.exit(app.exec())
