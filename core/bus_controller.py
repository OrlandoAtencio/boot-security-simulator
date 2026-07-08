from __future__ import annotations

from typing import Dict, List


class BusController:
    """Simula de forma básica el tráfico entre CPU, RAM, BIOS y buses del sistema."""

    SUPPORTED_BUS_TYPES = {"system", "pci", "sata", "usb", "lpc"}
    LATENCY_MS = {
        "system": 2,
        "pci": 4,
        "sata": 8,
        "usb": 12,
        "lpc": 3,
    }

    def __init__(self) -> None:
        self.trace: List[Dict[str, object]] = []
        self.last_status: str = "OK"

    def transfer(self, source: str, destination: str, address: int, value: int, size: int = 4, bus_type: str = "system") -> Dict[str, object]:
        if bus_type not in self.SUPPORTED_BUS_TYPES:
            transaction = {
                "source": source,
                "destination": destination,
                "address": address,
                "value": value,
                "size": size,
                "bus_type": bus_type,
                "status": "ERROR",
                "latency_ms": 0,
                "error": "Bus no soportado",
            }
            self.last_status = "ERROR"
            self.trace.append(transaction)
            return transaction

        latency = self.LATENCY_MS.get(bus_type, 5)
        transaction = {
            "source": source,
            "destination": destination,
            "address": address,
            "value": value,
            "size": size,
            "bus_type": bus_type,
            "latency_ms": latency,
            "status": "OK",
        }
        self.last_status = "OK"
        self.trace.append(transaction)
        return transaction

    def reset(self) -> None:
        """Limpia el historial de transacciones del controlador de buses."""
        self.trace.clear()
        self.last_status = "OK"
