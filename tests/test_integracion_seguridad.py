import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.post_engine import PostEngine

# 1. Creamos la instancia del motor (que ahora ya incluye tu SecureBoot)
motor = PostEngine()

print("--- INICIANDO PRUEBA DE INTEGRACIÓN ---")

try:
    # 2. Ejecutamos la etapa de Secure Boot manualmente para probar
    print("Ejecutando verificación...")
    motor._run_secure_boot_verify() 
    print("Resultado: ¡Arranque exitoso!")

except ValueError as e:
    # 3. Capturamos el error si el Secure Boot bloquea el sistema
    print(f"Resultado: El sistema se detuvo correctamente: {e}")

print("--- FIN DE LA PRUEBA ---")