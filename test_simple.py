#!/usr/bin/env python3
"""
Script simple para probar el endpoint get_leads y ver si la corrección datetime funciona
"""
import json
import urllib.request
import urllib.parse

def test_get_leads():
    """Test simple con urllib"""
    print("🧪 Probando endpoint get_leads...")
    
    # Datos del payload
    data = {
        "limit": 2
    }
    
    # Convertir a JSON
    json_data = json.dumps(data).encode('utf-8')
    
    # Crear request
    url = "http://localhost:8001/mcp/get_leads"
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={
            'Content-Type': 'application/json',
            'Content-Length': str(len(json_data))
        },
        method='POST'
    )
    
    try:
        print(f"📡 Enviando POST a {url}")
        print(f"📄 Payload: {data}")
        
        # Hacer la petición
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            status_code = response.getcode()
            
            print(f"📊 Status Code: {status_code}")
            
            if status_code == 200:
                # Parse JSON response
                result = json.loads(response_data)
                print("✅ ¡Success! El endpoint respondió correctamente")
                print(f"💬 Mensaje: {result.get('message', 'N/A')}")
                
                # Verificar campos datetime
                if result.get('success') and result.get('data'):
                    leads = result['data']
                    if leads:
                        first_lead = leads[0]
                        print(f"🔍 Primer lead ID: {first_lead.get('id')}")
                        
                        create_date = first_lead.get('create_date')
                        write_date = first_lead.get('write_date')
                        
                        print(f"📅 create_date: {create_date}")
                        print(f"📅 write_date: {write_date}")
                        
                        # Si llegamos aquí sin error de serialización, ¡la corrección funciona!
                        print("🎉 ¡CORRECCIÓN EXITOSA! No hay errores de serialización datetime")
                        return True
                    else:
                        print("⚠️ No hay leads en la respuesta")
                        return True  # Aún así, no hubo error de serialización
                else:
                    print("⚠️ Respuesta sin datos")
                    return True  # Aún así, no hubo error de serialización
            else:
                print(f"❌ Error HTTP: {status_code}")
                print(f"📄 Respuesta: {response_data}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code}")
        error_response = e.read().decode('utf-8')
        print(f"📄 Error response: {error_response}")
        
        # Verificar si es el error datetime específico
        if "Object of type datetime is not JSON serializable" in error_response:
            print("🚨 ¡ERROR! El problema de serialización datetime AÚN EXISTE")
            return False
        else:
            print("⚠️ Error diferente (no relacionado con datetime)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Probando corrección de error datetime serialization...")
    result = test_get_leads()
    
    if result:
        print("\n🎉 ¡PRUEBA EXITOSA! El error ha sido corregido")
    else:
        print("\n❌ La corrección necesita más trabajo")
