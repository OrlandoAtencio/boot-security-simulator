"""
skeleton.py — Esqueleto de Clases Base
========================================
Simulador Interactivo de Seguridad en el Proceso de Arranque
Equipo 9 · Arquitectura y Organización de Computadoras · UTP

Contiene las 6 clases base del proyecto con sus métodos vacíos.
Cada integrante debe buscar su clase, leer los docstrings
y programar SOLO los métodos marcados con TODO.

CLASES:
  1. CPU          → Backend POST/Hardware
  2. Memoria      → Backend POST/Hardware
  3. BIOS         → Backend BIOS/Almacenamiento
  4. SecureBoot   → Backend Secure Boot
  5. Rootkit      → Backend Rootkit
  6. LogSystem    → Backend Logs
"""

from config.settings import (
    BootStage,
    SecurityStatus,
    POSTResult,
    RootkitType,
    SimulationConfig,
)


# ==============================================================================
# CLASE 1 — CPU
# Responsable: Backend POST/Hardware
# ==============================================================================

class CPU:
    """
    Simula el comportamiento de la CPU durante el proceso POST.

    En hardware real, al encenderse la PC:
      - La CPU se resetea y salta al Reset Vector (0xFFFFFFF0 en x86).
      - Ejecuta el BIST (Built-In Self-Test) para verificar sus circuitos.
      - Inicializa sus registros internos a valores conocidos.
      - El core principal (BSP) despierta a los demás cores (APs).
    """

    def __init__(self, cores: int, frecuencia_mhz: int) -> None:
        self.cores          = cores
        self.frecuencia_mhz = frecuencia_mhz
        self.encendida      = False
        self.bist_ok        = False

    def encender(self) -> None:
        """
        Simula el encendido físico de la CPU.
        Debe marcar la CPU como encendida y establecer el Reset Vector.

        TODO: Implementar — Backend POST/Hardware
        """
        pass

    def ejecutar_post(self) -> POSTResult:
        """
        Ejecuta el Built-In Self-Test (BIST) de la CPU.
        Verifica ALU, FPU, registros internos y predictor de saltos.
        Retorna POSTResult.PASS si todo está bien, POSTResult.FAIL si no.

        TODO: Implementar — Backend POST/Hardware
        """
        pass

    def inicializar_registros(self) -> bool:
        """
        Pone los registros de la CPU en sus valores estándar post-reset.
        Ejemplo x86: CS=0xF000, IP=0xFFF0, EAX=0, EFLAGS=0x0002, etc.
        Retorna True si fue exitoso.

        TODO: Implementar — Backend POST/Hardware
        """
        pass

    def obtener_info(self) -> dict:
        """
        Retorna un diccionario con el estado actual de la CPU.
        Usado por la interfaz gráfica para mostrar el panel de hardware.

        TODO: Implementar — Backend POST/Hardware
        """
        pass


# ==============================================================================
# CLASE 2 — Memoria
# Responsable: Backend POST/Hardware
# ==============================================================================

class Memoria:
    """
    Simula la memoria RAM del sistema durante el POST.

    En hardware real:
      - El chipset detecta los módulos DIMM leyendo sus chips SPD via SMBus.
      - Se ejecuta el Walking Bit Test para encontrar celdas defectuosas.
      - El BIOS construye el mapa de memoria E820 y lo entrega al OS.
    """

    def __init__(self, capacidad_mb: int) -> None:
        self.capacidad_mb = capacidad_mb
        self.modulos      = []
        self.mapa         = {}
        self.test_ok      = False

    def detectar_modulos(self) -> list:
        """
        Detecta los módulos DIMM instalados simulando el protocolo SPD.
        Retorna una lista de módulos con su capacidad, tipo y fabricante.

        TODO: Implementar — Backend POST/Hardware
        """
        pass

    def ejecutar_post(self) -> POSTResult:
        """
        Ejecuta el Walking Bit Test sobre todos los módulos de RAM.
        Escribe y lee patrones (0x00, 0xFF, 0x55, 0xAA) en cada celda.
        Retorna POSTResult.PASS si toda la RAM está OK, FAIL si hay fallas.

        TODO: Implementar — Backend POST/Hardware
        """
        pass

    def construir_mapa(self) -> dict:
        """
        Construye el mapa de memoria E820 del sistema.
        Divide la RAM en regiones: convencional, VGA, BIOS, extendida.
        Retorna un diccionario con las regiones y sus direcciones.

        TODO: Implementar — Backend POST/Hardware
        """
        pass

    def obtener_info(self) -> dict:
        """
        Retorna un diccionario con el estado actual de la memoria.
        Usado por la interfaz gráfica para mostrar el panel de hardware.

        TODO: Implementar — Backend POST/Hardware
        """
        pass


# ==============================================================================
# CLASE 3 — BIOS
# Responsable: Backend BIOS/Almacenamiento
# ==============================================================================

class BIOS:
    """
    Simula el firmware BIOS/UEFI de la placa base.

    El BIOS es el primer software que ejecuta la CPU. Vive en una ROM Flash
    accesible via el bus LPC. Es responsable de inicializar el hardware,
    detectar dispositivos de arranque y cargar el bootloader del OS.

    IMPORTANTE para el Rootkit:
      El método adulterear_firmware() es llamado por la clase Rootkit
      para simular una infección. La verificación de integridad debe detectarlo.
    """

    def __init__(self) -> None:
        self.firmware_data      = b""
        self.hash_referencia    = ""
        self.tabla_interrupciones = {}
        self.dispositivos_boot  = []
        self.cargado            = False

    def cargar(self) -> bool:
        """
        Carga el firmware desde la ROM (o genera datos simulados).
        Calcula y guarda el hash SHA-256 del firmware como referencia limpia.
        Retorna True si la carga fue exitosa.

        TODO: Implementar — Backend BIOS/Almacenamiento
        """
        pass

    def verificar_integridad(self) -> bool:
        """
        Verifica que el firmware no ha sido modificado.
        Compara el hash SHA-256 actual del firmware con el hash de referencia.
        Retorna True si son iguales (íntegro), False si difieren (adulterado).

        TODO: Implementar — Backend BIOS/Almacenamiento
        """
        pass

    def inicializar_tabla_interrupciones(self) -> dict:
        """
        Construye la Interrupt Vector Table (IVT).
        Mapea cada número de interrupción a su handler.
        Ejemplo: INT 13h → Servicios de Disco, INT 10h → Servicios de Video.
        Retorna el diccionario {numero_int: descripcion}.

        TODO: Implementar — Backend BIOS/Almacenamiento
        """
        pass

    def detectar_dispositivos_boot(self) -> list:
        """
        Detecta los dispositivos desde los que se puede arrancar.
        Verifica cuáles tienen MBR/GPT válido con un bootloader.
        Retorna la lista ordenada por prioridad de arranque.

        TODO: Implementar — Backend BIOS/Almacenamiento
        """
        pass

    def adulterear_firmware(self, payload: bytes) -> bool:
        """
        Inyecta bytes maliciosos en el firmware cargado en memoria.
        Llamado por la clase Rootkit para simular una infección.

        IMPORTANTE: NO actualizar self.hash_referencia después de modificar
        self.firmware_data. Así verificar_integridad() detectará la diferencia.

        Retorna True si la adulteración fue aplicada.

        TODO: Implementar — Backend BIOS/Almacenamiento
        """
        pass

    def obtener_info(self) -> dict:
        """
        Retorna un diccionario con el estado actual del BIOS.
        Usado por la interfaz gráfica para mostrar el panel del BIOS.

        TODO: Implementar — Backend BIOS/Almacenamiento
        """
        pass


# ==============================================================================
# CLASE 4 — SecureBoot
# Responsable: Backend Secure Boot
# ==============================================================================

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
        self.habilitado      = habilitado
        self.platform_key    = None
        self.kek             = None
        self.db              = []   # Firmas permitidas
        self.dbx             = []   # Firmas revocadas
        self.cadena_valida   = False
        self.estado          = SecurityStatus.UNKNOWN

    def inicializar(self) -> bool:
        """
        Genera y carga las claves y bases de datos para la simulación.
        Debe generar: PK, KEK, db (con hash del bootloader limpio), dbx vacío.
        Retorna True si la inicialización fue exitosa.

        TODO: Implementar — Backend Secure Boot
        """
        pass

    def verificar_firmas(self, datos: bytes) -> bool:
        """
        Verifica la cadena completa de confianza sobre los datos dados.
        Sigue el orden estricto: PK → KEK → db → Bootloader → dbx.
        Retorna True si toda la cadena es válida, False si algún paso falla.

        TODO: Implementar — Backend Secure Boot
        """
        pass

    def verificar_contra_dbx(self, hash_valor: str) -> bool:
        """
        Verifica que un hash NO esté en la lista negra (dbx).
        Retorna True si está limpio (no en dbx), False si está revocado.

        TODO: Implementar — Backend Secure Boot
        """
        pass

    def agregar_a_dbx(self, hash_valor: str, motivo: str) -> bool:
        """
        Agrega un hash a la lista de firmas revocadas (dbx).
        Simula la revocación de un bootloader comprometido.
        Retorna True si fue agregado exitosamente.

        TODO: Implementar — Backend Secure Boot
        """
        pass

    def obtener_estado(self) -> dict:
        """
        Retorna un diccionario con el estado actual de Secure Boot.
        Usado por la interfaz gráfica para mostrar el panel de Secure Boot.

        TODO: Implementar — Backend Secure Boot
        """
        pass


# ==============================================================================
# CLASE 5 — Rootkit
# Responsable: Backend Rootkit
# ==============================================================================

class Rootkit:
    """
    Simula el comportamiento de un rootkit de firmware o bootkit.

    ADVERTENCIA: Solo para fines educativos. No representa malware funcional.

    Tipos simulados:
      - FIRMWARE: Se instala en la ROM Flash del BIOS. Sobrevive formateos.
                  Ejemplo real: LoJax (APT28, 2018), CosmicStrand (2022).
      - BOOTKIT:  Se instala en el MBR (sector 0 del disco). Controla el boot
                  antes de que cargue el OS.
                  Ejemplo real: TDL4/Alureon (2010).

    El ataque funciona llamando a:
      bios.adulterear_firmware(payload) para el tipo FIRMWARE.
    """

    def __init__(self, tipo: RootkitType, bios: BIOS) -> None:
        self.tipo      = tipo
        self.bios      = bios
        self.inyectado = False
        self.payload   = b""

    def crear_payload(self) -> bytes:
        """
        Genera los bytes maliciosos del rootkit según su tipo.
        Para FIRMWARE: simular un módulo DXE malicioso del UEFI.
        Para BOOTKIT:  simular un bootstrap loader malicioso (446 bytes).
        Guarda el resultado en self.payload y lo retorna.

        TODO: Implementar — Backend Rootkit
        """
        pass

    def inyectar(self) -> bool:
        """
        Inyecta el rootkit en el sistema objetivo.
        Debe llamar a self.bios.adulterear_firmware(self.payload).
        Marca self.inyectado = True si fue exitoso.
        Retorna True si la inyección fue exitosa.

        TODO: Implementar — Backend Rootkit
        """
        pass

    def simular_evasion(self) -> list:
        """
        Retorna una lista con las técnicas de evasión que emplearía el rootkit.
        Ejemplos: hook de INT 13h, SMM Ring-2, DKOM, patch de antivirus.

        TODO: Implementar — Backend Rootkit
        """
        pass

    def obtener_info(self) -> dict:
        """
        Retorna un diccionario con el estado del rootkit.
        Usado por la interfaz gráfica para mostrar el panel de ataque.

        TODO: Implementar — Backend Rootkit
        """
        pass


# ==============================================================================
# CLASE 6 — LogSystem
# Responsable: Backend Logs
# ==============================================================================

class LogSystem:
    """
    Sistema centralizado de registro de eventos del simulador.

    Registra cada evento del proceso de arranque con su timestamp,
    nivel de severidad y componente de origen. Permite exportar
    el historial completo a un archivo JSON al finalizar la simulación.
    """

    NIVELES = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self) -> None:
        self.entradas = []

    def registrar_evento(self, nivel: str, fuente: str, mensaje: str) -> dict:
        """
        Crea y almacena una entrada de log con timestamp automático.
        nivel debe ser uno de: DEBUG, INFO, WARNING, ERROR, CRITICAL.
        fuente es el componente que genera el log (ej. "CPU", "SecureBoot").
        Retorna la entrada creada como diccionario.

        TODO: Implementar — Backend Logs
        """
        pass

    def obtener_logs(self, nivel_minimo: str = "DEBUG") -> list:
        """
        Retorna la lista de entradas filtradas por nivel mínimo.
        Ejemplo: nivel_minimo="WARNING" retorna WARNING, ERROR y CRITICAL.
        El orden debe ser cronológico (más antiguo primero).

        TODO: Implementar — Backend Logs
        """
        pass

    def exportar_json(self, ruta: str) -> bool:
        """
        Guarda todos los logs en un archivo JSON en la ruta indicada.
        Crea el directorio si no existe.
        Retorna True si se guardó correctamente, False si hubo error.

        TODO: Implementar — Backend Logs
        """
        pass

    def limpiar(self) -> None:
        """
        Vacía la lista de logs en memoria.
        No borra el archivo en disco si ya fue exportado.

        TODO: Implementar — Backend Logs
        """
        pass

    def resumen(self) -> dict:
        """
        Retorna un conteo de entradas por nivel de severidad.
        Ejemplo: {"DEBUG": 0, "INFO": 5, "WARNING": 2, "ERROR": 0, "CRITICAL": 1}

        TODO: Implementar — Backend Logs
        """
        pass
