# core/ram.py

from typing import Dict


class RAMHardwareError(Exception):
    """
    Error que simula una falla física de RAM.
    """
    pass


class RAM:
    """
    Simulación básica de memoria RAM.
    """

    def __init__(self) -> None:
        self.memory: Dict[int, int] = {}
        self.simulate_failure: bool = False

    def write(
        self,
        address: int,
        value: int
    ) -> None:
        self.memory[address] = value

    def read(
        self,
        address: int
    ) -> int:
        return self.memory.get(address, 0)

    def verify_integrity(self) -> bool:
        """
        Ejecuta una prueba simple de lectura/escritura.
        """

        if self.simulate_failure:
            raise RAMHardwareError(
                "Fallo físico simulado en la memoria RAM."
            )

        test_address = 0x1000
        test_value = 0xAA

        self.write(test_address, test_value)

        if self.read(test_address) != test_value:
            raise RAMHardwareError(
                "Error de integridad detectado."
            )

        return True