#!/usr/bin/env python3
"""
Script de prueba de conexiones para el servidor MCP de Odoo
Prueba las conexiones antes del deployment en Coolify
"""

import os
import sys
import asyncio
import requests
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

def test_odoo_connection():
    """Probar conexión directa a Odoo"""
    print("🔍 Probando conexión a Odoo...")
    
    odoo_url = os.getenv('ODOO_URL')
    odoo_db = os.getenv('ODOO_DB') 
    odoo_username = os.getenv('ODOO_USERNAME')
    odoo_password = os.getenv('ODOO_PASSWORD')
    
    print(f"   URL: {odoo_url}")
    print(f"   DB: {odoo_db}")
    print(f"   Usuario: {odoo_username}")
    
    try:
        # Probar endpoint básico de Odoo
        response = requests.get(f"{odoo_url}/web/database/selector", timeout=10)
        if response.status_code == 200:
            print("✅ Odoo responde correctamente")
            return True
        else:
            print(f"❌ Odoo responde con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando a Odoo: {e}")
        return False

def test_anthropic_connection():
    """Probar conexión a Anthropic (si hay API key)"""
    print("\n🤖 Probando conexión a Anthropic...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  API key de Anthropic no configurada (opcional)")
        return True
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Cliente Anthropic inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error con Anthropic: {e}")
        return False

def test_local_server():
    """Probar servidor local si está corriendo"""
    print("\n🖥️  Probando servidor local...")
    
    try:
        response = requests.get("http://localhost:8083/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Servidor local funcionando:")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Odoo conectado: {data.get('odoo_connected')}")
            return True
        else:
            print(f"❌ Servidor local responde con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Servidor local no está corriendo")
        return False
    except Exception as e:
        print(f"❌ Error probando servidor local: {e}")
        return False

def test_coolify_url(coolify_url):
    """Probar URL de Coolify si se proporciona"""
    if not coolify_url:
        return True
        
    print(f"\n🌐 Probando URL de Coolify: {coolify_url}")
    
    try:
        # Probar health check
        health_url = f"{coolify_url.rstrip('/')}/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Coolify deployment funcionando:")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Odoo conectado: {data.get('odoo_connected')}")
            print(f"   Anthropic disponible: {data.get('anthropic_available')}")
            return True
        else:
            print(f"❌ Coolify responde con código {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar a {coolify_url}")
        return False
    except Exception as e:
        print(f"❌ Error probando Coolify: {e}")
        return False

def main():
    """Ejecutar todas las pruebas de conexión"""
    print("🚀 Iniciando pruebas de conexión para el servidor MCP de Odoo\n")
    
    results = []
    
    # Test 1: Odoo
    results.append(("Odoo", test_odoo_connection()))
    
    # Test 2: Anthropic  
    results.append(("Anthropic", test_anthropic_connection()))
    
    # Test 3: Servidor local
    results.append(("Servidor Local", test_local_server()))
    
    # Test 4: Coolify (si se proporciona URL)
    coolify_url = input("\n🌐 ¿Cuál es tu URL de Coolify? (Enter para saltar): ").strip()
    if coolify_url:
        results.append(("Coolify", test_coolify_url(coolify_url)))
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS DE CONEXIÓN")
    print("="*50)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:15} : {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\nResultado: {passed_tests}/{total_tests} pruebas exitosas")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡Todas las conexiones funcionan correctamente!")
        print("   Tu servidor está listo para deployment en Coolify.")
    else:
        print("\n⚠️  Algunas conexiones fallaron.")
        print("   Revisa la configuración antes del deployment.")

if __name__ == "__main__":
    main()
