from __future__ import annotations

from enum import Enum, auto

from PyQt6.QtCore import QObject, pyqtSignal

from core.cpu import CPU
from core.ram import RAM, RAMHardwareError
from core.secure_boot import SecureBoot


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
        self._secure_boot = SecureBoot() # <--- Instancia de tu clase
        self._current_stage: PostStage | None = None
        self._system_compromised: bool = False  # <-- NUEVO

    @property
    def system_compromised(self) -> bool:
        """Fuente de verdad para Fail-Closed en main.py."""
        return self._system_compromised

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
    def cpu(self) -> CPU | None:
        return self._cpu

    @property
    def ram(self) -> RAM | None:
        return self._ram

    def run_post_sequence(self, force_rootkit: bool = False) -> bool:
        """
        force_rootkit: viene del botón 'Inyectar Rootkit' de la UI.
        Permite que la verificación real de Secure Boot reaccione
        al mismo estado que ve el usuario en pantalla.
        """
        self._system_compromised = False
        self._force_rootkit = force_rootkit  # usado por _run_secure_boot_verify

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
                        self._run_secure_boot_verify()
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
        self.status_updated.emit(
            "Chipset inicializado. Buses de comunicación habilitados.",
            self.STATUS_OK,
        )

    def _run_dram_init(self) -> None:
        self._ram = RAM()
        self._ram.verify_integrity()

        self.status_updated.emit(
            "Memoria RAM verificada. Todos los bancos respondieron correctamente.",
            self.STATUS_OK,
        )

    def _run_secure_boot_verify(self) -> None:
        # Si el usuario activó "Inyectar Rootkit", forzamos un hash malicioso.
        # Si no, usamos el hash legítimo de siempre.
        hash_prueba = "HASH_ROOTKIT_MALICIOSO" if self._force_rootkit else "HASH_WINDOWS_BOOT"

        self.status_updated.emit(
            "Iniciando verificación de integridad de firma (Secure Boot)...",
            self.STATUS_OK,
        )

        if self._secure_boot.verificar_contra_dbx(hash_prueba):
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
