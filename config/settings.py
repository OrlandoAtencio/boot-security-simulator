"""
config/settings.py — Configuración Global del Simulador de Arranque Seguro
===========================================================================
Contiene TODAS las constantes, enumeraciones y configuraciones del proyecto.
Cualquier "número mágico" o constante compartida VIVE AQUÍ.

Responsable: Líder Técnico
ADVERTENCIA: No modificar sin consultar al Líder. Cambios aquí impactan TODO el proyecto.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Final, Dict

# ──────────────────────────────────────────────────────────────────────────────
# METADATOS DEL PROYECTO
# ──────────────────────────────────────────────────────────────────────────────
PROJECT_NAME: Final[str] = "Boot Security Simulator — UTP"
VERSION: Final[str] = "1.0.0"
AUTHORS: Final[str] = "Equipo 9 · Arquitectura y Organización de Computadoras"

# ──────────────────────────────────────────────────────────────────────────────
# TIMING DE SIMULACIÓN (milisegundos) — Ajustar para demos
# ──────────────────────────────────────────────────────────────────────────────
STEP_DELAY_MS: Final[int]   = 800     # Pausa entre etapas del arranque
ANIM_TICK_MS: Final[int]    = 50      # Tick de animación Tkinter (20 fps)
BUS_ANIM_SPEED_MS: Final[int] = 100   # Velocidad de paquete en animación de bus

# ──────────────────────────────────────────────────────────────────────────────
# HARDWARE SIMULADO — VALORES POR DEFECTO
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_RAM_MB: Final[int]       = 4096     # 4 GB
DEFAULT_CPU_CORES: Final[int]    = 4
DEFAULT_CPU_FREQ_MHZ: Final[int] = 3600
DEFAULT_CACHE_L1_KB: Final[int]  = 256
DEFAULT_CACHE_L2_KB: Final[int]  = 1024
DEFAULT_CACHE_L3_MB: Final[int]  = 8
CPU_RESET_VECTOR: Final[str]     = "0xFFFFFFF0"  # Vector de reset x86/x64

# ──────────────────────────────────────────────────────────────────────────────
# CRIPTOGRAFÍA (Secure Boot)
# ──────────────────────────────────────────────────────────────────────────────
HASH_ALGORITHM: Final[str]       = "sha256"
RSA_KEY_BITS: Final[int]         = 2048
SECURE_BOOT_ON_DEFAULT: Final[bool] = True

# ──────────────────────────────────────────────────────────────────────────────
# RUTAS DE ARCHIVOS
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR: Final[str]     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRMWARE_DIR: Final[str] = os.path.join(BASE_DIR, "data", "firmware")
KEYS_DIR: Final[str]     = os.path.join(FIRMWARE_DIR, "keys")
LOGS_DIR: Final[str]     = os.path.join(BASE_DIR, "data", "logs")
BIOS_BIN_PATH: Final[str] = os.path.join(FIRMWARE_DIR, "bios.bin")
LOG_FILE_PATH: Final[str] = os.path.join(LOGS_DIR, "boot_log.json")

# ──────────────────────────────────────────────────────────────────────────────
# PALETA DE COLORES TKINTER (tema oscuro estilo terminal)
# ──────────────────────────────────────────────────────────────────────────────
COLORS: Final[Dict[str, str]] = {
    "bg_dark":        "#0D1117",  # Fondo principal
    "bg_panel":       "#161B22",  # Fondo de paneles
    "accent_blue":    "#58A6FF",  # Resaltado azul (CPU, info)
    "accent_green":   "#3FB950",  # Verde (OK, verificado)
    "accent_red":     "#F85149",  # Rojo (error, rootkit)
    "accent_yellow":  "#D29922",  # Amarillo (advertencia)
    "accent_orange":  "#E3B341",  # Naranja (SATA, en proceso)
    "accent_purple":  "#A371F7",  # Púrpura (SMBus, crypto)
    "text_primary":   "#C9D1D9",  # Texto principal
    "text_secondary": "#8B949E",  # Texto secundario
    "border":         "#30363D",  # Bordes de paneles
}

# ──────────────────────────────────────────────────────────────────────────────
# ENUMERACIONES DEL SISTEMA — Importar desde aquí en todos los módulos
# ──────────────────────────────────────────────────────────────────────────────

class BootStage(Enum):
    """Etapas secuenciales del proceso de arranque simulado."""
    POWER_OFF          = auto()
    POWER_ON           = auto()
    CPU_RESET          = auto()
    CHIPSET_INIT       = auto()
    MEMORY_TEST        = auto()
    HARDWARE_ENUM      = auto()
    BIOS_LOAD          = auto()
    SECURE_BOOT_INIT   = auto()
    SECURE_BOOT_VERIFY = auto()
    ROOTKIT_SCAN       = auto()
    OS_HANDOFF         = auto()
    BOOT_SUCCESS       = auto()
    BOOT_FAILURE       = auto()


class SecurityStatus(Enum):
    """Estado de seguridad de un componente del sistema."""
    UNKNOWN   = "DESCONOCIDO"
    CLEAN     = "LIMPIO"
    INFECTED  = "INFECTADO"
    BLOCKED   = "BLOQUEADO"
    VERIFIED  = "VERIFICADO"
    TAMPERED  = "ADULTERADO"
    BYPASSED  = "ELUDIDO"


class POSTResult(Enum):
    """Resultado de una prueba POST individual."""
    PASS    = "OK"
    FAIL    = "FALLO"
    WARNING = "ADVERTENCIA"
    SKIP    = "OMITIDO"


class BusType(Enum):
    """Tipos de bus del sistema simulado."""
    SYSTEM_BUS = "Bus del Sistema (DMI)"
    PCI_E      = "PCIe"
    SATA       = "SATA"
    USB        = "USB"
    LPC        = "LPC (BIOS ROM)"
    SMBus      = "SMBus (SPD RAM)"


class RootkitType(Enum):
    """Tipos de rootkit simulados en el proyecto."""
    FIRMWARE   = "Rootkit de Firmware (UEFI Flash)"
    BOOTKIT    = "Bootkit (MBR Sector 0)"
    HYPERVISOR = "Hypervisor Rootkit (Blue Pill)"


# ──────────────────────────────────────────────────────────────────────────────
# DATACLASS DE CONFIGURACIÓN DE SIMULACIÓN
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SimulationConfig:
    """
    Configuración de un escenario de simulación.
    Se crea desde la UI y se pasa al POSTController.
    """
    scenario_name: str       = "Escenario por defecto"
    rootkit_enabled: bool    = False
    rootkit_type: RootkitType = RootkitType.FIRMWARE
    secure_boot_enabled: bool = True
    ram_mb: int              = DEFAULT_RAM_MB
    cpu_cores: int           = DEFAULT_CPU_CORES
    cpu_freq_mhz: int        = DEFAULT_CPU_FREQ_MHZ
    step_delay_ms: int       = STEP_DELAY_MS
    auto_run: bool           = False
