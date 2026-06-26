"""
UTP SecureSim — Pantalla 2: BIOS Setup Menu
============================================
Interfaz retro estilo AMI BIOS años 90, navegable con teclado y ratón.
Requiere: pip install PyQt6

Uso:
    python bios_setup.py
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QKeyEvent

# ---------------------------------------------------------------------------
# PALETA AMI BIOS AÑOS 90
# ---------------------------------------------------------------------------
C_BG         = "#000080"   # Azul cobalto fondo
C_CYAN       = "#00AAAA"   # Cian — barra título y estado
C_CYAN_TEXT  = "#000080"   # Texto sobre cian
C_TEXT       = "#C0C0C0"   # Gris claro — etiquetas
C_VALUE      = "#FFFF55"   # Amarillo — valores
C_ON         = "#55FF55"   # Verde — estado ON
C_OFF        = "#FF5555"   # Rojo — estado OFF
C_WARN_VAL   = "#FFAA00"   # Naranja — advertencia
C_SEL_BG     = "#00AAAA"   # Fondo fila seleccionada
C_SEL_TEXT   = "#000080"   # Texto fila seleccionada
C_SEP        = "#0000CC"   # Separadores
C_INFO_BG    = "#000060"   # Panel de info
C_HELP_BG    = "#555555"   # Barra de ayuda

FONT_MAIN = QFont("Courier New", 10)
FONT_BOLD = QFont("Courier New", 10)
FONT_BOLD.setBold(True)
FONT_SM   = QFont("Courier New", 9)

# ---------------------------------------------------------------------------
# DATOS DE LAS FILAS DEL MENÚ
# ---------------------------------------------------------------------------
BIOS_ROWS = {
    "left": [
        {
            "group": "STANDARD CMOS FEATURES",
            "items": [
                {"key": "Date / Time",    "val": "06/05/2025  14:32", "vtype": "normal",
                 "info_title": "Date / Time",
                 "info_desc": "Configura la fecha y hora del RTC del sistema. Afecta la validación de certificados en Secure Boot y los logs de auditoría del TPM."},
                {"key": "Language",       "val": "English", "vtype": "normal",
                 "info_title": "Language",
                 "info_desc": "Idioma de presentación del firmware UEFI. No afecta la funcionalidad de seguridad."},
            ]
        },
        {
            "group": "BOOT SEQUENCE",
            "items": [
                {"key": "1st Boot Device", "val": "NVMe SSD",   "vtype": "warn",
                 "id": "boot1",
                 "info_title": "1st Boot Device",
                 "info_desc": "Define la prioridad de arranque. El bootloader se carga desde el primer dispositivo activo. Con Secure Boot activo, cada componente del bootloader debe estar firmado criptográficamente."},
                {"key": "2nd Boot Device", "val": "USB Drive",  "vtype": "normal",
                 "info_title": "2nd Boot Device",
                 "info_desc": "Segundo dispositivo de arranque si el primero falla o no es bootable."},
                {"key": "3rd Boot Device", "val": "LAN / PXE",  "vtype": "normal",
                 "info_title": "3rd Boot Device",
                 "info_desc": "Arranque por red via PXE. Requiere configuración del servidor DHCP/TFTP."},
            ]
        },
        {
            "group": "ADVANCED CHIPSET",
            "items": [
                {"key": "DMI Gen",      "val": "4.0 (x16)", "vtype": "normal",
                 "info_title": "DMI Gen",
                 "info_desc": "Direct Media Interface — bus de alta velocidad entre CPU y PCH. DMI 4.0 ofrece 16 GT/s de ancho de banda."},
                {"key": "PCIe Speed",   "val": "Gen 5.0",   "vtype": "normal",
                 "info_title": "PCIe Speed",
                 "info_desc": "Velocidad del bus PCIe para GPU y almacenamiento NVMe. Gen 5.0 = 32 GT/s por carril."},
            ]
        },
    ],
    "right": [
        {
            "group": "SECURITY / SECURE BOOT",
            "items": [
                {"key": "Secure Boot",       "val": "[ ENABLED ]", "vtype": "on",
                 "id": "secure_boot",
                 "info_title": "Secure Boot",
                 "info_desc": "ACTIVADO: todos los módulos UEFI deben estar firmados. DESACTIVADO: el sistema cargará cualquier código sin verificación — rootkits pueden operar sin restricción. Use Enter para cambiar."},
                {"key": "Secure Boot Mode",  "val": "Standard",    "vtype": "normal",
                 "id": "sb_mode",
                 "info_title": "Secure Boot Mode",
                 "info_desc": "Standard: usa db/dbx de Microsoft. Custom: permite cargar llaves propias del laboratorio."},
                {"key": "Platform Key (PK)", "val": "Enrolled ✓",  "vtype": "on",
                 "info_title": "Platform Key (PK)",
                 "info_desc": "Llave raíz de la cadena de confianza UEFI. Firmada por el fabricante. Cambiarla requiere privilegios físicos."},
                {"key": "Key Exch. Key (KEK)","val": "Enrolled ✓", "vtype": "on",
                 "info_title": "Key Exchange Key (KEK)",
                 "info_desc": "Llave intermedia que autoriza actualizaciones de db/dbx."},
                {"key": "db / dbx Database", "val": "OK / 47 entries","vtype": "on",
                 "info_title": "db / dbx Database",
                 "info_desc": "db: firmas permitidas. dbx: firmas revocadas. El UEFI compara cada módulo cargado contra estas bases. Un rootkit añadiría su firma a db."},
            ]
        },
        {
            "group": "TPM / HARDWARE SECURITY",
            "items": [
                {"key": "TPM 2.0 Device",   "val": "Present / Active", "vtype": "on",
                 "info_title": "TPM 2.0 Device",
                 "info_desc": "Trusted Platform Module — chip criptográfico para almacenamiento seguro de claves y medición del arranque (PCR registers)."},
                {"key": "Measured Boot (PCR)","val": "Enabled", "vtype": "on",
                 "info_title": "Measured Boot",
                 "info_desc": "PCR[0-7] del TPM registran un hash de cada componente del arranque. Cualquier modificación produce un hash diferente, detectable por el sistema."},
            ]
        },
        {
            "group": "POWER MANAGEMENT",
            "items": [
                {"key": "Wake on LAN",      "val": "Disabled",  "vtype": "off",
                 "info_title": "Wake on LAN",
                 "info_desc": "Permite encender el equipo mediante paquete mágico de red. Desactivado por seguridad en entornos sensibles."},
                {"key": "ACPI Sleep State", "val": "S3 (Suspend)","vtype": "normal",
                 "info_title": "ACPI Sleep State",
                 "info_desc": "S3: suspende RAM, apaga el resto. S4: hiberna a disco. S5: apagado completo."},
            ]
        },
    ]
}

BOOT_DEVICES = ["NVMe SSD", "USB Drive", "LAN / PXE", "DVD/CD-ROM"]


# ---------------------------------------------------------------------------
# WIDGET: Fila individual del menú BIOS
# ---------------------------------------------------------------------------
class BiosRow(QFrame):
    clicked_signal = pyqtSignal(dict)

    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.item = item
        self.selected = False
        self.setFixedHeight(22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build()
        self._apply_style(False)

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(0)

        self.key_lbl = QLabel(self.item["key"])
        self.key_lbl.setFont(FONT_MAIN)
        layout.addWidget(self.key_lbl)

        layout.addStretch()

        self.val_lbl = QLabel(self.item["val"])
        self.val_lbl.setFont(FONT_BOLD)
        layout.addWidget(self.val_lbl)

        self._update_value_color(False)

    def _update_value_color(self, selected: bool):
        if selected:
            self.val_lbl.setStyleSheet(f"color: {C_SEL_TEXT}; background: transparent;")
        else:
            vtype = self.item.get("vtype", "normal")
            color_map = {
                "on":     C_ON,
                "off":    C_OFF,
                "warn":   C_WARN_VAL,
                "normal": C_VALUE,
            }
            self.val_lbl.setStyleSheet(
                f"color: {color_map.get(vtype, C_VALUE)}; background: transparent;"
            )

    def _apply_style(self, selected: bool):
        self.selected = selected
        if selected:
            self.setStyleSheet(f"background: {C_SEL_BG}; border-radius: 2px;")
            self.key_lbl.setStyleSheet(f"color: {C_SEL_TEXT}; background: transparent;")
        else:
            self.setStyleSheet(f"background: transparent;")
            self.key_lbl.setStyleSheet(f"color: {C_TEXT}; background: transparent;")
        self._update_value_color(selected)

    def set_selected(self, state: bool):
        self._apply_style(state)

    def update_value(self, new_val: str, new_vtype: str = "normal"):
        self.item["val"] = new_val
        self.item["vtype"] = new_vtype
        self.val_lbl.setText(new_val)
        self._update_value_color(self.selected)

    def mousePressEvent(self, event):
        self.clicked_signal.emit(self.item)
        super().mousePressEvent(event)


# ---------------------------------------------------------------------------
# PANTALLA BIOS SETUP
# ---------------------------------------------------------------------------
class BiosSetupScreen(QWidget):
    go_back   = pyqtSignal()             # F10 / ESC → volver a POST
    sb_changed = pyqtSignal(bool)        # Notifica al Dashboard el estado de Secure Boot

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sb_enabled = True
        self._boot_index = 0
        self._all_rows: list[BiosRow] = []
        self._selected_index = 0
        self._row_lookup: dict[str, BiosRow] = {}
        self._build_ui()
        self._select_row(0)

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
        # Encabezado cian
        root.addWidget(self._make_header())
        # Cuerpo — dos columnas
        root.addWidget(self._make_body(), 1)
        # Barra de estado
        self.status_bar = self._make_status_bar()
        root.addWidget(self.status_bar)
        # Panel de info
        root.addWidget(self._make_info_panel())
        # Barra de ayuda
        root.addWidget(self._make_help_bar())
        # Controles interactivos
        root.addWidget(self._make_controls())

    def _make_titlebar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(28)
        bar.setStyleSheet(f"background: #0000A0; border-bottom: 1px solid #0000CC;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)

        lbl = QLabel("CMOS SETUP UTILITY")
        lbl.setFont(FONT_BOLD)
        lbl.setStyleSheet(f"color: {C_CYAN}; background: transparent;")
        layout.addWidget(lbl)
        layout.addStretch()

        scr = QLabel("SCREEN 2 — BIOS Setup Menu")
        scr.setFont(FONT_SM)
        scr.setStyleSheet(f"color: #2A3A5A; background: transparent;")
        layout.addWidget(scr)
        return bar

    def _make_header(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(26)
        bar.setStyleSheet(f"background: {C_CYAN};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("◄  UTP SecureSim BIOS — ADVANCED SETUP  ►")
        lbl.setFont(FONT_BOLD)
        lbl.setStyleSheet(f"color: {C_CYAN_TEXT}; background: transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        return bar

    def _make_body(self) -> QWidget:
        body = QWidget()
        body.setStyleSheet(f"background: {C_BG};")
        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._make_column(BIOS_ROWS["left"]))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {C_SEP};")
        layout.addWidget(sep)

        layout.addWidget(self._make_column(BIOS_ROWS["right"]))
        return body

    def _make_column(self, groups: list) -> QWidget:
        col = QWidget()
        col.setStyleSheet(f"background: {C_BG};")
        layout = QVBoxLayout(col)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(0)

        for group in groups:
            # Título de grupo
            grp_lbl = QLabel(f"▸ {group['group']}")
            grp_lbl.setFont(FONT_BOLD)
            grp_lbl.setStyleSheet(f"color: {C_VALUE}; background: transparent; margin-top: 6px;")
            grp_lbl.setFixedHeight(20)
            layout.addWidget(grp_lbl)

            for item in group["items"]:
                row = BiosRow(item)
                row.clicked_signal.connect(self._on_row_clicked)
                if "id" in item:
                    self._row_lookup[item["id"]] = row
                self._all_rows.append(row)
                layout.addWidget(row)

            # Separador
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"background: {C_SEP}; margin: 4px 0px;")
            sep.setFixedHeight(1)
            layout.addWidget(sep)

        layout.addStretch()
        return col

    def _make_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(24)
        bar.setStyleSheet(f"background: {C_CYAN};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 14, 0)

        self.status_left = QLabel("Use ↑ ↓ para navegar  |  Enter para modificar")
        self.status_left.setFont(FONT_SM)
        self.status_left.setStyleSheet(f"color: {C_CYAN_TEXT}; background: transparent;")
        layout.addWidget(self.status_left)

        layout.addStretch()

        self.status_right = QLabel("Secure Boot: ACTIVO")
        self.status_right.setFont(FONT_SM)
        self.status_right.setStyleSheet(f"color: #006600; background: transparent;")
        layout.addWidget(self.status_right)

        return bar

    def _make_info_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedHeight(60)
        panel.setStyleSheet(f"background: {C_INFO_BG}; border-top: 1px solid {C_SEP};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(2)

        self.info_title = QLabel("Boot Order — Dispositivo de arranque primario")
        self.info_title.setFont(FONT_BOLD)
        self.info_title.setStyleSheet(f"color: {C_VALUE}; background: transparent;")
        layout.addWidget(self.info_title)

        self.info_desc = QLabel("Define la prioridad de arranque. El bootloader se carga desde el primer dispositivo activo.")
        self.info_desc.setFont(FONT_SM)
        self.info_desc.setStyleSheet(f"color: #AAAAAA; background: transparent;")
        self.info_desc.setWordWrap(True)
        layout.addWidget(self.info_desc)

        return panel

    def _make_help_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(24)
        bar.setStyleSheet(f"background: {C_HELP_BG};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(20)

        shortcuts = [
            ("↑↓", "Navegar"),
            ("Enter", "Seleccionar"),
            ("+/-", "Cambiar valor"),
            ("F9", "Defaults"),
            ("F10", "Guardar & salir"),
            ("ESC", "Salir sin guardar"),
        ]
        for key, desc in shortcuts:
            lbl = QLabel()
            lbl.setFont(FONT_SM)
            lbl.setText(f"<span style='color:{C_VALUE};font-weight:bold'>{key}</span>"
                        f"<span style='color:#ffffff'> {desc}</span>")
            lbl.setStyleSheet("background: transparent;")
            layout.addWidget(lbl)

        layout.addStretch()
        return bar

    def _make_controls(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"background: #00004A; border-top: 1px solid #1A1A3A;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(8)

        def btn(text, slot):
            b = QPushButton(text)
            b.setFont(FONT_SM)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {C_CYAN};
                    color: {C_CYAN};
                    padding: 3px 10px;
                    border-radius: 2px;
                }}
                QPushButton:hover {{
                    background: {C_CYAN};
                    color: {C_CYAN_TEXT};
                }}
            """)
            b.clicked.connect(slot)
            return b

        layout.addWidget(btn("Toggle Secure Boot", self._toggle_secure_boot))
        layout.addWidget(btn("Cambiar Boot Device", self._cycle_boot))
        layout.addStretch()

        hint = QLabel("Interactivo — haz clic en cualquier fila o usa teclado")
        hint.setFont(FONT_SM)
        hint.setStyleSheet(f"color: #005588; background: transparent;")
        layout.addWidget(hint)
        return bar

    # ------------------------------------------------------------------
    # LÓGICA DE INTERACCIÓN
    # ------------------------------------------------------------------
    def _select_row(self, index: int):
        if not self._all_rows:
            return
        index = max(0, min(index, len(self._all_rows) - 1))
        if self._selected_index < len(self._all_rows):
            self._all_rows[self._selected_index].set_selected(False)
        self._selected_index = index
        row = self._all_rows[index]
        row.set_selected(True)
        self.info_title.setText(row.item.get("info_title", row.item["key"]))
        self.info_desc.setText(row.item.get("info_desc", ""))

    def _on_row_clicked(self, item: dict):
        for i, row in enumerate(self._all_rows):
            if row.item is item:
                self._select_row(i)
                break

    def _toggle_secure_boot(self):
        self._sb_enabled = not self._sb_enabled
        row = self._row_lookup.get("secure_boot")
        mode_row = self._row_lookup.get("sb_mode")

        if self._sb_enabled:
            if row:
                row.update_value("[ ENABLED ]", "on")
            if mode_row:
                mode_row.update_value("Standard", "normal")
            self.status_right.setText("Secure Boot: ACTIVO")
            self.status_right.setStyleSheet(f"color: #006600; background: transparent;")
            self.info_title.setText("Secure Boot — Estado cambiado")
            self.info_desc.setText(
                "ACTIVADO. Todos los módulos UEFI deben estar firmados. "
                "Rootkits de firmware no podrán ejecutarse sin firma válida en db."
            )
        else:
            if row:
                row.update_value("[ DISABLED ]", "off")
            if mode_row:
                mode_row.update_value("Setup Mode", "warn")
            self.status_right.setText("!! Secure Boot: INACTIVO !!")
            self.status_right.setStyleSheet(f"color: {C_OFF}; background: transparent;")
            self.info_title.setText("ADVERTENCIA — Secure Boot desactivado")
            self.info_desc.setText(
                "PELIGRO: el sistema cargará cualquier código de arranque sin verificación. "
                "Rootkits de firmware pueden operar sin restricción."
            )

        self.sb_changed.emit(self._sb_enabled)

    def _cycle_boot(self):
        self._boot_index = (self._boot_index + 1) % len(BOOT_DEVICES)
        row = self._row_lookup.get("boot1")
        if row:
            new_dev = BOOT_DEVICES[self._boot_index]
            row.update_value(new_dev, "warn")
            self.info_title.setText("1st Boot Device cambiado")
            self.info_desc.setText(
                f"Nuevo dispositivo primario: {new_dev}. "
                "El sistema intentará cargar el bootloader desde este dispositivo primero."
            )

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Up:
            self._select_row(self._selected_index - 1)
        elif key == Qt.Key.Key_Down:
            self._select_row(self._selected_index + 1)
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            current = self._all_rows[self._selected_index].item
            item_id = current.get("id", "")
            if item_id == "secure_boot":
                self._toggle_secure_boot()
            elif item_id == "boot1":
                self._cycle_boot()
        elif key == Qt.Key.Key_F10 or key == Qt.Key.Key_Escape:
            self.go_back.emit()
        super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# VENTANA PRINCIPAL (para prueba standalone)
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UTP SecureSim — BIOS Setup")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(C_BG))
        self.setPalette(palette)

        self.bios = BiosSetupScreen()
        self.bios.go_back.connect(lambda: print("[SIGNAL] → Volver a POST"))
        self.bios.sb_changed.connect(lambda s: print(f"[SIGNAL] Secure Boot → {'ON' if s else 'OFF'}"))
        self.setCentralWidget(self.bios)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
