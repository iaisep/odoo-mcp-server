#!/usr/bin/env python3
"""
Test completo del servidor MCP en Coolify
URL: https://dev2.odoo.universidadisep.com/
"""

import requests
import json
import time
from datetime import datetime

def print_header(title):
    """Imprimir encabezado de sección"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def test_coolify_health():
    """Probar health check en Coolify"""
    url = "https://dev2.odoo.universidadisep.com/health"
    
    print(f"🔍 Probando health check: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"🕒 Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Health Check EXITOSO:")
                print(json.dumps(data, indent=2))
                
                # Validar campos esperados
                expected_fields = ['status', 'service', 'odoo_connected', 'anthropic_available']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Campos faltantes: {missing_fields}")
                else:
                    print(f"✅ Todos los campos esperados presentes")
                    
                return True, data
                
            except json.JSONDecodeError:
                print(f"❌ Respuesta no es JSON válido:")
                print(response.text[:200])
                return False, None
                
        else:
            print(f"❌ Health check falló")
            print(f"Response: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        return False, None
    except requests.exceptions.Timeout:
        print(f"❌ Timeout - el servidor no responde en 10 segundos")
        return False, None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False, None

def test_coolify_root():
    """Probar endpoint raíz en Coolify"""
    url = "https://dev2.odoo.universidadisep.com/"
    
    print(f"\n🔍 Probando endpoint raíz: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"🕒 Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Root endpoint EXITOSO:")
                print(json.dumps(data, indent=2))
                return True, data
                
            except json.JSONDecodeError:
                print(f"❌ Respuesta no es JSON válido:")
                print(response.text[:200])
                return False, None
                
        else:
            print(f"❌ Root endpoint falló")
            print(f"Response: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_connectivity():
    """Probar conectividad básica"""
    url = "https://dev2.odoo.universidadisep.com/"
    
    print(f"🌐 Probando conectividad básica...")
    
    try:
        # Solo hacer HEAD request para ver si el servidor responde
        response = requests.head(url, timeout=5)
        print(f"📡 Servidor responde: Status {response.status_code}")
        
        # Headers útiles
        useful_headers = ['server', 'content-type', 'x-powered-by', 'content-length']
        print("📋 Headers relevantes:")
        for header in useful_headers:
            if header in response.headers:
                print(f"   {header}: {response.headers[header]}")
                
        return True
        
    except Exception as e:
        print(f"❌ No hay conectividad: {e}")
        return False

def run_full_test():
    """Ejecutar test completo"""
    
    print_header("TEST SERVIDOR COOLIFY")
    print(f"🎯 URL: https://dev2.odoo.universidadisep.com/")
    print(f"🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'connectivity': False,
        'health': False,
        'root': False,
        'health_data': None
    }
    
    # Test 1: Conectividad básica
    print_header("TEST 1: CONECTIVIDAD")
    results['connectivity'] = test_connectivity()
    
    # Test 2: Health Check
    print_header("TEST 2: HEALTH CHECK")
    health_ok, health_data = test_coolify_health()
    results['health'] = health_ok
    results['health_data'] = health_data
    
    # Test 3: Root Endpoint
    print_header("TEST 3: ROOT ENDPOINT") 
    root_ok, root_data = test_coolify_root()
    results['root'] = root_ok
    
    # Resumen final
    print_header("RESUMEN DE RESULTADOS")
    
    total_tests = 3
    passed_tests = sum([results['connectivity'], results['health'], results['root']])
    
    print(f"📊 Tests ejecutados: {total_tests}")
    print(f"✅ Tests exitosos: {passed_tests}")
    print(f"❌ Tests fallidos: {total_tests - passed_tests}")
    print(f"📈 Porcentaje éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n🔍 Detalles:")
    print(f"   Conectividad: {'✅' if results['connectivity'] else '❌'}")
    print(f"   Health Check: {'✅' if results['health'] else '❌'}")
    print(f"   Root Endpoint: {'✅' if results['root'] else '❌'}")
    
    # Análisis específico
    if results['health'] and results['health_data']:
        health_data = results['health_data']
        print(f"\n🔍 Análisis Health Check:")
        print(f"   Servidor: {health_data.get('service', 'N/A')}")
        print(f"   Estado: {health_data.get('status', 'N/A')}")
        print(f"   Odoo conectado: {'✅' if health_data.get('odoo_connected') else '❌'}")
        print(f"   Anthropic disponible: {'✅' if health_data.get('anthropic_available') else '❌'}")
    
    # Recomendaciones
    print_header("RECOMENDACIONES")
    
    if passed_tests == total_tests:
        print("🎉 ¡Excelente! El servidor está funcionando perfectamente en Coolify.")
        print("✅ Listo para integrar con n8n o cualquier cliente MCP.")
    elif results['connectivity'] and not results['health']:
        print("🔧 El servidor responde pero hay problemas con la aplicación.")
        print("📝 Revisar logs de Coolify para errores de la aplicación.")
    elif not results['connectivity']:
        print("🚨 Problema de conectividad o el servidor no está ejecutándose.")
        print("📝 Verificar el deployment en Coolify.")
    else:
        print("⚠️  Problemas parciales detectados.")
        print("📝 Revisar configuración y logs en Coolify.")
        
    return results

if __name__ == "__main__":
    try:
        results = run_full_test()
        
        # Guardar resultados si es exitoso
        if results['health']:
            print(f"\n💾 Guardando resultados exitosos...")
            with open('coolify_test_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"📁 Resultados guardados en: coolify_test_results.json")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrumpido por usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
