import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt6.QtCore import QCoreApplication
from core.post_engine import PostEngine


def mostrar_estado(mensaje: str, estado: str) -> None:
    print(f"[{estado}] {mensaje}")


def correr_post_normal() -> None:
    print("\n=== PRUEBA 1: Secuencia de POST normal ===\n")

    engine = PostEngine()
    engine.status_updated.connect(mostrar_estado)

    exito = engine.run_post_sequence()

    if exito:
        print("\n✅ POST completado exitosamente.")
        print(f"   CPU final -> {engine.cpu.get_state()}")
    else:
        print("\n❌ POST detenido por un error crítico.")


def correr_post_con_fallo_ram() -> None:
    print("\n=== PRUEBA 2: Secuencia de POST con fallo simulado en RAM ===\n")

    engine = PostEngine()
    engine.status_updated.connect(mostrar_estado)

    def dram_init_con_fallo() -> None:
        from core.ram import RAM
        engine._ram = RAM()
        engine._ram.simulate_failure = True
        engine._ram.verify_integrity()

    engine._run_dram_init = dram_init_con_fallo

    exito = engine.run_post_sequence()

    if exito:
        print("\n✅ POST completado exitosamente.")
    else:
        print("\n❌ POST detenido por un error crítico (esperado en esta prueba).")


def main() -> None:
    app = QCoreApplication(sys.argv)

    correr_post_normal()
    correr_post_con_fallo_ram()


if __name__ == "__main__":
    main()
