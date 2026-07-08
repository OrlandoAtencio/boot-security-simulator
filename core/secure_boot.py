# ======================================================================
# CLASE 4 — SecureBoot
# Responsable: Backend Secure Boot
# ======================================================================

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import SecurityStatus, ROOTKIT_KNOWN_MALICIOUS_SIGNATURES
import hashlib


class SecureBoot:
    """
    Simula el motor de verificación de UEFI Secure Boot.

    Esta clase mantiene:
      - db: lista de hashes permitidos para bootloaders/cargas de arranque.
      - dbx: lista de hashes revocados/maliciosos.
      - habilitado: bandera de Secure Boot.

    El comportamiento simula un núcleo de verificación de firmas basadas en SHA-256.
    """

    DEFAULT_BOOTLOADER_PAYLOAD = b"UTP_VALID_BOOTLOADER_V1"
    DEFAULT_WINDOWS_PAYLOAD = b"WINDOWS_BOOTLOADER_V1"
    ROOTKIT_PAYLOAD = b"MALWARE_ROOTKIT_PAYLOAD_001"

    ALIAS_SIGNATURES = {
        "HASH_BOOTLOADER_VALIDO_001": DEFAULT_BOOTLOADER_PAYLOAD,
        "HASH_WINDOWS_BOOT": DEFAULT_WINDOWS_PAYLOAD,
        "HASH_ROOTKIT_MALICIOSO": ROOTKIT_PAYLOAD,
        "HASH_MALWARE_ROOTKIT_001": ROOTKIT_PAYLOAD,
    }

    def __init__(self, habilitado: bool = True) -> None:
        self.habilitado = habilitado
        self.platform_key = "PK_MASTER_KEY_2026"
        self.kek = "KEK_UTP_2026"
        self.db: list[str] = []
        self.dbx: list[str] = []
        self.estado = SecurityStatus.UNKNOWN
        self.inicializar()

    def _hash(self, datos: bytes | str) -> str:
        if isinstance(datos, str):
            datos = datos.encode("utf-8")
        return hashlib.sha256(datos).hexdigest().upper()

    def _normalize_hash(self, hash_valor: str | None) -> str:
        return hash_valor.strip().upper() if hash_valor else ""

    def _resolve_alias(self, hash_valor: str | None) -> str | bytes:
        normalized = self._normalize_hash(hash_valor)
        if normalized in self.ALIAS_SIGNATURES:
            return self.ALIAS_SIGNATURES[normalized]
        return normalized

    def inicializar(self) -> bool:
        """Inicializa db y dbx con valores de confianza y revocación."""
        try:
            self.platform_key = "PK_MASTER_KEY_2026"
            self.kek = "KEK_UTP_2026"
            self.db = [
                self._hash(self.DEFAULT_BOOTLOADER_PAYLOAD),
                self._hash(self.DEFAULT_WINDOWS_PAYLOAD),
            ]
            self.dbx = [self._hash(self.ROOTKIT_PAYLOAD)]
            self.dbx.extend(self._hash(sig) for sig in ROOTKIT_KNOWN_MALICIOUS_SIGNATURES)
            self.estado = SecurityStatus.CLEAN
            return True
        except Exception:
            self.estado = SecurityStatus.UNKNOWN
            return False

    def verificar_firmas(self, datos: bytes | str) -> bool:
        """Verifica un bootloader contra la lista blanca y la lista negra."""
        if not self.habilitado:
            self.estado = SecurityStatus.BYPASSED
            return True

        if isinstance(datos, str):
            datos = self._resolve_alias(datos)

        digest = self._hash(datos)

        if digest in (x.upper() for x in self.dbx):
            self.estado = SecurityStatus.BLOCKED
            return False

        if digest in (x.upper() for x in self.db):
            self.estado = SecurityStatus.VERIFIED
            return True

        self.estado = SecurityStatus.TAMPERED
        return False

    def verificar_contra_dbx(self, hash_valor: str | None) -> bool:
        """Verifica si un hash está revocado o pertenece a la lista blanca."""
        resolved = self._resolve_alias(hash_valor)
        if not resolved:
            return False

        if isinstance(resolved, str):
            hv = resolved
        else:
            hv = self._hash(resolved)

        if hv in (x.upper() for x in self.dbx):
            self.estado = SecurityStatus.BLOCKED
            return False

        if hv in (x.upper() for x in self.db):
            self.estado = SecurityStatus.VERIFIED
            return True

        self.estado = SecurityStatus.TAMPERED
        return False

    def agregar_a_dbx(self, hash_valor: str, motivo: str) -> bool:
        """Revoca un hash moviéndolo de db a dbx."""
        hv = self._normalize_hash(hash_valor)
        if not hv:
            return False

        self.db = [x for x in self.db if x.upper() != hv]
        if hv not in (x.upper() for x in self.dbx):
            self.dbx.append(hv)
        self.estado = SecurityStatus.BLOCKED
        return True

    def obtener_estado(self) -> dict:
        return {
            "habilitado": bool(self.habilitado),
            "platform_key": bool(self.platform_key),
            "kek": bool(self.kek),
            "db_count": len(self.db),
            "dbx_count": len(self.dbx),
            "estado": self.estado.name if isinstance(self.estado, SecurityStatus) else str(self.estado),
        }
