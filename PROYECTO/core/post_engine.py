from __future__ import annotations

from enum import Enum, auto

from PyQt6.QtCore import QObject, pyqtSignal

from core.cpu import CPU
from core.ram import RAM, RAMHardwareError


class PostStage(Enum):
    POWER_ON = auto()
    CPU_RESET_VECTOR = auto()
    CHIPSET_INIT = auto()
    DRAM_INIT = auto()


class PostEngine(QObject):

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
    )

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._cpu: CPU | None = None
        self._ram: RAM | None = None
        self._current_stage: PostStage | None = None

    @property
    def current_stage(self) -> PostStage | None:
        return self._current_stage

    @property
    def cpu(self) -> CPU | None:
        return self._cpu

    @property
    def ram(self) -> RAM | None:
        return self._ram

    def run_post_sequence(self) -> bool:
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
            except (RAMHardwareError, ValueError) as error:
                self.status_updated.emit(
                    f"[{stage.name}] Fallo crítico: {error}",
                    self.STATUS_ERROR,
                )
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
