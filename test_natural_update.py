#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de actualizaciones masivas con lenguaje natural
"""

import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8001"

def test_natural_update():
    """Prueba la funcionalidad de actualización natural"""
    
    # Ejemplos de instrucciones para probar
    test_cases = [
        {
            "name": "Llenar emails vacíos con patrón Universidad",
            "instruction": "Llenar el campo email_from con 'info@universidad.edu.co' para todos los leads que tengan 'Universidad' en el nombre y email vacío",
            "model": "crm.lead",
            "dry_run": True,
            "max_records": 10
        },
        {
            "name": "Actualizar teléfonos para leads de Bogotá",
            "instruction": "Actualizar el campo phone con '+57-1-555-0000' para todos los leads de Bogotá que no tengan teléfono",
            "model": "crm.lead", 
            "dry_run": True,
            "max_records": 5
        },
        {
            "name": "Cambiar estado de leads recientes",
            "instruction": "Cambiar el stage_id a 2 para todos los leads creados en los últimos 7 días",
            "model": "crm.lead",
            "dry_run": True,
            "max_records": 20
        }
    ]
    
    print("🚀 Probando funcionalidad de actualizaciones masivas con lenguaje natural\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}: {test_case['name']}")
        print(f"   Instrucción: {test_case['instruction']}")
        print(f"   Modelo: {test_case['model']}")
        print(f"   Dry Run: {test_case['dry_run']}")
        print(f"   Máx. Registros: {test_case['max_records']}\n")
        
        try:
            response = requests.post(
                f"{BASE_URL}/mcp/execute_natural_update",
                json=test_case,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ Respuesta exitosa:")
                print(f"   Plan: {result.get('plan', {}).get('description', 'No disponible')}")
                print(f"   Registros encontrados: {result.get('found_records', 0)}")
                print(f"   Mensaje: {result.get('message', 'Sin mensaje')}")
                
                if 'preview_current_data' in result and result['preview_current_data']:
                    print("   Vista previa de datos actuales:")
                    for record in result['preview_current_data'][:2]:  # Solo mostrar 2 registros
                        print(f"     - ID {record.get('id')}: {record.get('name', 'Sin nombre')}")
                
                if 'planned_updates' in result:
                    print(f"   Updates planeados: {result['planned_updates']}")
                    
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        print("-" * 80 + "\n")

def test_server_connection():
    """Verifica que el servidor esté funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor conectado correctamente")
            return True
        else:
            print(f"❌ Servidor responde con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se pudo conectar al servidor: {e}")
        print(f"   Asegúrate de que el servidor esté ejecutándose en {BASE_URL}")
        return False

if __name__ == "__main__":
    print("🔍 Probando Actualizaciones Masivas con Lenguaje Natural")
    print("=" * 60)
    print(f"Servidor: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    # Verificar conexión al servidor
    if test_server_connection():
        print()
        test_natural_update()
    
    print("🏁 Pruebas completadas")
