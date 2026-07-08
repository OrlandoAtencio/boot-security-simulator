"""
gui/rootkit_controller.py — Controlador GUI para Inyección de Rootkit
=====================================================================
Proporciona callbacks y handlers para los botones de inyección de Rootkit
en la interfaz gráfica Tkinter.

Responsable: Michael (Fase 4)
Función: Conectar eventos de GUI con la ejecución del módulo Rootkit
         y transmitir cambios de estado al POST engine.

COMPONENTES GUI:
1. Botón "Inyectar Rootkit" - Activa el ataque
2. Panel de Estado del Rootkit - Muestra progreso en tiempo real
3. Logs Forenses - Visualización de eventos de ataque
4. Indicadores de Detección - Muestra si fue detectado/bloqueado
"""

from __future__ import annotations
from typing import Callable, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import threading


class GUIRootkitState(Enum):
    """Estados que pueden mostrarse en la GUI."""
    IDLE            = "INACTIVO"
    INJECTING       = "INYECTANDO..."
    ACTIVE          = "ACTIVO EN FIRMWARE"
    DETECTED        = "¡DETECTADO!"
    BLOCKED         = "BLOQUEADO"
    EVASION_ACTIVE  = "EVASIÓN ACTIVA"


class RootkitGUIController:
    """
    Controlador que gestiona la interacción entre la GUI y el módulo Rootkit.
    
    Proporciona:
    - Callbacks para botones de la interfaz
    - Actualización de widgets en tiempo real
    - Sincronización con el POST engine
    - Visualización de eventos de ataque
    """
    
    def __init__(
        self,
        rootkit_module: Any,  # Instancia de RootkitModule
        combat_system: Any,    # Instancia de RootkitCombatSystem
        update_callback: Optional[Callable] = None,
        log_callback: Optional[Callable] = None
    ):
        """
        Inicializa el controlador.
        
        Args:
            rootkit_module: Instancia del módulo Rootkit
            combat_system: Sistema de combate Rootkit/Defensa
            update_callback: Función para actualizar widgets (ej: label.config)
            log_callback: Función para agregar eventos a log visual
        """
        self.rootkit = rootkit_module
        self.combat_system = combat_system
        
        # Callbacks para actualización de GUI
        self.update_callback = update_callback or (lambda **kw: None)
        self.log_callback = log_callback or (lambda msg, level: None)
        
        # Estado actual
        self.gui_state = GUIRootkitState.IDLE
        self.injection_active = False
        self.attack_thread: Optional[threading.Thread] = None
        
        # Histórico de cambios para visualización
        self.state_history: List[Dict] = []
        self.event_queue: List[Dict] = []
    
    
    def on_inject_button_clicked(self, firmware_map: Dict) -> None:
        """
        Callback para el botón "Inyectar Rootkit" en la GUI.
        
        Inicia el ataque en un thread separado para no bloquear la UI.
        
        Args:
            firmware_map: Mapa de secciones de firmware del sistema
        """
        if self.injection_active:
            self._log_event(
                "Inyección ya en progreso",
                level="WARNING"
            )
            return
        
        self.injection_active = True
        self.gui_state = GUIRootkitState.INJECTING
        self._update_state_label()
        
        # Ejecutar inyección en thread separado
        self.attack_thread = threading.Thread(
            target=self._execute_injection_thread,
            args=(firmware_map,),
            daemon=True
        )
        self.attack_thread.start()
    
    
    def _execute_injection_thread(self, firmware_map: Dict) -> None:
        """
        Ejecuta el ataque del Rootkit en un thread separado.
        Mantiene la GUI responsiva y permite mostrar progreso en tiempo real.
        """
        try:
            # Fase 1: Mostrar inicio de inyección
            self._log_event(
                f"🔴 INYECCIÓN DE ROOTKIT INICIADA",
                level="CRITICAL",
                color_hint="red"
            )
            
            self._log_event(
                f"ID Rootkit: {self.rootkit.rootkit_id}",
                level="INFO"
            )
            
            self._log_event(
                f"Vector de Ataque: {self.rootkit.attack_vector.value}",
                level="INFO"
            )
            
            # Fase 2: Ejecutar ataque
            attack_result = self.rootkit.execute_attack(firmware_map)
            
            if attack_result['success']:
                self.gui_state = GUIRootkitState.ACTIVE
                self._log_event(
                    "✓ Rootkit se estableció en firmware",
                    level="CRITICAL",
                    color_hint="red"
                )
                self._log_event(
                    f"Tiempo de inyección: {attack_result['duration_ms']:.2f}ms",
                    level="INFO"
                )
                self._log_event(
                    f"Intentos de acceso SPI: {attack_result['spi_access_attempts']}",
                    level="INFO"
                )
            else:
                self.gui_state = GUIRootkitState.BLOCKED
                self._log_event(
                    f"✗ Rootkit BLOQUEADO: {attack_result.get('blocked_by', 'Unknown')}",
                    level="WARNING",
                    color_hint="yellow"
                )
            
            # Fase 3: Mostrar payload info
            payload_info = self.rootkit.get_payload_info()
            if payload_info:
                self._log_event(
                    f"Tamaño de payload: {payload_info['injection_size_bytes']} bytes",
                    level="INFO"
                )
                self._log_event(
                    f"Técnica de evasión: {payload_info['evasion_technique']}",
                    level="INFO"
                )
                self._log_event(
                    f"Nivel de persistencia: {payload_info['persistence_level']}/5",
                    level="INFO"
                )
            
            # Fase 4: Simular respuesta del POST engine
            self._simulate_post_detection(firmware_map)
            
        except Exception as e:
            self._log_event(
                f"ERROR durante inyección: {str(e)}",
                level="ERROR",
                color_hint="red"
            )
            self.gui_state = GUIRootkitState.IDLE
        
        finally:
            self.injection_active = False
            self._update_state_label()
    
    
    def _simulate_post_detection(self, firmware_map: Dict) -> None:
        """
        Simula la respuesta del POST engine al Rootkit inyectado.
        
        El POST engine ejecutaría esto en SECURE_BOOT_VERIFY etapa.
        """
        self._log_event(
            "",
            level="SEPARATOR"  # Línea divisoria visual
        )
        
        self._log_event(
            "🔍 POST ENGINE: Iniciando verificación de Secure Boot...",
            level="INFO"
        )
        
        # Ejecutar detección a través del combat system
        from rootkit_integration import InjectionPoint
        
        boot_result = self.combat_system.process_boot_with_threat(
            rootkit_module=self.rootkit,
            firmware_map=firmware_map,
            injection_point=InjectionPoint.SECURE_BOOT_VERIFY
        )
        
        # Procesar resultados de detección
        if boot_result['secure_boot_passed']:
            self._log_event(
                "✓ Verificación de Secure Boot: PASÓ",
                level="SUCCESS",
                color_hint="green"
            )
            if self.gui_state != GUIRootkitState.BLOCKED:
                self.gui_state = GUIRootkitState.EVASION_ACTIVE
                self._log_event(
                    "⚠ Rootkit evadió Secure Boot",
                    level="CRITICAL",
                    color_hint="red"
                )
        else:
            self._log_event(
                "✗ Verificación de Secure Boot: FALLÓ",
                level="CRITICAL",
                color_hint="red"
            )
            
            # Mostrar detalles de detección
            if 'integrity_scan' in boot_result:
                scan = boot_result['integrity_scan']
                self._log_event(
                    f"Amenazas detectadas: {scan['threats_found']}",
                    level="CRITICAL"
                )
                
                for detail in scan['details']:
                    self._log_event(
                        f"  • {detail['section']}: {detail['verification_result']}",
                        level="CRITICAL"
                    )
            
            self.gui_state = GUIRootkitState.DETECTED
            self.rootkit.mark_as_detected("POST Engine - Secure Boot")
        
        # Mostrar estadísticas del combat system
        self._log_event(
            "",
            level="SEPARATOR"
        )
        
        detector_report = self.combat_system.rootkit_detector.get_detection_report()
        
        self._log_event(
            f"📊 ESTADÍSTICAS DE DETECCIÓN:",
            level="INFO"
        )
        
        self._log_event(
            f"  Total de detecciones: {detector_report['total_detections']}",
            level="INFO"
        )
        
        self._log_event(
            f"  Rootkits encontrados: {detector_report['rootkits_found']}",
            level="INFO"
        )
        
        self._log_event(
            f"  Veredicto final: {detector_report['verdict']}",
            level="INFO" if detector_report['verdict'] == 'SISTEMA_LIMPIO' else "CRITICAL"
        )
    
    
    def on_abort_injection(self) -> None:
        """
        Callback para botón de abortar inyección en progreso.
        """
        if self.injection_active and self.attack_thread and self.attack_thread.is_alive():
            self._log_event(
                "Abortando inyección en progreso...",
                level="WARNING"
            )
            # Nota: En Python, no se puede forzar detención de thread
            # Se espera a que termine naturalmente
            self.injection_active = False
    
    
    def on_clear_logs(self) -> None:
        """Limpia el historial de eventos en la GUI."""
        self.event_queue.clear()
        self._log_event(
            "📋 Logs limpios",
            level="INFO"
        )
    
    
    def get_status_display(self) -> Dict[str, str]:
        """
        Retorna información para mostrar en el panel de estado.
        
        Returns:
            Dict con valores para widgets:
                {
                    'state_text': str,
                    'state_color': str (color hex),
                    'active_text': str,
                    'modification_text': str
                }
        """
        rootkit_status = self.rootkit.get_status()
        
        # Mapeo de colores según estado
        state_colors = {
            GUIRootkitState.IDLE: "#8B949E",           # gris
            GUIRootkitState.INJECTING: "#D29922",      # naranja
            GUIRootkitState.ACTIVE: "#F85149",         # rojo
            GUIRootkitState.DETECTED: "#3FB950",       # verde
            GUIRootkitState.BLOCKED: "#3FB950",        # verde
            GUIRootkitState.EVASION_ACTIVE: "#F85149", # rojo
        }
        
        modifications = self.rootkit.get_firmware_modifications()
        mod_text = f"{len(modifications)} secciones modificadas" if modifications else "Sin modificaciones"
        
        return {
            'state_text': self.gui_state.value,
            'state_color': state_colors.get(self.gui_state, "#8B949E"),
            'active_text': "✓ ACTIVO" if rootkit_status['is_active'] else "✗ INACTIVO",
            'detected_text': "🚨 DETECTADO" if rootkit_status['is_detected'] else "OCULTO",
            'blocked_text': "🛡 BLOQUEADO" if rootkit_status['is_blocked'] else "EN PROGRESO",
            'modification_text': mod_text,
            'stage': rootkit_status['current_stage']
        }
    
    
    def get_attack_logs_for_display(self, limit: int = None) -> List[Dict]:
        """
        Retorna los eventos de ataque formateados para mostrar en GUI.
        
        Args:
            limit: Número máximo de eventos a retornar (None = todos)
            
        Returns:
            List de Dicts con: {
                'timestamp': str,
                'event': str,
                'level': str,
                'color': str (hex)
            }
        """
        events = self.event_queue
        if limit:
            events = events[-limit:]
        
        return events
    
    
    def get_forensic_report(self) -> str:
        """
        Genera un reporte forense del ataque en formato texto.
        Útil para exportar o analizar post-mortem.
        """
        lines = []
        lines.append("=" * 80)
        lines.append("REPORTE FORENSE DE ATAQUE ROOTKIT - FASE 4")
        lines.append("=" * 80)
        lines.append("")
        
        # Información del Rootkit
        rootkit_status = self.rootkit.get_status()
        lines.append("INFORMACIÓN DEL ROOTKIT:")
        lines.append(f"  ID: {rootkit_status['rootkit_id']}")
        lines.append(f"  Etapa actual: {rootkit_status['current_stage']}")
        lines.append(f"  Estado: {rootkit_status['status']}")
        lines.append(f"  Activo: {'✓' if rootkit_status['is_active'] else '✗'}")
        lines.append(f"  Detectado: {'✓' if rootkit_status['is_detected'] else '✗'}")
        lines.append(f"  Bloqueado: {'✓' if rootkit_status['is_blocked'] else '✗'}")
        lines.append("")
        
        # Métrica de ataque
        lines.append("MÉTRICAS DE ATAQUE:")
        lines.append(f"  Tiempo de inyección: {rootkit_status['injection_time_ms']:.2f}ms")
        lines.append(f"  Intentos SPI: {rootkit_status['spi_access_attempts']}")
        lines.append(f"  Firmas forjadas: {1 if rootkit_status['signature_forge_success'] else 0}")
        lines.append(f"  Inyección DBX: {'✓' if rootkit_status['dbx_injection_success'] else '✗'}")
        lines.append(f"  Score de detectabilidad: {rootkit_status['detection_score']:.2f}")
        lines.append("")
        
        # Payload
        payload_info = self.rootkit.get_payload_info()
        if payload_info:
            lines.append("INFORMACIÓN DEL PAYLOAD:")
            lines.append(f"  Vector: {payload_info['attack_vector']}")
            lines.append(f"  Tamaño: {payload_info['injection_size_bytes']} bytes")
            lines.append(f"  Evasión: {payload_info['evasion_technique']}")
            lines.append(f"  Persistencia: {payload_info['persistence_level']}/5")
            lines.append("")
        
        # Modificaciones de firmware
        modifications = self.rootkit.get_firmware_modifications()
        if modifications:
            lines.append("SECCIONES DE FIRMWARE MODIFICADAS:")
            for section_name, mod_data in modifications.items():
                lines.append(f"  [{section_name}]")
                lines.append(f"    Dirección: {mod_data['base_address']}")
                lines.append(f"    Tamaño: {mod_data['size_kb']} KB")
                lines.append(f"    Manipulado: {'✓' if mod_data['tampered'] else '✗'}")
            lines.append("")
        
        # Logs de eventos
        lines.append("HISTORIAL DE EVENTOS:")
        for event in self.event_queue[-20:]:  # Últimos 20 eventos
            lines.append(f"  [{event.get('level', 'INFO')}] {event.get('timestamp', '')}: {event.get('message', '')}")
        lines.append("")
        
        # Combat log
        combat_log = self.combat_system.get_combat_log()
        if combat_log:
            lines.append("REGISTRO DE COMBATE (ATAQUE/DEFENSA):")
            for entry in combat_log:
                lines.append(f"  [{entry['phase']}] {entry['timestamp']}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    
    # ──────────────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ──────────────────────────────────────────────────────────────────────
    
    def _log_event(
        self,
        message: str,
        level: str = "INFO",
        color_hint: Optional[str] = None
    ) -> None:
        """
        Registra un evento y lo añade a la cola de visualización.
        
        Args:
            message: Mensaje del evento
            level: Nivel ("INFO", "WARNING", "CRITICAL", "ERROR", "SUCCESS", "SEPARATOR")
            color_hint: Sugerencia de color para GUI
        """
        event = {
            'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3],
            'message': message,
            'level': level,
            'color_hint': color_hint or self._get_default_color(level)
        }
        
        self.event_queue.append(event)
        
        # Callback opcional para logger externo
        if self.log_callback:
            self.log_callback(message, level)
    
    
    def _get_default_color(self, level: str) -> str:
        """Retorna color por defecto según nivel de evento."""
        color_map = {
            "INFO": "#8B949E",
            "WARNING": "#D29922",
            "CRITICAL": "#F85149",
            "ERROR": "#F85149",
            "SUCCESS": "#3FB950",
            "SEPARATOR": "#30363D",
        }
        return color_map.get(level, "#C9D1D9")
    
    
    def _update_state_label(self) -> None:
        """Actualiza el label de estado mediante callback."""
        status = self.get_status_display()
        self.update_callback(
            text=status['state_text'],
            foreground=status['state_color']
        )
