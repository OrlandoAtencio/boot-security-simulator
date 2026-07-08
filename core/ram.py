# core/ram.py
from typing import Dict, List


class RAMHardwareError(Exception):
    """Error que simula una falla física de RAM."""
    pass


class RAM:
    """Simulación de memoria RAM con bancos, lectura/escritura y verificación de integridad."""

    def __init__(self) -> None:
        self.memory: Dict[int, int] = {}
        self.simulate_failure: bool = False
        self.failed_bank: str | None = None
        self.banks: List[Dict[str, object]] = [
            {"id": "A1", "size_mb": 2048, "status": "ready"},
            {"id": "A2", "size_mb": 2048, "status": "ready"},
        ]
        self.total_size_mb: int = sum(bank["size_mb"] for bank in self.banks)
        self.total_bytes: int = self.total_size_mb * 1024 * 1024

    def _validate_address(self, address: int) -> None:
        if address < 0 or address >= self.total_bytes:
            raise RAMHardwareError(f"Dirección fuera de rango: 0x{address:X}")

    def write(self, address: int, value: int) -> None:
        self._validate_address(address)
        self.memory[address] = value

    def read(self, address: int) -> int:
        self._validate_address(address)
        return self.memory.get(address, 0)

    def load_image(self, data: bytes, base_address: int = 0) -> None:
        """Carga una imagen de bytes en la memoria simulada."""
        if base_address < 0:
            raise RAMHardwareError("Dirección base inválida para cargar imagen.")
        if base_address + len(data) > self.total_bytes:
            raise RAMHardwareError("Imagen excede la capacidad de memoria RAM.")
        for offset, byte in enumerate(data):
            self.write(base_address + offset, byte)

    def get_memory_map(self) -> List[Dict[str, object]]:
        """Retorna un mapa simple de los bancos de memoria."""
        map_list: List[Dict[str, object]] = []
        current_base = 0
        for bank in self.banks:
            size_bytes = bank["size_mb"] * 1024 * 1024
            map_list.append({
                "id": bank["id"],
                "base": hex(current_base),
                "size_mb": bank["size_mb"],
                "status": bank["status"],
            })
            current_base += size_bytes
        return map_list

    def verify_integrity(self) -> bool:
        """Ejecuta una prueba de lectura/escritura en varios bancos de memoria."""
        if self.simulate_failure:
            for bank in self.banks:
                if bank["id"] == self.failed_bank or self.failed_bank is None:
                    bank["status"] = "failed"
            raise RAMHardwareError("Fallo físico simulado en la memoria RAM.")

        test_values = {0x1000: 0xAA, 0x2000: 0x55, 0x3000: 0xFF}
        for address, test_value in test_values.items():
            self.write(address, test_value)
            if self.read(address) != test_value:
                raise RAMHardwareError("Error de integridad detectado.")

        for bank in self.banks:
            bank["status"] = "ready"
        return True
