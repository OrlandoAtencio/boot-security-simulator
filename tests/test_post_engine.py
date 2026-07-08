import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.post_engine import PostEngine
from core.secure_boot import SecureBoot


def test_post_engine_clean_boot():
    engine = PostEngine()
    engine.apply_bios_configuration({
        "secure_boot": True,
        "sb_mode": "Standard",
        "boot1": "NVMe SSD",
        "boot2": "USB Drive",
        "boot3": "LAN / PXE",
        "tpm": True,
        "measured_boot": True,
        "wake_on_lan": False,
        "acpi_state": "S3 (Suspend)",
    })

    resultado = engine.run_post_sequence(inject_rootkit=False)

    assert resultado is True
    assert engine.system_compromised is False
    assert engine.cpu is not None
    assert engine.ram is not None
    assert engine.boot_order[0] == "NVMe SSD"


def test_post_engine_detects_rootkit_when_injected(monkeypatch):
    engine = PostEngine()
    engine.apply_bios_configuration({
        "secure_boot": True,
        "sb_mode": "Standard",
        "boot1": "NVMe SSD",
        "boot2": "USB Drive",
        "boot3": "LAN / PXE",
        "tpm": True,
        "measured_boot": True,
        "wake_on_lan": False,
        "acpi_state": "S3 (Suspend)",
    })

    # Fuerza la inyección para que el ataque pase al análisis de Secure Boot.
    monkeypatch.setattr("core.rootkit_module.random.random", lambda: 0.0)

    resultado = engine.run_post_sequence(inject_rootkit=True)

    assert resultado is False
    assert engine.system_compromised is True
    assert engine.current_stage.name == "SECURE_BOOT_VERIFY"


def test_secure_boot_known_hashes():
    sb = SecureBoot()
    assert sb.verificar_contra_dbx("HASH_WINDOWS_BOOT") is True
    assert sb.verificar_contra_dbx("HASH_MALWARE_ROOTKIT_001") is False
    assert sb.estado.name in {"VERIFIED", "BLOCKED"}
