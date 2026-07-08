# core/cpu.py
from typing import Dict


class CPU:
    """Simulación de una CPU x86 con estado de reset, microcódigo y conectividad de bus."""

    def __init__(self) -> None:
        self.eip: int = 0xFFFF0
        self.cs: int = 0xF000
        self.ip: int = 0x0000
        self.flags: int = 0x0000
        self.mode: str = "real"
        self.vendor: str = "Intel"
        self.model: str = "Core i7-12700K"
        self.microcode_version: str = "0x0024"
        self.cache: Dict[str, int] = {
            "L1_kb": 256,
            "L2_kb": 1024,
            "L3_mb": 25,
        }
        self.initialized: bool = False
        self.status: Dict[str, object] = {
            "mode": self.mode,
            "reset_vector": hex(self.eip),
            "cs": hex(self.cs),
            "bus_ready": True,
            "vendor": self.vendor,
            "microcode": self.microcode_version,
        }

    def reset(self) -> Dict[str, str]:
        """Simula el ciclo de reset de la CPU y deja el estado listo para el POST."""
        self.eip = 0xFFFF0
        self.cs = 0xF000
        self.ip = 0x0000
        self.flags = 0x0000
        self.mode = "real"
        self.initialized = True
        self.status.update({
            "mode": self.mode,
            "reset_vector": hex(self.eip),
            "cs": hex(self.cs),
            "bus_ready": True,
            "microcode": self.microcode_version,
        })
        return self.get_state()

    def enter_protected_mode(self) -> Dict[str, str]:
        """Simula el cambio de la CPU a modo protegido."""
        if self.mode != "protected":
            self.mode = "protected"
            self.flags |= 0x1
            self.status["mode"] = self.mode
            self.status["bus_ready"] = True
        return self.get_state()

    def get_microcode_info(self) -> Dict[str, str]:
        """Retorna información general de microcódigo y modelo."""
        return {
            "vendor": self.vendor,
            "model": self.model,
            "microcode": self.microcode_version,
        }

    def get_state(self) -> Dict[str, str]:
        """Retorna el estado actual de los registros."""
        return {
            "EIP": hex(self.eip),
            "CS": hex(self.cs),
            "IP": hex(self.ip),
            "FLAGS": hex(self.flags),
        }

    def update_register(self, register: str, value: int) -> None:
        """Actualiza un registro soportado."""
        register = register.upper()
        match register:
            case "EIP":
                self.eip = value
            case "CS":
                self.cs = value
            case "IP":
                self.ip = value
            case "FLAGS":
                self.flags = value
            case _:
                raise ValueError(f"Registro no soportado: {register}")
