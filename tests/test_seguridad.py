import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import SecurityStatus
from core.secure_boot import SecureBoot

sb = SecureBoot()

# Prueba 1: Hash limpio
print(f"¿Es seguro? {sb.verificar_contra_dbx('HASH_WINDOWS_BOOT')}") 

# Prueba 2: Hash malicioso (debe bloquearse)
print(f"¿Es seguro? {sb.verificar_contra_dbx('HASH_MALWARE_ROOTKIT_001')}")