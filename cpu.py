# core/cpu.py

from typing import Dict


class CPU:
    """
    Simulación básica de una CPU x86 durante el arranque.
    """

    def __init__(self) -> None:
        self.eip: int = 0xFFFF0
        self.cs: int = 0xF000

    def get_state(self) -> Dict[str, str]:
        """
        Retorna el estado actual de los registros.
        """
        return {
            "EIP": hex(self.eip),
            "CS": hex(self.cs)
        }

    def update_register(
        self,
        register: str,
        value: int
    ) -> None:
        """
        Actualiza el valor de un registro.
        """

        register = register.upper()

        match register:
            case "EIP":
                self.eip = value

            case "CS":
                self.cs = value

            case _:
                raise ValueError(
                    f"Registro no soportado: {register}"
                )