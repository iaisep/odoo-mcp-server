#!/usr/bin/env python3
"""
Test script para verificar que la corrección de serialización datetime funciona
"""
import requests
import json

def test_get_leads():
    """Probar el endpoint get_leads que estaba causando el error datetime"""
    print("🧪 Probando corrección de serialización datetime...")
    
    url = "http://localhost:8001/mcp/get_leads"
    payload = {
        "limit": 3
    }
    
    try:
        print(f"📡 Enviando POST a {url}")
        print(f"📄 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ¡Success! La serialización datetime funciona correctamente")
            print(f"📈 Leads encontrados: {data.get('count', 'N/A')}")
            print(f"💬 Mensaje: {data.get('message', 'N/A')}")
            
            # Verificar que hay datos y que las fechas están como strings
            if data.get('success') and data.get('data'):
                leads = data['data']
                if leads:
                    first_lead = leads[0]
                    print(f"🔍 Primer lead ID: {first_lead.get('id')}")
                    
                    # Verificar campos de fecha
                    create_date = first_lead.get('create_date')
                    write_date = first_lead.get('write_date')
                    
                    print(f"📅 create_date: {create_date} (tipo: {type(create_date).__name__})")
                    print(f"📅 write_date: {write_date} (tipo: {type(write_date).__name__})")
                    
                    if isinstance(create_date, str) and isinstance(write_date, str):
                        print("🎉 ¡PERFECTO! Las fechas están correctamente serializadas como strings")
                        return True
                    else:
                        print("⚠️ Las fechas no están como strings - puede haber un problema")
                        return False
            else:
                print("⚠️ No hay datos en la respuesta")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose en localhost:8001?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_health_check():
    """Probar el health check"""
    print("\n🔍 Probando health check...")
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data.get('status')}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de corrección datetime...")
    
    # Test health check primero
    health_ok = test_health_check()
    
    if health_ok:
        # Test del endpoint que estaba fallando
        leads_ok = test_get_leads()
        
        if leads_ok:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
            print("✅ El error de serialización datetime ha sido corregido")
        else:
            print("\n❌ Las pruebas fallaron")
    else:
        print("\n❌ Servidor no disponible")
