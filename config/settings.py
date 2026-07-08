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


from typing import List
 
# Punto de memoria donde el BIOS se carga (simulado)
ROOTKIT_BIOS_LOAD_ADDRESS: Final[str] = "0xFFFFC000"
 
# Sección de firmware atacada por defecto
ROOTKIT_TARGET_SECTION: Final[str] = "BIOS_BOOT_SECTOR"
 
# Tamaño típico de un bootkit
ROOTKIT_BOOTKIT_SIZE_BYTES: Final[int] = 4096  # 4 KB
 
# Tamaño máximo de payload que puede inyectarse
ROOTKIT_MAX_PAYLOAD_KB: Final[int] = 4
 
# Tamaño total del SPI Flash simulado (EEPROM)
ROOTKIT_SPI_FLASH_SIZE_KB: Final[int] = 8192  # 8 MB típico
 
# Nivel de persistencia por defecto (1 = mínimo, 5 = máximo)
ROOTKIT_DEFAULT_PERSISTENCE_LEVEL: Final[int] = 3
 
# Tiempo que lleva inyectar el rootkit (en milisegundos)
ROOTKIT_INJECTION_TIME_MS: Final[int] = 200
 
# Técnicas de evasión que el rootkit puede usar
ROOTKIT_EVASION_TECHNIQUES: Final[List[str]] = [
    "CodeCaveInjection",      # Inyecta en espacios de código sin usar
    "HookInterception",       # Intercepta llamadas del sistema
    "MemoryPaging",          # Se oculta en páginas de memoria
    "SMM_Abuse",             # Abusa de System Management Mode
    "VirtualMemoryHide",     # Se oculta en memoria virtual
    "SPI_FlashSwap"          # Intercambia contenido en SPI Flash
]
 
# Firmas maliciosas conocidas (DBX - Denied Boot eXecute)
# Lista de firmas SHA-256 que están "revocadas" y son maliciosas conocidas
ROOTKIT_KNOWN_MALICIOUS_SIGNATURES: Final[List[str]] = [
    # Bootkit conocidos
    "rootkit_fw_bootkit_ghosts_2024_v1",
    "rootkit_firmware_enterprise_pro",
    "bootsector_virus_persistent_x86",
    
    # Rootkit de firmware
    "rootkit_uefi_flash_exploiter",
    "rootkit_efi_system_partition",
    "firmware_backdoor_spi_access",
    
    # Hypervisor rootkits
    "hypervisor_bluepill_rootkit_v3",
    "hypervisor_red_pill_simulator",
    "vmm_hidden_boot_injector",
    
    # Otros malware
    "malware_spi_flasher_enterprise",
    "bios_implant_trojan_advanced",
    "smm_code_injector_persistent"
]
 
# Firmas autorizadas (DB - Database)
# Firmas legítimas que el POST engine confía durante Secure Boot
ROOTKIT_TRUSTED_BOOT_SIGNATURES: Final[List[str]] = [
    # BIOS/UEFI oficiales
    "amibios_plus_v22_official_signed",
    "insyde_h2o_certified_enterprise",
    "ami_aptio_v5_signed_production",
    "phoenix_uefi_pro_authorized",
    
    # Kernels y bootloaders legítimos
    "linux_kernel_official_signature",
    "windows_bootmgr_authorized",
    "grub_bootloader_official_efi",
    "coreboot_official_build_signed",
    
    # OEM específicos
    "dell_system_firmware_2024",
    "hp_proliant_bios_authorized",
    "lenovo_thinkpad_firmware_v1",
    "supermicro_ipmi_bios_signed"
]
 
# Etapas del boot donde el rootkit intenta inyectarse
# Mapea etapa de boot a puntos de inyección posibles
ROOTKIT_INJECTION_POINTS: Final[Dict[str, List[str]]] = {
    "BIOS_LOAD": [
        "SPI_FLASH_READ",
        "MEMORY_COPY",
        "DMA_ATTACK"
    ],
    "SECURE_BOOT_INIT": [
        "VARIABLE_MODIFICATION",
        "POLICY_BYPASS",
        "FLAG_RESET"
    ],
    "SECURE_BOOT_VERIFY": [
        "SIGNATURE_SWAP",
        "DBX_INJECTION",
        "SIGNATURE_FORGERY",
        "HASH_COLLISION"
    ],
    "ROOTKIT_SCAN": [
        "PATTERN_EVASION",
        "MEMORY_HIDING",
        "HOOK_REDIRECTION"
    ]
}
 
# Probabilidades de éxito del rootkit contra diferentes defensas
ROOTKIT_ATTACK_SUCCESS_RATES: Final[Dict[str, float]] = {
    "against_no_defense": 0.95,          # Sin Secure Boot: 95%
    "against_secure_boot": 0.15,         # Con Secure Boot: 15%
    "against_secure_boot_plus_dbt": 0.05, # Con Secure Boot + DBT: 5%
    "signature_forgery_success": 0.35,   # Forja de firma: 35%
    "spi_access_bypass": 0.40            # Elusión de protección SPI: 40%
}
 
# Puntuaciones de detectabilidad de técnicas de evasión
ROOTKIT_EVASION_DETECTION_SCORES: Final[Dict[str, float]] = {
    # Puntuación de 0.0 a 1.0 (0 = difícil de detectar, 1 = fácil de detectar)
    "CodeCaveInjection": 0.25,           # Difícil de detectar
    "HookInterception": 0.40,            # Moderadamente difícil
    "MemoryPaging": 0.35,                # Difícil
    "SMM_Abuse": 0.15,                   # Muy difícil de detectar
    "VirtualMemoryHide": 0.30,           # Difícil
    "SPI_FlashSwap": 0.70                # Relativamente fácil (afecta integridad)
}
 
# Impacto en el sistema de diferentes tipos de rootkit
ROOTKIT_IMPACT_LEVELS: Final[Dict[str, Dict]] = {
    "FIRMWARE": {
        "persistence": "PERMANENTE",
        "privilege": "MÁXIMO",
        "impact": "CRÍTICO",
        "removal_difficulty": "MUY_DIFÍCIL"
    },
    "BOOTKIT": {
        "persistence": "PERSISTENTE",
        "privilege": "ALTO",
        "impact": "CRÍTICO",
        "removal_difficulty": "DIFÍCIL"
    },
    "HYPERVISOR": {
        "persistence": "TEMPORAL",
        "privilege": "MÁXIMO",
        "impact": "CRÍTICO",
        "removal_difficulty": "EXTREMADAMENTE_DIFÍCIL"
    }
}
 
# Indicadores de compromiso (IOCs) para detectar rootkits
ROOTKIT_COMPROMISE_INDICATORS: Final[List[str]] = [
    "SPI_FLASH_DIRECT_ACCESS",           # Acceso directo a SPI Flash detectado
    "FIRMWARE_SIGNATURE_MISMATCH",       # Firma de firmware no coincide
    "SECURE_BOOT_DISABLED_UNEXPECTEDLY", # Secure Boot deshabilitado
    "UNKNOWN_CODE_IN_FIRMWARE",          # Código desconocido en firmware
    "DBX_SIGNATURE_DETECTED",            # Firma revocada encontrada
    "HASH_INTEGRITY_VIOLATION",          # Integridad de hash violada
    "UNAUTHORIZED_SMM_ACCESS",           # Acceso no autorizado a SMM
    "PCI_EXPANSION_ROM_INFECTION",       # ROM de expansión comprometida
    "BOOTLOADER_MODIFICATION",           # Bootloader modificado
    "MEMORY_MAPPING_ANOMALY"             # Anomalía en mapeo de memoria
]
 
# Configuración de simulación: ¿Qué tan realista es el rootkit?
ROOTKIT_REALISM_LEVEL: Final[int] = 3  # 1 = Básico, 5 = Altamente realista
 
# Si True, el rootkit puede intentar múltiples vectores de ataque
ROOTKIT_MULTI_VECTOR_ATTACKS: Final[bool] = True
 
# Si True, el rootkit intenta ocultarse después de inyección
ROOTKIT_STEALTH_MODE: Final[bool] = True
 
# Verbosidad de logs del rootkit (0 = silencioso, 3 = muy detallado)
ROOTKIT_LOG_VERBOSITY: Final[int] = 2
 
# Ruta donde se guardan logs de ataque del rootkit
ROOTKIT_ATTACK_LOG_PATH: Final[str] = os.path.join(LOGS_DIR, "rootkit_attacks.json")
 
# Ruta donde se guardan reportes forenses
ROOTKIT_FORENSIC_REPORT_PATH: Final[str] = os.path.join(LOGS_DIR, "forensic_report.txt")

@dataclass
class SimulationConfig:
    scenario_name: str = "Escenario por defecto"
    
    # Configuración de Secure Boot
    secure_boot_enabled: bool = True
    
    # Configuración de Rootkit (NUEVAS - Fase 4)
    rootkit_enabled: bool    = False
    rootkit_type: RootkitType = RootkitType.FIRMWARE
    rootkit_persistence_level: int = ROOTKIT_DEFAULT_PERSISTENCE_LEVEL
    rootkit_evasion_technique: str = "CodeCaveInjection"
    rootkit_stealth_mode: bool = ROOTKIT_STEALTH_MODE
    
    # Hardware
    ram_mb: int              = DEFAULT_RAM_MB
    cpu_cores: int           = DEFAULT_CPU_CORES
    cpu_freq_mhz: int        = DEFAULT_CPU_FREQ_MHZ
    
    # Timing
    step_delay_ms: int       = STEP_DELAY_MS
    auto_run: bool           = False
    
    # Logging y debug
    verbose_logs: bool = False
    capture_forensics: bool = True
 
# ──────────────────────────────────────────────────────────────────────────────
# COLORES ADICIONALES PARA ROOTKIT EN INTERFAZ
# ──────────────────────────────────────────────────────────────────────────────
 
# Agregar a COLORS:
COLORS_ROOTKIT_ADDITIONS = {
    "rootkit_injecting":    "#D29922",  # Naranja: En progreso
    "rootkit_active":       "#F85149",  # Rojo: Activo/Peligroso
    "rootkit_detected":     "#3FB950",  # Verde: Detectado/Bloqueado
    "rootkit_evasion":      "#F85149",  # Rojo: Evasión activa
    "threat_critical":      "#F85149",  # Rojo: Amenaza crítica
    "forensic_evidence":    "#A371F7",  # Púrpura: Evidencia forense
}
 
# Actualizar COLORS dict:
# COLORS.update(COLORS_ROOTKIT_ADDITIONS)
 
# ──────────────────────────────────────────────────────────────────────────────
# NUEVAS ENUMERACIONES
# ──────────────────────────────────────────────────────────────────────────────
 
# Ya están definidas en el archivo principal:
# - RootkitType (FIRMWARE, BOOTKIT, HYPERVISOR)
# Pero puedes extenderlas si necesitas:
 
class RootkitBehavior(Enum):
    PASSIVE           = "Rootkit pasivo (solo escucha)"
    ACTIVE_MONITORING = "Monitoreo activo (registra actividad)"
    DATA_EXFILTRATION = "Exfiltración de datos"
    LATERAL_MOVEMENT  = "Movimiento lateral en la red"
    PERSISTENCE       = "Establecimiento de persistencia"
    EVASION          = "Técnicas de evasión"
    DESTRUCTION      = "Destrucción de evidencia"
 
 
class RootkitThreatLevel(Enum):
    LOW       = "BAJO (Educativo)"
    MEDIUM    = "MEDIO (Realista)"
    HIGH      = "ALTO (Avanzado)"
    CRITICAL  = "CRÍTICO (Máxima Sofisticación)"
 
 
# ──────────────────────────────────────────────────────────────────────────────
# DOCUMENTACIÓN DE INTEGRACIÓN
# ──────────────────────────────────────────────────────────────────────────────
from typing import List, Dict
   

ROOTKIT_BIOS_LOAD_ADDRESS = "0xFFFFC000"
ROOTKIT_TARGET_SECTION = "BIOS_BOOT_SECTOR"
 
COLORS.update({
       "rootkit_injecting": "#D29922",
       "rootkit_active": "#F85149",
        "rootkit_detected": "#3FB950",
})
 
rootkit_enabled: bool = False
rootkit_persistence_level: int = ROOTKIT_DEFAULT_PERSISTENCE_LEVEL
 
class RootkitBehavior(Enum):
    PASSIVE           = "Rootkit pasivo (solo escucha)"
    ACTIVE_MONITORING = "Monitoreo activo (registra actividad)"
    DATA_EXFILTRATION = "Exfiltración de datos"
    LATERAL_MOVEMENT  = "Movimiento lateral en la red"
    PERSISTENCE       = "Establecimiento de persistencia"
    EVASION           = "Técnicas de evasión"
    DESTRUCTION       = "Destrucción de evidencia"
   
class RootkitThreatLevel(Enum):
    LOW       = "BAJO (Educativo)"
    MEDIUM    = "MEDIO (Realista)"
    HIGH      = "ALTO (Avanzado)"
    CRITICAL  = "CRÍTICO (Máxima Sofisticación)"
   
