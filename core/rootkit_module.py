"""
core/rootkit_module.py — Módulo de Rootkit para Fase 4
========================================================
Emula un malware de persistencia avanzada en firmware que intenta sobrescribir
el sector de arranque virtualizado (SPI Flash simulada) durante el boot.

Responsable: Michael (Fase 4)
Objetivo: Atacar las defensas criptográficas implementadas por el backend,
          específicamente la verificación de firmas SHA-256 en Secure Boot.

ARQUITECTURA DEL ATAQUE:
1. Inyección: Se activa desde el botón GUI en momento específico del boot
2. Persistencia: Modifica el almacenamiento virtual de BIOS
3. Evasión: Intenta inyectar firma revocada (dbx) en el sector de arranque
4. Detección: El POST engine debe detectar la manipulación en SECURE_BOOT_VERIFY
"""

from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Tuple, List
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────────────
# ENUMERACIONES DEL ROOTKIT
# ──────────────────────────────────────────────────────────────────────────────

class RootkitStage(Enum):
    """Etapas de progresión del ataque del Rootkit."""
    DORMANT         = "INACTIVO"           # Sin infectar
    INJECTED        = "INYECTADO"          # Payload cargado en memoria
    SPI_ACCESS      = "ACCESO_SPI"         # Obtuvo acceso a SPI Flash
    SIGNATURE_SWAP  = "CAMBIO_FIRMA"       # Intercambió firma autorizada
    PERSISTENCE     = "PERSISTENCIA"       # Se volvió persistente en firmware
    DETECTED        = "DETECTADO"          # Descubierto por POST engine
    BLOCKED         = "BLOQUEADO"          # Neutralizado por Secure Boot


class AttackVector(Enum):
    """Vectores de ataque específicos del Rootkit."""
    FIRMWARE_FLASH  = "Escritura directa en SPI Flash"
    SECTOR_0_MBR    = "Sobrescritura del MBR (Sector 0)"
    SIGNATURE_FORGE = "Forja de firma SHA-256"
    DBX_INJECTION   = "Inyección de firma revocada (DBX)"
    INTEGRITY_BYPASS = "Elusión de verificación de integridad"


class RootkitStatus(Enum):
    """Estados de salud del Rootkit."""
    HEALTHY         = "ACTIVO"
    WEAKENED        = "DEBILITADO"
    COMPROMISED     = "COMPROMETIDO"
    NEUTRALIZED     = "NEUTRALIZADO"


# ──────────────────────────────────────────────────────────────────────────────
# ESTRUCTURAS DE DATOS
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class FirmwareSection:
    """Representa una sección del almacenamiento virtual de firmware."""
    name: str                           # Nombre de la sección (ej: "BIOS_CODE")
    base_address: str                   # Dirección base (ej: "0xFFFC0000")
    size_kb: int                        # Tamaño en KB
    content_hash: str                   # SHA-256 del contenido original
    is_signed: bool                     # ¿Está firmado por autoridad?
    signature: Optional[str] = None     # Firma digital (RSA-2048)
    original_content: bytes = field(default_factory=bytes)  # Respaldo original
    current_content: bytes = field(default_factory=bytes)   # Contenido modificado
    tampered: bool = False              # ¿Fue modificado?


@dataclass
class RootkitPayload:
    """Estructura del payload malicioso del Rootkit."""
    rootkit_id: str                     # ID único (ej: "ROOT_FW_2024")
    creation_date: datetime             # Fecha de creación
    attack_vector: AttackVector         # Vector de ataque
    malicious_signature: str            # Firma falsa del rootkit
    target_section: str                 # Sección a atacar (ej: "BIOS_BOOT")
    injection_size_bytes: int           # Tamaño del código inyectado
    evasion_technique: str              # Técnica de evasión (ej: "CodeCave")
    persistence_level: int              # Nivel de persistencia (1-5, siendo 5 máximo)
    detection_score: float = 0.0        # Puntuación de detectabilidad (0.0-1.0)


@dataclass
class AttackLog:
    """Registro de eventos del ataque del Rootkit."""
    timestamp: datetime
    stage: RootkitStage
    event: str
    success: bool
    details: Dict
    forensic_evidence: List[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# CLASE PRINCIPAL: ROOTKIT
# ──────────────────────────────────────────────────────────────────────────────

class RootkitModule:
    """
    Emula un Rootkit avanzado que ataca el sector de arranque durante el boot.
    Coordina inyección, persistencia y evasión de defensas criptográficas.
    
    INTERFAZ PÚBLICA:
        - inject() → Inyecta el payload en el almacenamiento virtual
        - execute_attack() → Ejecuta el ataque completo
        - get_status() → Retorna estado actual del rootkit
        - get_attack_logs() → Retorna historial forense del ataque
    """
    
    def __init__(
        self,
        rootkit_id: str = "ROOT_FW_2024_PHASE4",
        attack_vector: AttackVector = AttackVector.FIRMWARE_FLASH,
        persistence_level: int = 5
    ):
        """Inicializa el módulo del Rootkit."""
        self.rootkit_id = rootkit_id
        self.attack_vector = attack_vector
        self.persistence_level = persistence_level
        
        # Estado interno
        self.current_stage: RootkitStage = RootkitStage.DORMANT
        self.status: RootkitStatus = RootkitStatus.HEALTHY
        self.is_active: bool = False
        self.is_detected: bool = False
        self.is_blocked: bool = False
        
        # Payload y firmware
        self.payload: Optional[RootkitPayload] = None
        self.firmware_sections: Dict[str, FirmwareSection] = {}
        self.attack_logs: List[AttackLog] = []
        
        # Métricas de ataque
        self.injection_time_ms: float = 0.0
        self.spi_access_attempts: int = 0
        self.signature_forge_success: bool = False
        self.dbx_injection_success: bool = False
        
        # Generar payload por defecto
        self._initialize_payload()
    
    
    def _initialize_payload(self) -> None:
        """Inicializa el payload malicioso del Rootkit."""
        self.payload = RootkitPayload(
            rootkit_id=self.rootkit_id,
            creation_date=datetime.now(),
            attack_vector=self.attack_vector,
            malicious_signature=self._generate_malicious_signature(),
            target_section="BIOS_BOOT_SECTOR",
            injection_size_bytes=4096,  # Tamaño típico de bootkit
            evasion_technique="CodeCaveInjection",
            persistence_level=self.persistence_level,
            detection_score=self._calculate_detection_score()
        )
        self._log_event(
            stage=RootkitStage.DORMANT,
            event="Payload inicializado",
            success=True,
            details={
                "payload_id": self.payload.rootkit_id,
                "vector": self.attack_vector.value,
                "evasion": self.payload.evasion_technique
            }
        )
    
    
    def inject(self, firmware_map: Dict[str, FirmwareSection]) -> bool:
        """
        Inyecta el rootkit en el almacenamiento virtual de firmware (SPI Flash).
        
        PASOS:
        1. Copiar map de firmware a estructura interna
        2. Intentar acceso SPI (simular lectura física)
        3. Generar firma falsa compatible con DBX
        4. Sobrescribir sector de arranque con payload
        
        Args:
            firmware_map: Dict de secciones de firmware del POST engine
            
        Returns:
            bool: True si la inyección fue exitosa, False si fue bloqueada
        """
        start_time = time.time()
        
        # Paso 1: Copiar mapa de firmware
        self.firmware_sections = firmware_map.copy()
        self._log_event(
            stage=RootkitStage.INJECTED,
            event="Mapa de firmware copiado",
            success=True,
            details={"sections_count": len(firmware_map)}
        )
        
        # Paso 2: Intentar acceso SPI Flash
        spi_access_granted = self._attempt_spi_access()
        if not spi_access_granted:
            self._log_event(
                stage=RootkitStage.SPI_ACCESS,
                event="Acceso SPI FALLIDO - Secure Boot lo bloqueó",
                success=False,
                details={"attempts": self.spi_access_attempts}
            )
            self.is_blocked = True
            self.current_stage = RootkitStage.BLOCKED
            return False
        
        self._log_event(
            stage=RootkitStage.SPI_ACCESS,
            event="Acceso SPI otorgado",
            success=True,
            details={
                "access_level": "WRITE",
                "attempts": self.spi_access_attempts,
                "memory_protection": "BYPASSED"
            }
        )
        
        # Paso 3: Inyectar firma maliciosa (DBX-compatible)
        signature_injected = self._inject_malicious_signature()
        if not signature_injected:
            self._log_event(
                stage=RootkitStage.SIGNATURE_SWAP,
                event="Inyección de firma FALLIDA",
                success=False,
                details={"reason": "Verificación de integridad detectó cambio"}
            )
            return False
        
        self._log_event(
            stage=RootkitStage.SIGNATURE_SWAP,
            event="Firma maliciosa inyectada en DBX",
            success=True,
            details={
                "forged_signature": self.payload.malicious_signature[:32] + "...",
                "replaced_signature": self.firmware_sections.get("BIOS_BOOT_SECTOR", 
                                                                   FirmwareSection("", "", 0, "", False)).signature[:32] + "..." 
                                      if self.firmware_sections.get("BIOS_BOOT_SECTOR") else "N/A"
            }
        )
        
        # Paso 4: Establecer persistencia
        persistence_set = self._establish_persistence()
        if persistence_set:
            self.current_stage = RootkitStage.PERSISTENCE
            self.is_active = True
            self.signature_forge_success = True
            self.dbx_injection_success = True
        
        injection_time_ms = (time.time() - start_time) * 1000
        self.injection_time_ms = injection_time_ms
        
        self._log_event(
            stage=RootkitStage.PERSISTENCE,
            event="Rootkit estableció persistencia en firmware",
            success=persistence_set,
            details={
                "injection_time_ms": injection_time_ms,
                "persistence_level": self.persistence_level,
                "status": "PERSISTENTE" if persistence_set else "FALLIDO"
            }
        )
        
        return persistence_set
    
    
    def execute_attack(self, firmware_map: Dict[str, FirmwareSection]) -> Dict:
        """
        Ejecuta el ciclo completo de ataque del Rootkit.
        Coordina inyección, ocultación y evasión.
        
        Returns:
            Dict con resultados del ataque: {
                'success': bool,
                'stage': RootkitStage,
                'status': RootkitStatus,
                'duration_ms': float,
                'attack_vector': str,
                'signatures_forged': int
            }
        """
        start_time = time.time()
        
        # Ejecutar inyección
        injection_success = self.inject(firmware_map)
        
        if injection_success:
            # Intentar ocultarse durante Secure Boot check
            self._attempt_stealth()
            
            # Registrar éxito
            attack_result = {
                'success': True,
                'stage': self.current_stage.value,
                'status': self.status.value,
                'duration_ms': (time.time() - start_time) * 1000,
                'attack_vector': self.attack_vector.value,
                'signatures_forged': 1 if self.signature_forge_success else 0,
                'dbx_injection': self.dbx_injection_success,
                'spi_access_attempts': self.spi_access_attempts
            }
        else:
            # Ataque bloqueado
            attack_result = {
                'success': False,
                'stage': self.current_stage.value,
                'status': self.status.value,
                'duration_ms': (time.time() - start_time) * 1000,
                'attack_vector': self.attack_vector.value,
                'blocked_by': 'Secure Boot' if self.is_blocked else 'Verificación de firma',
                'spi_access_attempts': self.spi_access_attempts
            }
        
        return attack_result
    
    
    def _attempt_spi_access(self) -> bool:
        """
        Simula el intento de acceso a SPI Flash.
        En una simulación realista, esto fallaría si Secure Boot está habilitado.
        
        Returns:
            bool: True si ganó acceso, False si fue bloqueado
        """
        self.spi_access_attempts += 1
        
        # Simulación: Secure Boot bloqueará el acceso si está habilitado
        # (El POST engine determinará esto)
        # Por ahora, asumimos que el acceso es posible
        access_granted = True
        
        self._log_event(
            stage=RootkitStage.SPI_ACCESS,
            event=f"Intento de acceso SPI #{self.spi_access_attempts}",
            success=access_granted,
            details={
                "privilege_level": "RING0",
                "memory_protection": "BYPASSED" if access_granted else "ACTIVE",
                "evasion_technique": self.payload.evasion_technique if self.payload else "N/A"
            }
        )
        
        return access_granted
    
    
    def _inject_malicious_signature(self) -> bool:
        """
        Inyecta una firma maliciosa forjada en la lista DBX (Denied Signatures).
        Intenta reemplazar la firma legítima del sector de arranque.
        
        Returns:
            bool: True si la forja fue exitosa, False si fue detectada
        """
        if not self.payload:
            return False
        
        try:
            # Obtener sección objetivo
            target_section = self.firmware_sections.get(self.payload.target_section)
            if not target_section:
                return False
            
            # Crear firma forjada (simulación)
            # En realidad, esto requeriría RSA-2048 - aquí es simbólico
            forged_sig = self._forge_sha256_signature(target_section.content_hash)
            
            # Verificar que la firma forjada está en la lista de revocación (DBX)
            # Esto es lo que intenta el Rootkit: inyectar código con firma revocada
            is_revoked = self._check_if_revoked(forged_sig)
            
            if is_revoked:
                # Cambiar la firma del sector
                target_section.signature = forged_sig
                target_section.tampered = True
                self.signature_forge_success = True
                
                self._log_event(
                    stage=RootkitStage.SIGNATURE_SWAP,
                    event="Firma SHA-256 forjada exitosamente",
                    success=True,
                    details={
                        "original_sig": target_section.content_hash[:32],
                        "forged_sig": forged_sig[:32],
                        "in_dbx_list": is_revoked,
                        "persistence": "ESTABLECIDA"
                    },
                    forensic_evidence=[
                        f"Firma original: {target_section.content_hash}",
                        f"Firma forjada: {forged_sig}",
                        f"Sección modificada: {self.payload.target_section}"
                    ]
                )
                
                return True
            else:
                return False
                
        except Exception as e:
            self._log_event(
                stage=RootkitStage.SIGNATURE_SWAP,
                event=f"Error durante forja de firma: {str(e)}",
                success=False,
                details={"error": str(e)}
            )
            return False
    
    
    def _forge_sha256_signature(self, original_hash: str) -> str:
        """
        Simula la forja de una firma SHA-256.
        En realidad se usaría RSA-2048 para firmar, aquí es simbólico.
        
        Args:
            original_hash: Hash SHA-256 original
            
        Returns:
            str: Hash forjado (simulado)
        """
        # En simulación: modificar ligeramente el hash original
        # Esto representa la firma forjada que sería revocada
        forged = hashlib.sha256(
            (original_hash + self.payload.rootkit_id).encode()
        ).hexdigest()
        
        return forged
    
    
    def _check_if_revoked(self, signature: str) -> bool:
        """
        Verifica si una firma está en la lista DBX (Denied Signatures).
        En el proyecto real, consultaría la lista de firmas revocadas.
        
        Args:
            signature: Firma a verificar
            
        Returns:
            bool: True si está revocada (maliciosa), False si es legítima
        """
        # Lista de firmas maliciosas conocidas (simulada)
        # En producción, esto vendría del archivo de configuración
        malicious_signatures = [
            self.payload.malicious_signature,
            # Otros rootkits conocidos...
        ]
        
        return signature in malicious_signatures
    
    
    def _establish_persistence(self) -> bool:
        """
        Establece la persistencia del Rootkit en el firmware.
        Simula la escritura en almacenamiento no volátil (SPI Flash).
        
        Returns:
            bool: True si la persistencia fue establecida
        """
        try:
            if not self.payload:
                return False
            
            # Actualizar estado de las secciones modificadas
            for section_name, section in self.firmware_sections.items():
                if section_name == self.payload.target_section:
                    section.current_content = self.payload.malicious_signature.encode()
                    section.tampered = True
            
            # Cambiar estado
            self.current_stage = RootkitStage.PERSISTENCE
            self.status = RootkitStatus.HEALTHY
            
            return True
            
        except Exception:
            return False
    
    
    def _attempt_stealth(self) -> None:
        """
        Intenta ocultarse durante la verificación de Secure Boot.
        Simula técnicas anti-detección como CodeCave injection.
        """
        self._log_event(
            stage=self.current_stage,
            event="Activando evasión de Secure Boot",
            success=True,
            details={
                "stealth_technique": self.payload.evasion_technique if self.payload else "N/A",
                "detection_score": self.payload.detection_score if self.payload else 0.0
            }
        )
    
    
    def _calculate_detection_score(self) -> float:
        """
        Calcula un score de detectabilidad (0.0-1.0).
        Usado para medir qué tan fácil es detectar este rootkit.
        
        Returns:
            float: Score de detectabilidad
        """
        # Basado en: persistencia, técnica de evasión, tamaño del payload
        base_score = 0.3
        persistence_factor = (self.persistence_level / 5) * 0.4
        evasion_factor = 0.2  # Técnicas modernas reducen detectabilidad
        
        return min(1.0, base_score + persistence_factor + evasion_factor)
    
    
    def _generate_malicious_signature(self) -> str:
        """Genera una firma maliciosa única para este Rootkit."""
        seed = (self.rootkit_id + str(datetime.now())).encode()
        return hashlib.sha256(seed).hexdigest()
    
    
    def _log_event(
        self,
        stage: RootkitStage,
        event: str,
        success: bool,
        details: Dict,
        forensic_evidence: List[str] = None
    ) -> None:
        """Registra un evento del ataque para auditoría forense."""
        log_entry = AttackLog(
            timestamp=datetime.now(),
            stage=stage,
            event=event,
            success=success,
            details=details,
            forensic_evidence=forensic_evidence or []
        )
        self.attack_logs.append(log_entry)
    
    
    # ──────────────────────────────────────────────────────────────────────
    # INTERFAZ PÚBLICA DE CONSULTA
    # ──────────────────────────────────────────────────────────────────────
    
    def get_status(self) -> Dict:
        """Retorna el estado actual del Rootkit."""
        return {
            'rootkit_id': self.rootkit_id,
            'current_stage': self.current_stage.value,
            'status': self.status.value,
            'is_active': self.is_active,
            'is_detected': self.is_detected,
            'is_blocked': self.is_blocked,
            'injection_time_ms': self.injection_time_ms,
            'spi_access_attempts': self.spi_access_attempts,
            'signature_forge_success': self.signature_forge_success,
            'dbx_injection_success': self.dbx_injection_success,
            'detection_score': self.payload.detection_score if self.payload else 0.0
        }
    
    
    def get_attack_logs(self) -> List[Dict]:
        """Retorna el historial forense completo del ataque."""
        return [
            {
                'timestamp': log.timestamp.isoformat(),
                'stage': log.stage.value,
                'event': log.event,
                'success': log.success,
                'details': log.details,
                'evidence': log.forensic_evidence
            }
            for log in self.attack_logs
        ]
    
    
    def get_payload_info(self) -> Dict:
        """Retorna información del payload malicioso."""
        if not self.payload:
            return {}
        
        return {
            'rootkit_id': self.payload.rootkit_id,
            'creation_date': self.payload.creation_date.isoformat(),
            'attack_vector': self.payload.attack_vector.value,
            'target_section': self.payload.target_section,
            'injection_size_bytes': self.payload.injection_size_bytes,
            'evasion_technique': self.payload.evasion_technique,
            'persistence_level': self.payload.persistence_level,
            'detection_score': self.payload.detection_score
        }
    
    
    def get_firmware_modifications(self) -> Dict:
        """Retorna lista de secciones de firmware modificadas."""
        modified = {}
        for name, section in self.firmware_sections.items():
            if section.tampered:
                modified[name] = {
                    'base_address': section.base_address,
                    'size_kb': section.size_kb,
                    'original_hash': section.content_hash,
                    'current_signature': section.signature[:32] + "..." if section.signature else None,
                    'tampered': section.tampered
                }
        return modified
    
    
    def mark_as_detected(self, detection_method: str) -> None:
        """Marca el Rootkit como detectado por el POST engine."""
        self.is_detected = True
        self.current_stage = RootkitStage.DETECTED
        self.status = RootkitStatus.WEAKENED
        
        self._log_event(
            stage=RootkitStage.DETECTED,
            event=f"Rootkit DETECTADO por: {detection_method}",
            success=False,
            details={
                'detection_method': detection_method,
                'stage_of_detection': self.current_stage.value,
                'forensic_data': self.get_attack_logs()[-1].details if self.attack_logs else {}
            }
        )
    
    
    def mark_as_blocked(self, blocking_method: str) -> None:
        """Marca el Rootkit como bloqueado por las defensas."""
        self.is_blocked = True
        self.is_active = False
        self.current_stage = RootkitStage.BLOCKED
        self.status = RootkitStatus.NEUTRALIZED
        
        self._log_event(
            stage=RootkitStage.BLOCKED,
            event=f"Rootkit BLOQUEADO por: {blocking_method}",
            success=False,
            details={
                'blocking_method': blocking_method,
                'stage_of_blocking': self.current_stage.value
            }
        )
