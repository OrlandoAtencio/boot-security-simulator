from __future__ import annotations

from enum import Enum, auto

from PyQt6.QtCore import QObject, pyqtSignal

from core.cpu import CPU
from core.ram import RAM, RAMHardwareError
from core.secure_boot import SecureBoot
from core.bus_controller import BusController
from core.rootkit_module import AttackVector, FirmwareSection, RootkitModule
from core.rootkit_integration import InjectionPoint, RootkitCombatSystem


class PostStage(Enum):
    POWER_ON = auto()
    CPU_RESET_VECTOR = auto()
    CHIPSET_INIT = auto()
    DRAM_INIT = auto()
    SECURE_BOOT_VERIFY = auto()


class PostEngine(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._cpu: CPU | None = None
        self._ram: RAM | None = None
        self._secure_boot = SecureBoot()
        self._bus_controller = BusController()
        self._current_stage: PostStage | None = None
        self._system_compromised: bool = False
        self._bios_config: dict[str, object] = {}
        self._boot_order: list[str] = ["NVMe SSD", "USB Drive", "LAN / PXE"]
        self._secure_boot_mode: str = "Standard"
        self._rootkit_module = RootkitModule()
        self._combat_system = RootkitCombatSystem()
        self._firmware_map: dict[str, FirmwareSection] = {}
        self._last_combat_report: dict | None = None

    @property
    def system_compromised(self) -> bool:
        """Fuente de verdad para Fail-Closed en main.py."""
        return self._system_compromised

    @property
    def last_combat_report(self) -> dict | None:
        """Reporte del último ataque de rootkit procesado por el motor."""
        return self._last_combat_report

    def apply_bios_configuration(self, bios_config: dict) -> None:
        """Aplica la configuración del BIOS al motor POST en tiempo real."""
        self._bios_config = bios_config.copy()
        self._secure_boot.habilitado = bool(bios_config.get("secure_boot", True))
        self._secure_boot_mode = str(bios_config.get("sb_mode", "Standard"))
        self._boot_order = [
            str(bios_config.get("boot1", "NVMe SSD")),
            str(bios_config.get("boot2", "USB Drive")),
            str(bios_config.get("boot3", "LAN / PXE")),
        ]

        if self._secure_boot_mode == "Custom":
            self.status_updated.emit(
                "Modo Secure Boot: Custom. Se permiten firmas definidas manualmente.",
                self.STATUS_OK,
            )

        measured_enabled = bool(bios_config.get("measured_boot", True))
        tpm_present = bool(bios_config.get("tpm", True))

        if measured_enabled and not tpm_present:
            self.status_updated.emit(
                "Measured Boot habilitado pero TPM ausente: las PCR no podrán sellarse correctamente.",
                self.STATUS_WARN,
            )
        elif measured_enabled:
            self.status_updated.emit(
                "Measured Boot habilitado: PCRs preparados para registrar arranque.",
                self.STATUS_OK,
            )
        else:
            self.status_updated.emit(
                "Measured Boot deshabilitado: las mediciones de arranque no se registrarán.",
                self.STATUS_WARN,
            )

        if not tpm_present:
            self.status_updated.emit(
                "TPM deshabilitado en BIOS: la cadena de confianza hardware se degrada.",
                self.STATUS_WARN,
            )

        if bios_config.get("wake_on_lan", False):
            self.status_updated.emit(
                "Wake on LAN habilitado en BIOS: el adaptador puede iniciar el sistema desde red.",
                self.STATUS_OK,
            )

        acpi_state = bios_config.get("acpi_state", "S3 (Suspend)")
        if acpi_state != "S3 (Suspend)":
            self.status_updated.emit(
                f"ACPI configurado como {acpi_state}. Esto puede cambiar cómo se reanuda el hardware.",
                self.STATUS_WARN,
            )

    # Agrega este nuevo método al final de la clase:
    def _run_secure_boot(self) -> None:
        # Simulamos un hash de un bootloader (puedes cambiarlo para probar el bloqueo)
        hash_prueba = "HASH_WINDOWS_BOOT" 
        
        if self._secure_boot.verificar_contra_dbx(hash_prueba):
            self.status_updated.emit("Verificación de firma exitosa. Secure Boot OK.", self.STATUS_OK)
        else:
            raise ValueError("¡Firma maliciosa detectada! El sistema se bloqueó.")
        
    status_updated = pyqtSignal(str, str)

    STATUS_OK: str = "OK"
    STATUS_WARN: str = "WARN"
    STATUS_ERROR: str = "ERROR"

    RESET_EIP: int = 0xFFFF0
    RESET_CS: int = 0xF000

    _STAGE_SEQUENCE: tuple[PostStage, ...] = (
        PostStage.POWER_ON,
        PostStage.CPU_RESET_VECTOR,
        PostStage.CHIPSET_INIT,
        PostStage.DRAM_INIT,
        PostStage.SECURE_BOOT_VERIFY,
    )

    @property
    def current_stage(self) -> PostStage | None:
        return self._current_stage

    @property
    def bios_config(self) -> dict[str, object]:
        return self._bios_config.copy()

    @property
    def boot_order(self) -> tuple[str, str, str]:
        return tuple(self._boot_order)

    @property
    def secure_boot_mode(self) -> str:
        return self._secure_boot_mode

    @property
    def cpu(self) -> CPU | None:
        return self._cpu

    @property
    def ram(self) -> RAM | None:
        return self._ram

    def run_post_sequence(
        self,
        inject_rootkit: bool = False,
        attack_vector: AttackVector | None = None
    ) -> bool:
        """
        inject_rootkit: simula la acción del botón de inyección de rootkit.
        attack_vector: permite seleccionar el vector de ataque usado por el rootkit.
        Inicia el flujo de ataque/defensa con el sistema de Rootkit.
        """
        self._system_compromised = False
        self._rootkit_module = RootkitModule()
        self._firmware_map = self._build_firmware_map()
        self._ensure_secure_boot_defense_lists()
        self._last_combat_report = None

        if inject_rootkit:
            self._rootkit_module.attack_vector = (
                attack_vector if attack_vector is not None else AttackVector.FIRMWARE_FLASH
            )
            self._rootkit_module.persistence_level = int(self._bios_config.get("rootkit_persistence_level", 3))
            self._rootkit_module._initialize_payload()

        for stage in self._STAGE_SEQUENCE:
            self._current_stage = stage
            try:
                match stage:
                    case PostStage.POWER_ON:
                        self._run_power_on()
                    case PostStage.CPU_RESET_VECTOR:
                        self._run_cpu_reset_vector()
                    case PostStage.CHIPSET_INIT:
                        self._run_chipset_init()
                    case PostStage.DRAM_INIT:
                        self._run_dram_init()
                    case PostStage.SECURE_BOOT_VERIFY:
                        self._run_secure_boot_verify(inject_rootkit=inject_rootkit)
            except (RAMHardwareError, ValueError) as error:
                self.status_updated.emit(
                    f"[{stage.name}] Fallo crítico: {error}",
                    self.STATUS_ERROR,
                )
                if stage == PostStage.SECURE_BOOT_VERIFY:
                    self._system_compromised = True
                return False

        return True

    def _run_power_on(self) -> None:
        self.status_updated.emit(
            "Alimentación eléctrica estable. Iniciando secuencia de arranque.",
            self.STATUS_OK,
        )

    def _run_cpu_reset_vector(self) -> None:
        self._cpu = CPU()
        self._cpu.reset()
        self._bus_controller.transfer("CPU", "BIOS", 0xFFFF0, 0xF000, size=4, bus_type="system")
        estado = self._cpu.get_state()

        eip_actual = int(estado["EIP"], 16)
        cs_actual = int(estado["CS"], 16)

        if eip_actual != self.RESET_EIP or cs_actual != self.RESET_CS:
            raise ValueError(
                "La CPU no inicializó en el vector de reset esperado "
                f"(EIP={estado['EIP']}, CS={estado['CS']})."
            )

        self.status_updated.emit(
            f"CPU inicializada correctamente en EIP={estado['EIP']}, "
            f"CS={estado['CS']}.",
            self.STATUS_OK,
        )

    def _run_chipset_init(self) -> None:
        self._bus_controller.transfer("PCH", "CPU", 0x0, 0x0, size=8, bus_type="system")
        self.status_updated.emit(
            "Chipset inicializado. Buses de comunicación habilitados (DMI/PCIe).",
            self.STATUS_OK,
        )

    def _run_dram_init(self) -> None:
        self._ram = RAM()
        self._ram.verify_integrity()
        self._bus_controller.transfer("CPU", "RAM", 0x1000, 0xAA, size=4, bus_type="system")

        self.status_updated.emit(
            "Memoria RAM verificada. Todos los bancos respondieron correctamente en el bus del sistema.",
            self.STATUS_OK,
        )

    def _build_firmware_map(self) -> dict[str, FirmwareSection]:
        """Construye un mapa simulado de secciones de firmware para el ataque."""
        default_section = FirmwareSection(
            name="BIOS_BOOT_SECTOR",
            base_address="0x00080000",
            size_kb=64,
            content_hash=self._secure_boot._hash(self._secure_boot.DEFAULT_WINDOWS_PAYLOAD),
            is_signed=True,
            signature=self._secure_boot._hash(self._secure_boot.DEFAULT_WINDOWS_PAYLOAD),
            original_content=self._secure_boot.DEFAULT_WINDOWS_PAYLOAD,
            current_content=self._secure_boot.DEFAULT_WINDOWS_PAYLOAD,
            tampered=False,
        )
        return {default_section.name: default_section}

    def _ensure_secure_boot_defense_lists(self) -> None:
        """Sincroniza las listas DB y DBX del sistema de combate con el motor de Secure Boot."""
        self._combat_system.secure_boot_defense.trusted_signatures = list(self._secure_boot.db)
        self._combat_system.secure_boot_defense.revoked_signatures = list(self._secure_boot.dbx)

    def _run_secure_boot_verify(self, inject_rootkit: bool = False) -> None:
        boot_device = self._bios_config.get("boot1", "NVMe SSD")
        if boot_device != "NVMe SSD":
            self.status_updated.emit(
                f"Arranque primario seleccionado desde {boot_device}.",
                self.STATUS_OK,
            )

        if not self._secure_boot.habilitado:
            self.status_updated.emit(
                "Secure Boot deshabilitado en BIOS. Omisión de verificación de firma.",
                self.STATUS_WARN,
            )
            return

        if not self._bios_config.get("tpm", True):
            self.status_updated.emit(
                "TPM ausente: la integridad de la cadena de confianza se reduce.",
                self.STATUS_WARN,
            )

        if self._bios_config.get("measured_boot", True):
            self.status_updated.emit(
                "Measured Boot activo: PCRs de arranque se evaluarán.",
                self.STATUS_OK,
            )
        else:
            self.status_updated.emit(
                "Measured Boot deshabilitado: no se verificarán PCRs.",
                self.STATUS_WARN,
            )

        if self._secure_boot_mode == "Custom":
            self.status_updated.emit(
                "Secure Boot Custom: validación con parámetros definidos por BIOS.",
                self.STATUS_OK,
            )

        if boot_device == "LAN / PXE" and not self._bios_config.get("wake_on_lan", False):
            self.status_updated.emit(
                "Boot desde LAN configurado sin Wake on LAN — la red puede no despertar el sistema.",
                self.STATUS_WARN,
            )

        self.status_updated.emit(
            "Iniciando verificación de integridad de firma (Secure Boot)...",
            self.STATUS_OK,
        )

        if inject_rootkit:
            combat_report = self._combat_system.process_boot_with_threat(
                self._rootkit_module,
                self._firmware_map,
                InjectionPoint.SECURE_BOOT_VERIFY,
            )
            self._last_combat_report = combat_report

            if not combat_report['boot_success']:
                self.status_updated.emit(
                    "¡Rootkit detectado y bloqueado durante Secure Boot!",
                    self.STATUS_ERROR,
                )
                raise ValueError("¡Ataque de rootkit bloqueado! Sistema detenido.")

            self.status_updated.emit(
                "Secure Boot completado: no se detectaron amenazas en firmware.",
                self.STATUS_OK,
            )
            return

        # Sin rootkit inyectado, verificamos el payload legítimo.
        if self._secure_boot.verificar_contra_dbx("HASH_WINDOWS_BOOT"):
            self.status_updated.emit("Verificación de firma exitosa. Secure Boot OK.", self.STATUS_OK)
        else:
            raise ValueError("¡Firma maliciosa detectada! El sistema se bloqueó por seguridad.")

    def reset_security_state(self) -> None:
        """Handshake de mitigación: limpia el estado tras la limpieza de Andrée."""
        self._system_compromised = False
        self.status_updated.emit(
            "Firmas maliciosas removidas. Estado de seguridad reiniciado.",
            self.STATUS_OK,
        )
