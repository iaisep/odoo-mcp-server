#!/usr/bin/env python3
"""
Script de prueba para verificar el servidor MCP con health check HTTP
"""

import requests
import time
import json

def test_health_endpoint():
    """Probar el endpoint de health check"""
    url = "http://localhost:8000/health"
    
    try:
        print(f"🔍 Probando health check en {url}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check exitoso:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Health check falló con código: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está ejecutándose?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root_endpoint():
    """Probar el endpoint raíz"""
    url = "http://localhost:8000/"
    
    try:
        print(f"\n🔍 Probando endpoint raíz en {url}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint raíz exitoso:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Endpoint raíz falló con código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando pruebas del servidor MCP...")
    print("📝 Asegúrate de que el servidor esté ejecutándose con: python main.py")
    print("   (con PORT=8000)")
    print()
    
    # Dar tiempo para que el usuario inicie el servidor
    print("⏳ Esperando 3 segundos...")
    time.sleep(3)
    
    # Ejecutar pruebas
    health_ok = test_health_endpoint()
    root_ok = test_root_endpoint()
    
    print(f"\n📊 Resultados:")
    print(f"   Health check: {'✅' if health_ok else '❌'}")
    print(f"   Root endpoint: {'✅' if root_ok else '❌'}")
    
    if health_ok and root_ok:
        print(f"\n🎉 ¡Todas las pruebas exitosas! El servidor está listo para Coolify.")
    else:
        print(f"\n🚨 Algunas pruebas fallaron. Revisa la configuración del servidor.")
