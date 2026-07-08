import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.cpu import CPU
from core.ram import RAM
from core.bus_controller import BusController


def test_cpu_reset_initializes_expected_x86_state():
    cpu = CPU()
    state = cpu.reset()

    assert state["EIP"] == "0xffff0"
    assert state["CS"] == "0xf000"
    assert cpu.status["reset_vector"] == "0xffff0"
    assert cpu.status["vendor"] == "Intel"
    assert cpu.mode == "real"


def test_cpu_can_enter_protected_mode():
    cpu = CPU()
    cpu.reset()

    state = cpu.enter_protected_mode()

    assert cpu.mode == "protected"
    assert state["FLAGS"] == "0x1"
    assert cpu.status["mode"] == "protected"


def test_ram_integrity_check_touches_memory_banks_and_bus():
    ram = RAM()
    ram.simulate_failure = False

    assert ram.verify_integrity() is True
    assert ram.memory[0x1000] == 0xAA
    assert ram.memory[0x2000] == 0x55
    assert ram.memory[0x3000] == 0xFF
    assert ram.banks[0]["status"] == "ready"
    assert ram.total_size_mb == 4096


def test_ram_load_image_respects_capacity():
    ram = RAM()
    data = bytes([0x01, 0x02, 0x03, 0x04])
    ram.load_image(data, base_address=0x100)

    assert ram.read(0x100) == 0x01
    assert ram.read(0x103) == 0x04


def test_bus_controller_records_transactions():
    bus = BusController()
    tx = bus.transfer("CPU", "RAM", 0x1000, 0xAA, size=4, bus_type="system")

    assert tx["source"] == "CPU"
    assert tx["destination"] == "RAM"
    assert tx["address"] == 0x1000
    assert tx["status"] == "OK"
    assert tx["latency_ms"] == 2
    assert len(bus.trace) == 1


def test_bus_controller_rejects_unknown_bus():
    bus = BusController()
    tx = bus.transfer("CPU", "BIOS", 0x0, 0x0, size=4, bus_type="agp")

    assert tx["status"] == "ERROR"
    assert tx["error"] == "Bus no soportado"
    assert bus.last_status == "ERROR"
    assert len(bus.trace) == 1
