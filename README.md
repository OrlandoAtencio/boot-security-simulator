# 🔐 Simulador Interactivo de Seguridad en el Proceso de Arranque

> **Universidad Tecnológica de Panamá — Facultad de Ingeniería de Sistemas Computacionales**
> Arquitectura y Organización de Computadoras · Proyecto Final de Semestre

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-purple)](https://github.com/TomSchimansky/CustomTkinter)
[![Crypto](https://img.shields.io/badge/Crypto-SHA--256-green)](https://docs.python.org/3/library/hashlib.html)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

## Descripción del Proyecto

Este simulador interactivo modela con detalle técnico la **secuencia de arranque seguro de un sistema de cómputo moderno**, abarcando:

- La secuencia **POST** completa (`POWER_ON → CPU_RESET_VECTOR → CHIPSET_INIT → DRAM_INIT → FIRMWARE_VERIFICATION → OS_HANDOFF`)
- La **emulación de chipset** (ICH9) con registros de CPU reales (`EIP = 0xFFFF0`, `CS = 0xF000`)
- La **detección y mitigación criptográfica de Rootkits de Firmware** mediante hashes SHA-256 reales
- Un sistema de **auditoría forense** con persistencia de logs en formato JSON estructurado

---

## 📊 Arquitectura del Ciclo de Arranque y Seguridad

Para el desarrollo del backend y las pruebas de control de calidad, el equipo se guiará estrictamente por el siguiente mapa lógico de ejecución (POST, verificación criptográfica SHA-256 de firmas de firmware y mitigación activa de amenazas por Rootkits/Bootkits):

![Diagrama de Flujo del Simulador](data/diagrama_bloques_arranque.png)

---

## 👥 Equipo de Desarrollo

| Rol | Nombre | Responsabilidad |
|---|---|---|
| Líder Técnico | **Orlando Atencio** | Arquitectura, orquestación y configuración global |
| Analista QA | **Josué Contreras** | Diseño de pruebas (`/tests`), control de excepciones y logs |
| Backend — POST & Core | **Meisy Rodríguez** | Lógica del POST y motor de arranque (`core/post_engine.py`) |
| Backend — Hardware | **Allen Rodríguez** | Emulación de CPU y RAM (`core/cpu.py`, `core/ram.py`) |
| Backend — Malware | **Andrée Romero** | Inyección de rootkits y payloads (`core/rootkit.py`) |
| Backend — Cripto | **Jahir Flores** | SHA-256 y Secure Boot (`crypto/`) |
| Frontend — UI | **Rangelino González** | Diseño de interfaces, paleta y layouts (`ui/`) |
| Frontend — Animación | **Alexander Gutiérrez** | Hilos de animación de buses de datos (`ui/bus_animation.py`) |
| Frontend — Consola | **Michael Santimateo** | Consola de auditoría táctica (`ui/audit_console.py`) |

---

## 🗂️ Estructura del Proyecto
simulador-arranque-seguro/
│
├── config/          # Constantes y configuraciones globales
│   └── settings.py  # Rutas, paleta de colores CTk y tick rate de animación
│
├── core/            # Lógica de hardware, CPU, BIOS, POST y Rootkit
│   ├── cpu.py           # Emulación de registros de CPU (EIP, CS, IP)
│   ├── ram.py           # Bancos de memoria y detección de errores
│   ├── chipset.py       # Emulación ICH9, base APIC
│   ├── post_engine.py   # Secuencia POST completa
│   ├── bios.py          # Menú Setup de BIOS simulado
│   ├── rootkit.py       # Inyección de payloads maliciosos
│   └── log_system.py    # Funciones write_event() y flush_session()
│
├── crypto/          # Motor de hashes SHA-256 para Secure Boot
│   ├── hash_engine.py   # Cálculo de SHA-256 sobre bloques de firmware
│   └── secure_boot.py   # Verificación de firmas y bloqueo de arranque
│
├── events/          # Bus de comunicación asíncrona por eventos
│   └── event_bus.py     # Despacho de eventos entre backend y UI
│
├── ui/              # Interfaz gráfica (ventanas, temas y animaciones)
│   ├── main_window.py   # Ventana principal CustomTkinter
│   ├── bus_animation.py # Hilos de animación de buses de datos
│   └── audit_console.py # Consola táctica de auditoría en tiempo real
│
├── data/            # Persistencia local
│   ├── firmware/        # Firmware simulado (limpio e infectado)
│   │   ├── clean_firmware.bin
│   │   └── infected_firmware.bin
│   └── logs/            # Logs de auditoría forense
│       └── boot_log.json
│
├── tests/           # Scripts de pruebas unitarias y de estrés (zona QA)
│   ├── test_post.py
│   ├── test_crypto.py
│   ├── test_rootkit.py
│   └── test_log_system.py
│
├── main.py          # Punto de entrada principal del simulador
├── requirements.txt # Dependencias del proyecto
└── README.md
---

## ⚙️ Requisitos del Sistema

| Requisito | Versión mínima |
|---|---|
| Python | **3.10 o superior** |
| Sistema Operativo | Windows 10 / macOS 12 / Ubuntu 20.04 |
| Espacio en disco | ~50 MB |

> ⚠️ **Importante:** Este proyecto **requiere Python 3.10+** por el uso de `match/case` (structural pattern matching) en la lógica del simulador. Verifica tu versión antes de continuar.

---

## 🚀 Instalación — Guía de Inicio Rápido

Sigue estos pasos **en orden exacto**. Todos los miembros del equipo deben usar el mismo entorno virtual para garantizar la reproducibilidad.

### Paso 1 — Clonar el repositorio

```bash
git clone [https://github.com/](https://github.com/)[org-del-equipo]/simulador-arranque-seguro.git
cd simulador-arranque-seguro

Verificar la versión de Python
python --version
# Salida esperada: Python 3.10.x o superior

Crear el entorno virtual
# En Windows
python -m venv venv

# En macOS / Linux
python3 -m venv venv

Activar el entorno virtual
# En Windows (Command Prompt)
venv\Scripts\activate.bat

# En Windows (PowerShell)
venv\Scripts\Activate.ps1

# En macOS / Linux
source venv/bin/activate

Instalar dependencias
pip install -r requirements.txt

Ejecutar el simulador
python main.py

Variables de Configuración
# config/settings.py (extracto relevante)

# --- Rutas de persistencia ---
LOG_FILE_PATH     = "data/logs/boot_log.json"
FIRMWARE_CLEAN    = "data/firmware/clean_firmware.bin"
FIRMWARE_INFECTED = "data/firmware/infected_firmware.bin"

# --- Parámetros de animación ---
ANIMATION_TICK_MS = 50      # Intervalo de actualización de la GUI (milisegundos)
BUS_SPEED_FACTOR  = 1.0     # Multiplicador de velocidad de animación de buses

# --- Configuración de seguridad ---
SECURE_BOOT_ENABLED = True  # Activar/desactivar verificación SHA-256 al inicio

Ejecutar las Pruebas (Zona QA)
# Ejecutar todos los tests
python -m pytest tests/ -v

# Ejecutar tests por módulo específico
python -m pytest tests/test_crypto.py -v
python -m pytest tests/test_post.py -v
python -m pytest tests/test_rootkit.py -v

# Ejecutar con reporte de cobertura
python -m pytest tests/ --cov=core --cov=crypto --cov-report=term-missing


📋 Formato del Log de Auditoría
{
  "event_id": "EVT-0007",
  "timestamp": "2026-06-06T14:32:05.112Z",
  "boot_stage": "FIRMWARE_VERIFICATION",
  "module": "crypto.secure_boot",
  "severity": "CRITICAL",
  "security_status": "TAMPERED",
  "logical_address": "0xF0000",
  "crypto": {
    "algorithm": "SHA-256",
    "firmware_hash": "deadbeef...ef",
    "signature_valid": false
  },
  "threat_indicators": {
    "rootkit_detected": true,
    "attack_vector": "FIRMWARE_FLASH_INJECT"
  }
}

🌿 Flujo de Trabajo con Git
# Crear una rama para tu tarea utilizando el prefijo corto acordado
git checkout -b feat/nombre-de-tu-tarea

# Hacer commit de tu trabajo
git add .
git commit -m "feat(modulo): descripción corta del cambio"

# Subir tu rama
git push origin feat/nombre-de-tu-tarea

# Abrir un Pull Request hacia la rama 'develop'
# NUNCA hacer push directo a 'main' o 'develop' sin revisión

📄 Licencia
Este proyecto es de uso académico exclusivo para la Universidad Tecnológica de Panamá.
Desarrollado para la materia de Arquitectura y Organización de Computadoras.

Equipo de Desarrollo · UTP · 2026
