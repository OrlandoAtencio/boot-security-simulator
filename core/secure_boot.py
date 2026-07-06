# ==============================================================================
# CLASE 4 — SecureBoot
# Responsable: Backend Secure Boot
# ==============================================================================

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import SecurityStatus
import hashlib
class SecureBoot:
    """
    Implementa la verificación criptográfica del arranque (UEFI Secure Boot).

    Cadena de confianza que debe verificarse en orden:
      Platform Key (PK) → Key Exchange Key (KEK) → Base de firmas (db) → Bootloader

    Si cualquier eslabón de la cadena falla, el arranque debe ser bloqueado.
    La base de datos dbx contiene firmas revocadas que también deben verificarse.

    Librería recomendada: pip install cryptography
    """

    def __init__(self, habilitado: bool = True) -> None:
        self.habilitado = habilitado
        self.platform_key = "PK_MASTER_KEY_2026"
        self.kek = "KEK_UTP_2026"
        
        # db: Lista de firmas válidas (firmas digitales permitidas)
        self.db = ["HASH_BOOTLOADER_VALIDO_001", "HASH_WINDOWS_BOOT"]
        
        # dbx: Lista de firmas revocadas (blacklist)
        self.dbx = ["HASH_MALWARE_ROOTKIT_001"]
        
        self.estado = SecurityStatus.UNKNOWN
        
    def inicializar(self) -> bool:
        """
        Genera y carga las claves y bases de datos para la simulación.
        Debe generar: PK, KEK, db (con hash del bootloader limpio), dbx vacío.
        Retorna True si la inicialización fue exitosa.

        TODO: Implementar — Backend Secure Boot
        """
        # Para la simulación, (re)establecemos las bases de datos y el estado
        try:
            # Asegurar que exista al menos una firma válida en db
            if not self.db:
                self.db = ["HASH_BOOTLOADER_VALIDO_001", "HASH_WINDOWS_BOOT"]
            # Asegurar que dbx exista
            if not hasattr(self, "dbx"):
                self.dbx = []
            self.estado = SecurityStatus.CLEAN
            return True
        except Exception:
            self.estado = SecurityStatus.UNKNOWN
            return False

    def verificar_firmas(self, datos: bytes) -> bool:
        """
        Verifica la cadena completa de confianza sobre los datos dados.
        Sigue el orden estricto: PK → KEK → db → Bootloader → dbx.
        Retorna True si toda la cadena es válida, False si algún paso falla.

        TODO: Implementar — Backend Secure Boot
        """
        if not self.habilitado:
            # Si Secure Boot está deshabilitado, siempre permitimos continuar
            self.estado = SecurityStatus.BYPASSED
            return True

        # Calculamos el hash SHA-256 de los datos y lo comparamos
        h = hashlib.sha256()
        h.update(datos)
        digest = h.hexdigest().upper()

        # Si está en la lista revocada (dbx) -> falla
        if digest in (x.upper() for x in self.dbx):
            self.estado = SecurityStatus.BLOCKED
            print(f"[ALERTA DE SEGURIDAD] ¡Firma {digest} encontrada en dbx (Revocada)!")
            return False

        # Si está en db (lista blanca) -> ok
        if digest in (x.upper() for x in self.db):
            self.estado = SecurityStatus.VERIFIED
            return True

        # Si no está en ninguna lista -> considerar sospechoso
        self.estado = SecurityStatus.TAMPERED
        return False

    def verificar_contra_dbx(self, hash_valor: str) -> bool:
        """
        Verifica que un hash NO esté en la lista negra (dbx).
        Retorna True si está limpio (no en dbx), False si está revocado.

        TODO: Implementar — Backend Secure Boot
        """
        if hash_valor is None:
            return False

        hv = hash_valor.upper()
        if hv in (x.upper() for x in getattr(self, "dbx", [])):
            print(f"[ALERTA DE SEGURIDAD] ¡Firma {hash_valor} encontrada en dbx (Revocada)!")
            self.estado = SecurityStatus.BLOCKED
            return False

        # Si está en la db blanca, la consideramos verificada
        if hv in (x.upper() for x in getattr(self, "db", [])):
            self.estado = SecurityStatus.VERIFIED
            return True

        # No conocido — tratar como adulterado
        self.estado = SecurityStatus.TAMPERED
        return False

    def restaurar_firmware(self) -> bool:
        """
        Fase 3:
        Simula la restauración del firmware utilizando una Golden Image.
        """
    
        print("[INFO] Iniciando restauración del firmware...")
    
        # Simulación de recuperación
        self.estado = SecurityStatus.VERIFIED
    
        print("[OK] Golden Image aplicada correctamente.")
        print("[OK] Integridad del firmware restaurada.")
    
        return True

    def agregar_a_dbx(self, hash_valor: str, motivo: str) -> bool:
        """
        Agrega un hash a la lista de firmas revocadas (dbx).
        Simula la revocación de un bootloader comprometido.
        Retorna True si fue agregado exitosamente.

        TODO: Implementar — Backend Secure Boot
        """
        if not hash_valor:
            return False
        if not hasattr(self, "dbx"):
            self.dbx = []
        hv = hash_valor.upper()
        if hv in (x.upper() for x in self.dbx):
            return False
        self.dbx.append(hash_valor)
        self.estado = SecurityStatus.BLOCKED
        print(f"[SECURE_BOOT] Agregado a dbx: {hash_valor} — {motivo}")
        return True

    def obtener_estado(self) -> dict:
        """
        Retorna un diccionario con el estado actual de Secure Boot.
        Usado por la interfaz gráfica para mostrar el panel de Secure Boot.

        TODO: Implementar — Backend Secure Boot
        """
        return {
            "habilitado": bool(self.habilitado),
            "platform_key": bool(self.platform_key),
            "db_count": len(getattr(self, "db", [])),
            "dbx_count": len(getattr(self, "dbx", [])),
            "estado": self.estado.name if isinstance(self.estado, SecurityStatus) else str(self.estado),
        }
        
